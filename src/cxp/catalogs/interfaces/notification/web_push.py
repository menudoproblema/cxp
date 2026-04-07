from __future__ import annotations

import msgspec

from cxp.catalogs.base import (
    CapabilityCatalog,
    CapabilityTelemetry,
    CatalogCapability,
    CatalogOperation,
    ConformanceTier,
    TelemetryMetricSpec,
    register_catalog,
)
from cxp.catalogs.common import (
    CXP_RESOURCE_NAME,
    PUSH_OUTCOME,
)
from cxp.catalogs.interfaces.notification.family import (
    NOTIFICATION_INTERFACE,
    NOTIFICATION_OP_SEND,
)
from cxp.catalogs.results import PushResult

WEB_PUSH_INTERFACE = "notification/web-push"

# Web-Push Specific Capabilities
WEB_PUSH_VAPID_CONFIG = "vapid_configuration"

class VapidMetadata(msgspec.Struct, frozen=True):
    public_key: str
    subject: str
    expiration_hours: int = 12

_PUSH_TELEMETRY = CapabilityTelemetry(
    metrics=(
        TelemetryMetricSpec(
            name="push.web.sent",
            required_labels=(CXP_RESOURCE_NAME, PUSH_OUTCOME),
        ),
    ),
)

WEB_PUSH_CATALOG = register_catalog(
    CapabilityCatalog(
        interface=WEB_PUSH_INTERFACE,
        satisfies_interfaces=(NOTIFICATION_INTERFACE,),
        description=(
            "Specialized notification provider for W3C Web Push, using VAPID "
            "for browser authentication."
        ),
        capabilities=(
            CatalogCapability(
                name=WEB_PUSH_VAPID_CONFIG,
                description="Cryptographic configuration for browser push services.",
                metadata_schema=VapidMetadata,
            ),
            CatalogCapability(
                name="delivery",
                description="Standard Web Push delivery to browser endpoints.",
                telemetry=_PUSH_TELEMETRY,
                operations=(
                    CatalogOperation(
                        name=NOTIFICATION_OP_SEND,
                        result_type="push.result",
                        result_schema=PushResult,
                        description="Send a Web Push message to a browser subscriber.",
                    ),
                ),
            ),
        ),
        tiers=(
            ConformanceTier(
                name="core",
                required_capabilities=(WEB_PUSH_VAPID_CONFIG, "delivery"),
                description="Standard W3C-compliant Web Push provider.",
            ),
        ),
    ),
    replace=True,
)

__all__ = (
    "WEB_PUSH_CATALOG",
    "WEB_PUSH_INTERFACE",
)
