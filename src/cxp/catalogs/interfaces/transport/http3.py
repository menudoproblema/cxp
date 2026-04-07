from __future__ import annotations

import msgspec

from cxp.catalogs.base import (
    CapabilityCatalog,
    CatalogCapability,
    ConformanceTier,
    register_catalog,
)
from cxp.catalogs.interfaces.transport.family import HTTP_TRANSPORT_INTERFACE

HTTP3_TRANSPORT_INTERFACE = "transport/http3"

# H3 Specific Capabilities
HTTP3_QUIC_TRANSPORT = "quic_transport"
HTTP3_ZERO_RTT = "zero_rtt_handshake"
HTTP3_CONNECTION_MIGRATION = "connection_migration"

class Http3Metadata(msgspec.Struct, frozen=True):
    quic_version: str
    supports_0rtt: bool = False

HTTP3_TRANSPORT_CATALOG = register_catalog(
    CapabilityCatalog(
        interface=HTTP3_TRANSPORT_INTERFACE,
        satisfies_interfaces=(HTTP_TRANSPORT_INTERFACE,),
        description="Standard catalog for HTTP/3 (QUIC) transport.",
        capabilities=(
            CatalogCapability(
                name=HTTP3_QUIC_TRANSPORT,
                description="UDP-based transport with integrated TLS.",
                metadata_schema=Http3Metadata,
            ),
            CatalogCapability(
                name=HTTP3_CONNECTION_MIGRATION,
                description=(
                    "Ability to survive IP/Port changes without dropping requests."
                ),
            ),
        ),
        tiers=(
            ConformanceTier(
                name="core",
                required_capabilities=(HTTP3_QUIC_TRANSPORT,),
                description="Functional HTTP/3 transport.",
            ),
        ),
    ),
    replace=True,
)

__all__ = (
    "HTTP3_TRANSPORT_CATALOG",
    "HTTP3_TRANSPORT_INTERFACE",
)
