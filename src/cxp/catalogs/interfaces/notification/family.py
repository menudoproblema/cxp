from __future__ import annotations

from cxp.catalogs.base import (
    CapabilityCatalog,
    CatalogCapability,
    CatalogOperation,
    ConformanceTier,
    register_catalog,
)
from cxp.catalogs.results import PushResult

NOTIFICATION_INTERFACE = "notification/common"

# Standard Operation Names
NOTIFICATION_OP_SEND = "notification.send"
NOTIFICATION_OP_BATCH_SEND = "notification.batch_send"

NOTIFICATION_CATALOG = register_catalog(
    CapabilityCatalog(
        interface=NOTIFICATION_INTERFACE,
        abstract=True,
        description=(
            "Abstract base for all notification delivery providers "
            "(WebPush, FCM, SMS, Email). Defines the core contract for "
            "reaching endpoints or devices."
        ),
        capabilities=(
            CatalogCapability(
                name="delivery",
                description=(
                    "Atomic delivery of a message to a single endpoint or device."
                ),
                operations=(
                    CatalogOperation(
                        name=NOTIFICATION_OP_SEND,
                        result_type="notification.result",
                        result_schema=PushResult,
                        description="Send a notification and return delivery status.",
                    ),
                ),
            ),
            CatalogCapability(
                name="batch_delivery",
                description=(
                    "Efficient delivery of notifications to multiple endpoints."
                ),
            ),
        ),
        tiers=(
            ConformanceTier(
                name="core",
                required_capabilities=("delivery",),
                description="Minimum functional notification provider.",
            ),
        ),
    ),
    replace=True,
)

__all__ = (
    "NOTIFICATION_CATALOG",
    "NOTIFICATION_INTERFACE",
    "NOTIFICATION_OP_SEND",
)
