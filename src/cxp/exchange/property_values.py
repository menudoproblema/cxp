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
    value: Any,
    definition: JsonObject,
    path: str,
    *,
    allow_null: bool = True,
    check_constraints: bool = True,
) -> Comparable:
    kind = definition["kind"]
    if value is None:
        if allow_null and definition["nullable"]:
            return None
        raise invalid("null_not_allowed", path, "Property does not allow null here")
    if kind == "string" and isinstance(value, str):
        if check_constraints:
            _check_domain((value,), definition, path)
        return value
    if kind == "boolean" and type(value) is bool:
        return value
    if kind == "integer" and type(value) is int:
        if check_constraints:
            _check_bounds(value, definition, path)
        return value
    if kind == "string_set" and isinstance(value, list):
        if all(isinstance(item, str) for item in value) and len(set(value)) == len(
            value
        ):
            if check_constraints:
                _check_domain(value, definition, path)
            return frozenset(value)
    if kind == "decimal" and isinstance(value, str):
        result = Fraction(Decimal(normalize_decimal(value, path=path)))
        if check_constraints:
            _check_bounds(result, definition, path)
        return result
    if kind == "quantity" and isinstance(value, dict):
        quantity = Quantity(value["value"], value["unit"])
        if quantity.dimension != definition["dimension"]:
            raise invalid(
                "dimension_mismatch", path, "Quantity has the wrong dimension"
            )
        if check_constraints:
            _check_bounds(quantity.exact_value, definition, path)
        return quantity.exact_value
    raise invalid("property_type_mismatch", path, f"Expected property kind {kind!r}")


def _check_domain(
    values: list[str] | tuple[str, ...], definition: JsonObject, path: str
) -> None:
    domain = definition.get("domain")
    if domain is None or domain["mode"] == "open":
        return
    allowed = set(domain["values"])
    for index, value in enumerate(values):
        if value not in allowed:
            location = path if definition["kind"] == "string" else f"{path}/{index}"
            raise invalid(
                "value_outside_domain", location, "Value is outside the closed domain"
            )


def _check_bounds(value: int | Fraction, definition: JsonObject, path: str) -> None:
    bounds = definition.get("bounds")
    if bounds is None:
        return
    for name, excluded in (
        ("minimum", "below_catalog_minimum"),
        ("maximum", "above_catalog_maximum"),
    ):
        if name not in bounds:
            continue
        bound = property_value(
            bounds[name],
            definition,
            f"{path}/{name}",
            allow_null=False,
            check_constraints=False,
        )
        assert isinstance(bound, (int, Fraction)) and not isinstance(bound, bool)
        inclusive = bounds.get(f"{name}_inclusive", True)
        outside = (
            (value < bound or (value == bound and not inclusive))
            if name == "minimum"
            else (value > bound or (value == bound and not inclusive))
        )
        if outside:
            raise invalid(excluded, path, "Value is outside the catalog bounds")
