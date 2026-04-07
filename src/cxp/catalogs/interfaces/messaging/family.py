from __future__ import annotations

from cxp.catalogs.base import (
    CapabilityCatalog,
    CatalogCapability,
    CatalogOperation,
    ConformanceTier,
    register_catalog,
)
from cxp.catalogs.results import (
    Message,
    MessageAck,
)

MESSAGING_INTERFACE = "messaging/event-bus"

# Capability Names
MESSAGING_PUB_SUB = "pub_sub"
MESSAGING_REQUEST_REPLY = "request_reply"
MESSAGING_DURABLE_STREAMS = "durable_streams"

# Operation Names
MESSAGING_OP_PUBLISH = "messaging.publish"
MESSAGING_OP_SUBSCRIBE = "messaging.subscribe"
MESSAGING_OP_REQUEST = "messaging.request"

MESSAGING_CATALOG = register_catalog(
    CapabilityCatalog(
        interface=MESSAGING_INTERFACE,
        abstract=True,
        description=(
            "Abstract base for all messaging providers (NATS, Kafka, RabbitMQ). "
            "Defines core patterns like pub/sub, request/reply and persistent streams."
        ),
        capabilities=(
            CatalogCapability(
                name=MESSAGING_PUB_SUB,
                description="One-to-many asynchronous message distribution.",
                operations=(
                    CatalogOperation(
                        name=MESSAGING_OP_PUBLISH,
                        result_type="messaging.ack",
                        result_schema=MessageAck,
                    ),
                    CatalogOperation(
                        name=MESSAGING_OP_SUBSCRIBE,
                        result_type="messaging.stream",
                        result_schema=Message,
                    ),
                ),
            ),
            CatalogCapability(
                name=MESSAGING_REQUEST_REPLY,
                description="One-to-one synchronous communication pattern (for Commands).",
                operations=(
                    CatalogOperation(
                        name=MESSAGING_OP_REQUEST,
                        result_type="messaging.reply",
                        result_schema=Message,
                    ),
                ),
            ),
            CatalogCapability(
                name=MESSAGING_DURABLE_STREAMS,
                description="Persistence and replayability of message history.",
            ),
        ),
        tiers=(
            ConformanceTier(
                name="core",
                required_capabilities=(MESSAGING_PUB_SUB,),
                description="Minimum functional message bus.",
            ),
            ConformanceTier(
                name="reliable",
                required_capabilities=(MESSAGING_PUB_SUB, MESSAGING_DURABLE_STREAMS),
                description="Message bus with persistence support (Event Store).",
            ),
        ),
    ),
    replace=True,
)

__all__ = (
    "MESSAGING_CATALOG",
    "MESSAGING_INTERFACE",
    "MESSAGING_OP_PUBLISH",
    "MESSAGING_OP_SUBSCRIBE",
    "MESSAGING_OP_REQUEST",
)
