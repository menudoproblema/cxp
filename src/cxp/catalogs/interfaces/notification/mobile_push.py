from __future__ import annotations

import msgspec

from cxp.catalogs.base import (
    CapabilityCatalog,
    CatalogCapability,
    CatalogOperation,
    ConformanceTier,
    register_catalog,
)
from cxp.catalogs.interfaces.notification.family import (
    NOTIFICATION_INTERFACE,
    NOTIFICATION_OP_SEND,
)
from cxp.catalogs.results import ActionResult, PushResult

MOBILE_PUSH_INTERFACE = "notification/mobile-push"

# Capability Names
PUSH_FCM_SUPPORT = "fcm_protocol"  # Firebase Cloud Messaging
PUSH_APNS_SUPPORT = "apns_protocol" # Apple Push Notification service
PUSH_TOPIC_MANAGEMENT = "topic_management"

class FcmMetadata(msgspec.Struct, frozen=True):
    project_id: str
    is_v1_api: bool = True

class ApnsMetadata(msgspec.Struct, frozen=True):
    team_id: str
    key_id: str
    bundle_id: str
    is_production: bool = False

MOBILE_PUSH_CATALOG = register_catalog(
    CapabilityCatalog(
        interface=MOBILE_PUSH_INTERFACE,
        satisfies_interfaces=(NOTIFICATION_INTERFACE,),
        description=(
            "Standard catalog for Mobile Push providers, supporting FCM (Android) "
            "and APNs (iOS) delivery with token lifecycle management."
        ),
        capabilities=(
            CatalogCapability(
                name=PUSH_FCM_SUPPORT,
                description="Delivery via Google Firebase Cloud Messaging.",
                metadata_schema=FcmMetadata,
                operations=(
                    CatalogOperation(
                        name=NOTIFICATION_OP_SEND,
                        result_type="push.mobile_result",
                        result_schema=PushResult,
                    ),
                ),
            ),
            CatalogCapability(
                name=PUSH_APNS_SUPPORT,
                description="Delivery via Apple Push Notification service (HTTP/2).",
                metadata_schema=ApnsMetadata,
                operations=(
                    CatalogOperation(
                        name=NOTIFICATION_OP_SEND,
                        result_type="push.mobile_result",
                        result_schema=PushResult,
                    ),
                ),
            ),
            CatalogCapability(
                name=PUSH_TOPIC_MANAGEMENT,
                description="Ability to subscribe/unsubscribe devices to interest topics.",
                operations=(
                    CatalogOperation(
                        name="mobile.topic_subscribe",
                        result_type="action.result",
                        result_schema=ActionResult,
                    ),
                    CatalogOperation(
                        name="mobile.topic_unsubscribe",
                        result_type="action.result",
                        result_schema=ActionResult,
                    ),
                ),
            ),
        ),
        tiers=(
            ConformanceTier(
                name="cross-platform",
                required_capabilities=(PUSH_FCM_SUPPORT, PUSH_APNS_SUPPORT),
                description="Provider capable of reaching both Android and iOS devices.",
            ),
        ),
    ),
    replace=True,
)

__all__ = (
    "MOBILE_PUSH_CATALOG",
    "MOBILE_PUSH_INTERFACE",
)
