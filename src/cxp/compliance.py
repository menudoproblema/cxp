from __future__ import annotations

import msgspec

from cxp._legacy import warn_legacy_import
from cxp.catalogs.base import CapabilityMatrixValidationResult
from cxp.handshake import HandshakeResponse

warn_legacy_import(__name__)


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
