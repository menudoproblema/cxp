"""Pure typed property conversion for validated exchange data."""

from __future__ import annotations

from decimal import Decimal
from fractions import Fraction
from typing import Any

from cxp.exchange.errors import invalid
from cxp.exchange.quantities import Quantity, normalize_decimal

type JsonObject = dict[str, Any]
type Comparable = str | bool | int | Fraction | frozenset[str] | None


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
