from __future__ import annotations

from cxp.catalogs.base import (
    CapabilityCatalog,
    CatalogCapability,
    CatalogOperation,
    ConformanceTier,
    register_catalog,
)
from cxp.catalogs.results import ActionResult, WebSocketMessage

WEBSOCKET_INTERFACE = "transport/websocket"

# Capability Names
WS_FULL_DUPLEX = "full_duplex"
WS_BINARY_STREAMS = "binary_streams"

# Operation Names
WS_OP_CONNECT = "ws.connect"
WS_OP_SEND = "ws.send"
WS_OP_RECEIVE = "ws.receive"
WS_OP_CLOSE = "ws.close"

WEBSOCKET_CATALOG = register_catalog(
    CapabilityCatalog(
        interface=WEBSOCKET_INTERFACE,
        description="Standard catalog for WebSocket full-duplex communication.",
        capabilities=(
            CatalogCapability(
                name=WS_FULL_DUPLEX,
                description="Concurrent bi-directional message exchange.",
                operations=(
                    CatalogOperation(name=WS_OP_CONNECT, result_type="ws.session"),
                    CatalogOperation(
                        name=WS_OP_SEND,
                        result_type="action.result",
                        result_schema=ActionResult,
                        description="Send a message to the remote peer.",
                    ),
                    CatalogOperation(
                        name=WS_OP_RECEIVE,
                        result_type="ws.message",
                        result_schema=WebSocketMessage,
                        description="Wait for and receive a message.",
                    ),
                    CatalogOperation(
                        name=WS_OP_CLOSE,
                        result_type="action.result",
                        result_schema=ActionResult,
                    ),
                ),
            ),
            CatalogCapability(
                name=WS_BINARY_STREAMS,
                description="Support for raw binary frames (ArrayBuffer/Blob).",
            ),
        ),
        tiers=(
            ConformanceTier(
                name="core",
                required_capabilities=(WS_FULL_DUPLEX,),
                description="Basic functional WebSocket provider.",
            ),
        ),
    ),
    replace=True,
)

__all__ = (
    "WEBSOCKET_CATALOG",
    "WEBSOCKET_INTERFACE",
)
