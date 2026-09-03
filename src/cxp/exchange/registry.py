"""Resolución local y validación semántica contra catálogos inmutables."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from decimal import Decimal
from fractions import Fraction
from typing import Any

from cxp.exchange.documents import Document, JsonObject, pointer_token
from cxp.exchange.errors import InvalidDocumentError, invalid
from cxp.exchange.quantities import Quantity, normalize_decimal
from cxp.validation import ValidationIssue

__all__ = ("CatalogStore", "catalog_reference")

type Comparable = str | bool | int | Fraction | frozenset[str] | None


def catalog_reference(catalog: Document) -> dict[str, str]:
    catalog.require_type("cxp.catalog")
    return {**catalog.payload["identity"], "sha256": catalog.sha256}


def property_value(
    value: Any, definition: JsonObject, path: str, *, allow_null: bool = True
) -> Comparable:
    kind = definition["kind"]
    if value is None:
        if allow_null and definition["nullable"]:
            return None
        raise invalid("null_not_allowed", path, "Property does not allow null here")
    if kind == "string" and isinstance(value, str):
        return value
    if kind == "boolean" and type(value) is bool:
        return value
    if kind == "integer" and type(value) is int:
        return value
    if kind == "string_set" and isinstance(value, list):
        if all(isinstance(item, str) for item in value) and len(set(value)) == len(
            value
        ):
            return frozenset(value)
    if kind == "decimal" and isinstance(value, str):
        return Fraction(Decimal(normalize_decimal(value, path=path)))
    if kind == "quantity" and isinstance(value, dict):
        quantity = Quantity(value["value"], value["unit"])
        if quantity.dimension != definition["dimension"]:
            raise invalid(
                "dimension_mismatch", path, "Quantity has the wrong dimension"
            )
        return quantity.exact_value
    raise invalid("property_type_mismatch", path, f"Expected property kind {kind!r}")


def _numeric(value: Any, definition: JsonObject, path: str) -> int | Fraction:
    result = property_value(value, definition, path, allow_null=False)
    if isinstance(result, bool) or not isinstance(result, (int, Fraction)):
        raise invalid("invalid_range", path, "Range values must be numeric")
    return result


def validate_leaf(node: JsonObject, capability: JsonObject, path: str) -> None:
    operations = {item["name"] for item in capability["operations"]}
    for index, name in enumerate(node["operations"]):
        if name not in operations:
            raise invalid(
                "unknown_operation",
                f"{path}/operations/{index}",
                "Required operation is absent from the catalog",
            )
    operator = node["operator"]
    if operator == "support":
        return
    name = node["path"].removeprefix("/properties/")
    definition = capability["properties"].get(name)
    if definition is None:
        raise invalid(
            "unknown_property", f"{path}/path", "Property is absent from catalog"
        )
    if operator == "contains_all":
        if definition["kind"] != "string_set":
            raise invalid(
                "invalid_operator", path, "contains_all requires a string set"
            )
    elif operator == "equals":
        property_value(node["value"], definition, f"{path}/value")
    elif operator == "one_of":
        for index, value in enumerate(node["values"]):
            property_value(value, definition, f"{path}/values/{index}")
    elif operator == "range":
        if definition["kind"] not in ("integer", "decimal", "quantity"):
            raise invalid("invalid_operator", path, "range requires a numeric property")
        numbers = {
            key: _numeric(node[key], definition, f"{path}/{key}")
            for key in ("minimum", "maximum", "step", "origin")
            if key in node
        }
        if "minimum" in numbers and "maximum" in numbers:
            minimum, maximum = numbers["minimum"], numbers["maximum"]
            if minimum > maximum or (
                minimum == maximum
                and not (node["minimum_inclusive"] and node["maximum_inclusive"])
            ):
                raise invalid("invalid_range", path, "Range is empty or inverted")
        if "step" in numbers and numbers["step"] <= 0:
            raise invalid("invalid_step", f"{path}/step", "Step must be positive")


@dataclass(frozen=True, slots=True, init=False)
class CatalogStore:
    """Un registro fijado: añadir catálogos requiere construir otro registro."""

    _catalogs: tuple[Document, ...]

    def __init__(self, catalogs: Iterable[Document] = ()) -> None:
        documents: list[Document] = []
        seen: set[tuple[str, str, str]] = set()
        for catalog in catalogs:
            if len(documents) >= 1000:
                raise invalid("resource_limit", "", "Too many catalogs")
            catalog.require_type("cxp.catalog")
            identity = catalog.payload["identity"]
            key = (identity["namespace"], identity["name"], identity["version"])
            if key in seen:
                raise invalid(
                    "duplicate_catalog", "", "Duplicate catalog identity/version"
                )
            seen.add(key)
            documents.append(catalog)
        object.__setattr__(self, "_catalogs", tuple(documents))

    def resolve(self, reference: dict[str, str]) -> Document:
        if set(reference) != {"namespace", "name", "version", "sha256"} or not all(
            isinstance(value, str) for value in reference.values()
        ):
            raise invalid(
                "invalid_reference", "/payload/catalog", "Invalid catalog reference"
            )
        for catalog in self._catalogs:
            identity = catalog.payload["identity"]
            if all(reference[key] == identity[key] for key in identity):
                if reference["sha256"] != catalog.sha256:
                    raise invalid(
                        "catalog_hash_mismatch",
                        "/payload/catalog/sha256",
                        "Catalog reference does not match its content",
                    )
                return catalog
        raise invalid(
            "unresolved_catalog", "/payload/catalog", "Catalog is not registered"
        )

    def validate_snapshot(self, snapshot: Document) -> Document:
        snapshot.require_type("cxp.snapshot")
        payload = snapshot.payload
        catalog = self.resolve(payload["catalog"])
        definitions = {item["name"]: item for item in catalog.payload["capabilities"]}
        issues: list[ValidationIssue] = []
        for index, capability in enumerate(payload["capabilities"]):
            path = f"/payload/capabilities/{index}"
            definition = definitions.get(capability["name"])
            if definition is None:
                issues.extend(
                    invalid(
                        "unknown_capability",
                        f"{path}/name",
                        "Capability is absent from catalog",
                    ).issues
                )
                continue
            for key, value in capability["properties"].items():
                property_path = f"{path}/properties/{pointer_token(key)}"
                property_definition = definition["properties"].get(key)
                if property_definition is None:
                    issues.extend(
                        invalid(
                            "unknown_property",
                            property_path,
                            "Property is absent from catalog",
                        ).issues
                    )
                    continue
                try:
                    property_value(value, property_definition, property_path)
                except InvalidDocumentError as error:
                    issues.extend(error.issues)
            operations = {item["name"]: item for item in definition["operations"]}
            for offset, binding in enumerate(capability["operations"]):
                binding_path = f"{path}/operations/{offset}"
                operation = operations.get(binding["name"])
                if operation is None:
                    issues.extend(
                        invalid(
                            "unknown_operation",
                            binding_path,
                            "Operation is absent from catalog",
                        ).issues
                    )
                elif binding["result_type"] != operation["result_type"]:
                    issues.extend(
                        invalid(
                            "conflicting_operation_result",
                            f"{binding_path}/result_type",
                            "Binding result contradicts catalog",
                        ).issues
                    )
        if issues:
            raise InvalidDocumentError(
                sorted(issues, key=lambda issue: (issue.path, issue.code))
            )
        return catalog

    def validate_requirements(self, requirements: Document) -> Document:
        requirements.require_type("cxp.requirements")
        payload = requirements.payload
        catalog = self.resolve(payload["catalog"])
        definitions = {item["name"]: item for item in catalog.payload["capabilities"]}
        issues: list[ValidationIssue] = []

        def visit(node: JsonObject, path: str) -> None:
            if node["operator"] in ("all", "any"):
                for index, child in enumerate(node["conditions"]):
                    visit(child, f"{path}/conditions/{index}")
                return
            definition = definitions.get(node["capability"])
            if definition is None:
                issues.extend(
                    invalid(
                        "unknown_capability",
                        f"{path}/capability",
                        "Required capability is absent from catalog",
                    ).issues
                )
                return
            try:
                validate_leaf(node, definition, path)
            except InvalidDocumentError as error:
                issues.extend(error.issues)

        visit(payload["requirement"], "/payload/requirement")
        if issues:
            raise InvalidDocumentError(
                sorted(issues, key=lambda issue: (issue.path, issue.code))
            )
        return catalog
