"""Magnitudes exactas, independientes del contexto decimal del proceso."""

from __future__ import annotations

import re
from dataclasses import dataclass
from decimal import Decimal
from fractions import Fraction
from types import MappingProxyType

from cxp.exchange.errors import invalid

__all__ = ("Quantity", "normalize_decimal")

DECIMAL_PATTERN = r"-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?"
UNITS = MappingProxyType(
    {
        "um": ("length", Fraction(1, 1000)),
        "mm": ("length", Fraction(1)),
        "in": ("length", Fraction(127, 5)),
        "pt": ("length", Fraction(127, 360)),
        "g": ("mass", Fraction(1)),
        "kg": ("mass", Fraction(1000)),
        "dpi": ("resolution", Fraction(1)),
        "deg": ("angle", Fraction(1)),
    }
)


def normalize_decimal(value: str, *, path: str = "") -> str:
    if (
        not isinstance(value, str)
        or len(value) > 128
        or re.fullmatch(DECIMAL_PATTERN, value) is None
    ):
        raise invalid("invalid_decimal", path, "Expected a finite decimal string")
    # Eliminamos ceros sin usar operaciones sujetas al contexto de Decimal.
    whole, dot, fraction = value.partition(".")
    fraction = fraction.rstrip("0")
    normalized = whole + (dot + fraction if fraction else "")
    return "0" if normalized == "-0" else normalized


@dataclass(frozen=True, slots=True)
class Quantity:
    value: str
    unit: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", normalize_decimal(self.value, path="/value"))
        if not isinstance(self.unit, str) or self.unit not in UNITS:
            raise invalid("unknown_unit", "/unit", f"Unknown unit: {self.unit!r}")

    @property
    def dimension(self) -> str:
        return UNITS[self.unit][0]

    @property
    def exact_value(self) -> Fraction:
        return Fraction(Decimal(self.value)) * UNITS[self.unit][1]

    def as_dict(self) -> dict[str, str]:
        return {"value": self.value, "unit": self.unit}

    def compare(self, other: Quantity) -> int:
        if self.dimension != other.dimension:
            raise invalid(
                "dimension_mismatch", "", "Cannot compare different dimensions"
            )
        left, right = self.exact_value, other.exact_value
        return (left > right) - (left < right)
