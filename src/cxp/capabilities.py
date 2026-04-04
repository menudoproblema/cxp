from __future__ import annotations

from collections.abc import Iterable
from typing import TypeVar

import msgspec

T = TypeVar("T")
# El valor real esperado aquí es un mapping simple o un msgspec.Struct,
# pero msgspec no permite unions con varios tipos "dict-like" al decodificar.
# Se mantiene deliberadamente amplio para preservar roundtrip y conversión.
type CapabilityMetadata = object


class Capability(msgspec.Struct, frozen=True):
    name: str
    metadata: CapabilityMetadata = msgspec.field(default_factory=dict)

    def get_metadata(self, struct_type: type[T]) -> T:
        """Helper para obtener la metadata convertida a un tipo específico."""
        if isinstance(self.metadata, struct_type):
            return self.metadata
        return msgspec.convert(self.metadata, struct_type)


class CapabilityMatrix(msgspec.Struct, frozen=True):
    capabilities: tuple[Capability, ...] = ()

    @classmethod
    def from_names(cls, names: Iterable[str]) -> CapabilityMatrix:
        """Helper para crear una matriz a partir de una lista de nombres simples."""
        return cls(capabilities=tuple(Capability(name=name) for name in names))

    def has_capability(self, name: str) -> bool:
        return any(c.name == name for c in self.capabilities)

    def get_capability(self, name: str) -> Capability | None:
        for c in self.capabilities:
            if c.name == name:
                return c
        return None
