"""Entrada JSON acotada y documentos inmutables identificados por contenido."""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from functools import lru_cache
from importlib.resources import files
from typing import Any

try:
    import rfc8785
    from jsonschema import Draft202012Validator
    from referencing import Registry
except ModuleNotFoundError as error:
    # Solo aclaramos dependencias opcionales ausentes, no imports rotos internos.
    if error.name not in {"rfc8785", "jsonschema", "referencing"}:
        raise
    raise ModuleNotFoundError(
        "CXP document exchange requires the optional dependencies. "
        "Install them with: pip install 'cxp[exchange]'",
        name=error.name,
    ) from error

from cxp.exchange.errors import InvalidDocumentError, invalid, unsupported
from cxp.exchange.normalization import normalize_payload, requirement_shape_issues
from cxp.validation import ValidationIssue

__all__ = ("Document", "document_schema", "load_document")

type JsonObject = dict[str, Any]

DOCUMENT_TYPES = (
    "cxp.catalog",
    "cxp.snapshot",
    "cxp.requirements",
    "cxp.context",
    "cxp.evaluation",
    "cxp.exchange_request",
    "cxp.exchange_response",
)
MAX_BYTES = 1024 * 1024
MAX_DEPTH = 32
MAX_NODES = 20_000
MAX_STRING = 16_384
MAX_INTEGER = 9_007_199_254_740_991


class _Pairs(list[tuple[str, object]]):
    """Conservamos las claves repetidas hasta conocer su ruta completa."""


class _Number(str):
    """Conservamos el token numérico antes de cualquier redondeo de JSON."""


def pointer_token(value: str | int) -> str:
    return str(value).replace("~", "~0").replace("/", "~1")


def _copy_json(value: object) -> Any:
    remaining = MAX_NODES
    remaining_bytes = MAX_BYTES

    def visit(node: Any, path: str, depth: int) -> Any:
        nonlocal remaining, remaining_bytes
        remaining -= 1
        if remaining < 0 or depth > MAX_DEPTH:
            raise invalid("resource_limit", path, "Document exceeds structural limits")
        if isinstance(node, _Number):
            try:
                number = Decimal(node)
            except (ValueError, InvalidOperation, OverflowError) as error:
                raise invalid("invalid_number", path, "Invalid JSON number") from error
            if not number.is_finite():
                raise invalid("invalid_number", path, "JSON numbers must be finite")
            # Clasificamos enteros antes de perder precisión al pasar por float.
            if number == number.to_integral_value():
                if number.copy_abs() > MAX_INTEGER:
                    raise invalid(
                        "unsafe_integer", path, "Integer exceeds interoperable range"
                    )
                node = int(number)
            else:
                binary = float(node)
                if not math.isfinite(binary):
                    raise invalid("invalid_number", path, "JSON numbers must be finite")
                if number != Decimal(str(binary)):
                    raise invalid(
                        "lossy_number", path, "Use a decimal string for this precision"
                    )
                node = binary
        if isinstance(node, str):
            if len(node) > MAX_STRING:
                raise invalid("resource_limit", path, "String exceeds document limit")
            try:
                remaining_bytes -= len(node.encode("utf-8"))
            except UnicodeError as error:
                raise invalid(
                    "invalid_unicode", path, "Invalid Unicode string"
                ) from error
            if remaining_bytes < 0:
                raise invalid("resource_limit", path, "Document exceeds byte limit")
            return node
        if node is None or isinstance(node, bool):
            return node
        if isinstance(node, (int, float)):
            if isinstance(node, float):
                if not math.isfinite(node):
                    raise invalid("invalid_number", path, "JSON numbers must be finite")
                if node.is_integer():
                    node = int(node)
            if isinstance(node, int) and abs(node) > MAX_INTEGER:
                raise invalid(
                    "unsafe_integer", path, "Integer exceeds interoperable range"
                )
            return node
        if isinstance(node, (dict, _Pairs)):
            result: JsonObject = {}
            pairs = node.items() if isinstance(node, dict) else node
            for key, item in pairs:
                if not isinstance(key, str):
                    raise invalid("invalid_key", path, "JSON keys must be strings")
                child_path = f"{path}/{pointer_token(key)}"
                if key in result:
                    raise invalid("duplicate_key", child_path, "Duplicate JSON key")
                visit(key, child_path, depth + 1)
                result[key] = visit(item, child_path, depth + 1)
            return result
        if isinstance(node, list):
            return [
                visit(item, f"{path}/{index}", depth + 1)
                for index, item in enumerate(node)
            ]
        raise invalid("invalid_json_value", path, "Value is not a JSON type")

    return visit(value, "", 0)


@lru_cache(maxsize=1)
def _schema() -> JsonObject:
    resource = files("cxp.exchange").joinpath("schemas/exchange-v1.json")
    return json.loads(resource.read_text(encoding="utf-8"))


def document_schema() -> JsonObject:
    """Devolvemos una copia del contrato estructural distribuido con CXP."""
    return json.loads(json.dumps(_schema()))


@lru_cache(maxsize=7)
def _validator(document_type: str) -> Draft202012Validator:
    schema = _schema()
    definition = next(
        item
        for item in schema["oneOf"]
        if item["properties"]["document_type"]["const"] == document_type
    )
    return Draft202012Validator(
        {**definition, "$defs": schema["$defs"]}, registry=Registry()
    )


def _validate(value: object, expected_type: str) -> bytes:
    content = _copy_json(value)
    if not isinstance(content, dict):
        raise invalid("invalid_document", "", "Document must be a JSON object")
    document_type = content.get("document_type")
    if not isinstance(document_type, str):
        raise invalid(
            "invalid_document_type", "/document_type", "Document type is required"
        )
    if document_type not in DOCUMENT_TYPES or document_type != expected_type:
        raise unsupported(
            "unsupported_document_type", "/document_type", "Unexpected document family"
        )
    version = content.get("spec_version")
    if type(version) is not int:
        raise invalid(
            "invalid_version", "/spec_version", "Document version must be an integer"
        )
    if version != 1:
        raise unsupported(
            "unsupported_version", "/spec_version", "Unsupported document version"
        )
    # Damos diagnósticos precisos sin retirar las restricciones del JSON Schema.
    issues = requirement_shape_issues(content)
    if issues:
        raise InvalidDocumentError(issues)
    for error in _validator(document_type).iter_errors(content):
        path = "/" + "/".join(pointer_token(token) for token in error.absolute_path)
        issues.append(
            ValidationIssue("schema_violation", path.rstrip("/"), error.message[:512])
        )
        if len(issues) >= 100:
            break
    if issues:
        raise InvalidDocumentError(
            sorted(issues, key=lambda issue: (issue.path, issue.code, issue.message))
        )
    normalize_payload(content)
    # Los valores por defecto también cuentan en el documento que exportamos.
    content = _copy_json(content)
    # La normalización no puede introducir duplicados ni romper el esquema.
    for error in _validator(document_type).iter_errors(content):
        path = "/" + "/".join(pointer_token(token) for token in error.absolute_path)
        raise invalid("schema_violation", path.rstrip("/"), error.message[:512])
    encoded = rfc8785.dumps(content)
    if len(encoded) > MAX_BYTES:
        raise invalid("resource_limit", "", "Document exceeds byte limit")
    return encoded


@dataclass(frozen=True, slots=True, init=False)
class Document:
    """Conservamos solo bytes propios; cada acceso a datos devuelve una copia."""

    _canonical: bytes

    def __init__(self, content: JsonObject, *, expected_type: str) -> None:
        object.__setattr__(self, "_canonical", _validate(content, expected_type))

    @property
    def document_type(self) -> str:
        return self.as_dict()["document_type"]

    @property
    def spec_version(self) -> int:
        return self.as_dict()["spec_version"]

    @property
    def payload(self) -> JsonObject:
        return self.as_dict()["payload"]

    @property
    def sha256(self) -> str:
        return hashlib.sha256(self._canonical).hexdigest()

    def as_dict(self) -> JsonObject:
        return json.loads(self._canonical)

    def to_bytes(self) -> bytes:
        return self._canonical

    def require_type(self, expected_type: str) -> None:
        if self.document_type != expected_type:
            raise unsupported(
                "unsupported_document_type",
                "/document_type",
                "Unexpected document family",
            )


def load_document(data: bytes | str, *, expected_type: str) -> Document:
    try:
        encoded = data.encode("utf-8") if isinstance(data, str) else data
    except UnicodeError as error:
        raise invalid("invalid_unicode", "", "Document must be UTF-8") from error
    if not isinstance(encoded, bytes):
        raise invalid("invalid_document", "", "Expected bytes or a UTF-8 string")
    if len(encoded) > MAX_BYTES:
        raise invalid("resource_limit", "", "Document exceeds byte limit")
    try:
        content = json.loads(
            encoded.decode("utf-8"),
            object_pairs_hook=_Pairs,
            parse_int=_Number,
            parse_float=_Number,
            parse_constant=_Number,
        )
    except (ValueError, UnicodeError, RecursionError) as error:
        raise invalid("invalid_json", "", "Invalid UTF-8 JSON document") from error
    return Document(content, expected_type=expected_type)
