from __future__ import annotations

import msgspec

from cxp.catalogs.base import CapabilityMatrixValidationResult
from cxp.handshake import HandshakeResponse


class CatalogComplianceReport(msgspec.Struct, frozen=True):
    compliant: bool
    catalog_interface: str
    offered_interface: str
    required_tier: str | None = None
    reason: str | None = None
    messages: tuple[str, ...] = ()
    validation: CapabilityMatrixValidationResult | None = None


class NegotiatedCatalogDecision(msgspec.Struct, frozen=True):
    response: HandshakeResponse
    compliance: CatalogComplianceReport


__all__ = (
    "CatalogComplianceReport",
    "NegotiatedCatalogDecision",
)
