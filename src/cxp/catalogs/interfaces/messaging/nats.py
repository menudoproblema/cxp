from __future__ import annotations

import msgspec

from cxp.catalogs.base import (
    CapabilityCatalog,
    CatalogCapability,
    ConformanceTier,
    register_catalog,
)
from cxp.catalogs.interfaces.messaging.family import MESSAGING_INTERFACE

NATS_INTERFACE = "messaging/nats"

# NATS Specific Capabilities
NATS_JETSTREAM = "jetstream"
NATS_SUBJECT_MAPPING = "subject_mapping"

class NatsMetadata(msgspec.Struct, frozen=True):
    server_version: str
    max_payload_bytes: int
    jetstream_enabled: bool = False

NATS_CATALOG = register_catalog(
    CapabilityCatalog(
        interface=NATS_INTERFACE,
        satisfies_interfaces=(MESSAGING_INTERFACE,),
        description=(
            "Canonical catalog for NATS.io providers, supporting core NATS "
            "and persistent NATS JetStream semantics."
        ),
        capabilities=(
            CatalogCapability(
                name=NATS_JETSTREAM,
                description="Persistence and guaranteed delivery via JetStream.",
                metadata_schema=NatsMetadata,
            ),
            CatalogCapability(
                name=NATS_SUBJECT_MAPPING,
                description="Dynamic subject remapping and wildcard support.",
            ),
        ),
        tiers=(
            ConformanceTier(
                name="core",
                required_capabilities=(NATS_JETSTREAM,),
                description="Basic NATS server with persistence support.",
            ),
        ),
    ),
    replace=True,
)

__all__ = (
    "NATS_CATALOG",
    "NATS_INTERFACE",
)
