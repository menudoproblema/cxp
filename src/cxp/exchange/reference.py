"""Recursos de referencia propios, sin descubrimiento ni catálogos globales."""

from __future__ import annotations

import json
from importlib.resources import files
from typing import Any

from jsonschema import Draft202012Validator
from referencing import Registry

from cxp.exchange.documents import Document, _copy_json, load_document, pointer_token
from cxp.exchange.errors import InvalidDocumentError, unsupported
from cxp.exchange.normalization import timestamp
from cxp.validation import ValidationIssue

__all__ = (
    "REFERENCE_CATALOGS",
    "legacy_idempotency",
    "load_reference_catalog",
    "operation_schema",
    "validate_operation_payload",
)

REFERENCE_CATALOGS = (
    "software-service",
    "physical-printing",
    "document-processing",
    "job-submission",
    "finishing",
)


def load_reference_catalog(name: str) -> Document:
    if name not in REFERENCE_CATALOGS:
        raise ValueError(f"Unknown reference catalog: {name!r}")
    return load_document(
        files("cxp.exchange").joinpath(f"catalogs/{name}.json").read_bytes(),
        expected_type="cxp.catalog",
    )


def legacy_idempotency(idempotent: bool) -> dict[str, str]:
    """False no permite recuperar si el emisor omitió la garantía heredada."""
    if type(idempotent) is not bool:
        raise TypeError("Expected a legacy boolean guarantee")
    return {"state": "guaranteed" if idempotent else "unknown"}


def operation_schema(contract_type: str) -> dict[str, Any]:
    schema = json.loads(
        files("cxp.exchange").joinpath("schemas/operations-v1.json").read_bytes()
    )
    contracts = {
        f"org.cxp:{name}:1": definition for name, definition in schema["$defs"].items()
    }
    if contract_type not in contracts:
        raise unsupported("unknown_operation_contract", "", "Unknown payload contract")
    return {"$schema": schema["$schema"], **contracts[contract_type]}


def validate_operation_payload(
    contract_type: str, payload: dict[str, Any]
) -> dict[str, Any]:
    """Validamos y copiamos datos; no ejecutamos ni confirmamos trabajos."""
    schema = operation_schema(contract_type)
    content = _copy_json(payload)
    issues = [
        ValidationIssue(
            "schema_violation",
            "/" + "/".join(pointer_token(item) for item in error.absolute_path),
            error.message[:512],
        )
        for error in Draft202012Validator(schema, registry=Registry()).iter_errors(
            content
        )
    ]
    if issues:
        raise InvalidDocumentError(
            sorted(issues, key=lambda item: (item.path, item.message))
        )
    if "observed_at" in content:
        content["observed_at"] = timestamp(content["observed_at"], "/observed_at")
    return content
