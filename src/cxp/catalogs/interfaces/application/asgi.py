from __future__ import annotations

import msgspec

from cxp.catalogs.base import (
    CapabilityCatalog,
    CapabilityProfile,
    CapabilityRequirement,
    CatalogCapability,
    CatalogOperation,
    ConformanceTier,
    register_catalog,
)
from cxp.catalogs.interfaces.application.family import HTTP_APPLICATION_INTERFACE

ASGI_APPLICATION_INTERFACE = "application/asgi"

ASGI_APPLICATION_HTTP = "http"
ASGI_APPLICATION_WEBSOCKET = "websocket"
ASGI_APPLICATION_LIFESPAN = "lifespan"
ASGI_APPLICATION_TLS = "tls"
ASGI_APPLICATION_WEBSOCKET_DENIAL_RESPONSE = "websocket_denial_response"
ASGI_APPLICATION_HTTP_SERVER_PUSH = "http_server_push"
ASGI_APPLICATION_ZERO_COPY_SEND = "http_zero_copy_send"
ASGI_APPLICATION_PATH_SEND = "http_path_send"
ASGI_APPLICATION_EARLY_HINTS = "http_early_hints"
ASGI_APPLICATION_TRAILERS = "http_trailers"

ASGI_APPLICATION_HTTP_SCOPE_INSPECT = "http.scope.inspect"
ASGI_APPLICATION_HTTP_REQUEST_RECEIVE = "http.request.receive"
ASGI_APPLICATION_HTTP_DISCONNECT_RECEIVE = "http.disconnect.receive"
ASGI_APPLICATION_HTTP_RESPONSE_START = "http.response.start"
ASGI_APPLICATION_HTTP_RESPONSE_BODY = "http.response.body"

ASGI_APPLICATION_WEBSOCKET_SCOPE_INSPECT = "websocket.scope.inspect"
ASGI_APPLICATION_WEBSOCKET_CONNECT_RECEIVE = "websocket.connect.receive"
ASGI_APPLICATION_WEBSOCKET_ACCEPT = "websocket.accept"
ASGI_APPLICATION_WEBSOCKET_RECEIVE = "websocket.receive"
ASGI_APPLICATION_WEBSOCKET_SEND = "websocket.send"
ASGI_APPLICATION_WEBSOCKET_CLOSE = "websocket.close"
ASGI_APPLICATION_WEBSOCKET_DISCONNECT_RECEIVE = "websocket.disconnect.receive"

ASGI_APPLICATION_LIFESPAN_SCOPE_INSPECT = "lifespan.scope.inspect"
ASGI_APPLICATION_LIFESPAN_STARTUP_RECEIVE = "lifespan.startup.receive"
ASGI_APPLICATION_LIFESPAN_STARTUP_COMPLETE = "lifespan.startup.complete"
ASGI_APPLICATION_LIFESPAN_STARTUP_FAILED = "lifespan.startup.failed"
ASGI_APPLICATION_LIFESPAN_SHUTDOWN_RECEIVE = "lifespan.shutdown.receive"
ASGI_APPLICATION_LIFESPAN_SHUTDOWN_COMPLETE = "lifespan.shutdown.complete"
ASGI_APPLICATION_LIFESPAN_SHUTDOWN_FAILED = "lifespan.shutdown.failed"

ASGI_APPLICATION_TLS_SCOPE_INSPECT = "tls.scope.inspect"

ASGI_APPLICATION_WEBSOCKET_HTTP_RESPONSE_START = (
    "websocket.http.response.start"
)
ASGI_APPLICATION_WEBSOCKET_HTTP_RESPONSE_BODY = "websocket.http.response.body"
ASGI_APPLICATION_HTTP_PUSH = "http.response.push"
ASGI_APPLICATION_HTTP_PATH_SEND = "http.response.pathsend"
ASGI_APPLICATION_HTTP_EARLY_HINT = "http.response.early_hint"
ASGI_APPLICATION_HTTP_TRAILERS = "http.response.trailers"
ASGI_APPLICATION_HTTP_ZERO_COPY_SEND = "http.response.zerocopysend"

ASGI_APPLICATION_HTTP_CORE_TIER = "http-core"
ASGI_APPLICATION_WEB_CORE_TIER = "web-core"
ASGI_APPLICATION_REALTIME_TIER = "realtime"

ASGI_APPLICATION_HTTP_CORE_PROFILE_NAME = "asgi-http-core"
ASGI_APPLICATION_WEB_CORE_PROFILE_NAME = "asgi-web-core"
ASGI_APPLICATION_REALTIME_PROFILE_NAME = "asgi-realtime"
ASGI_APPLICATION_TLS_AWARE_PROFILE_NAME = "asgi-tls-aware"
ASGI_APPLICATION_EXTENDED_HTTP_PROFILE_NAME = "asgi-extended-http"
ASGI_APPLICATION_WEBSOCKET_DENIAL_PROFILE_NAME = "asgi-websocket-denial"
ASGI_APPLICATION_LIFESPAN_PROFILE_NAME = "asgi-lifespan"
ASGI_APPLICATION_EARLY_HINTS_PROFILE_NAME = "asgi-early-hints"


class AsgiHttpMetadata(msgspec.Struct, frozen=True):
    specVersion: str
    httpVersions: tuple[str, ...]


class AsgiWebSocketMetadata(msgspec.Struct, frozen=True):
    specVersion: str
    subprotocols: tuple[str, ...]


class AsgiLifespanMetadata(msgspec.Struct, frozen=True):
    specVersion: str


class AsgiTlsMetadata(msgspec.Struct, frozen=True):
    scopeKeys: tuple[str, ...]


ASGI_APPLICATION_CATALOG = register_catalog(
    CapabilityCatalog(
        interface=ASGI_APPLICATION_INTERFACE,
        description="Canonical catalog for ASGI-compatible applications.",
        satisfies_interfaces=(HTTP_APPLICATION_INTERFACE,),
        capabilities=(
            CatalogCapability(
                name=ASGI_APPLICATION_HTTP,
                description="Primary ASGI HTTP protocol.",
                operations=(
                    CatalogOperation(
                        name=ASGI_APPLICATION_HTTP_SCOPE_INSPECT,
                        result_type="http.scope",
                    ),
                    CatalogOperation(
                        name=ASGI_APPLICATION_HTTP_REQUEST_RECEIVE,
                        result_type="http.request",
                    ),
                    CatalogOperation(
                        name=ASGI_APPLICATION_HTTP_DISCONNECT_RECEIVE,
                        result_type="http.disconnect",
                    ),
                    CatalogOperation(
                        name=ASGI_APPLICATION_HTTP_RESPONSE_START,
                        result_type="http.response.started",
                    ),
                    CatalogOperation(
                        name=ASGI_APPLICATION_HTTP_RESPONSE_BODY,
                        result_type="http.response.body",
                    ),
                ),
                metadata_schema=AsgiHttpMetadata,
            ),
            CatalogCapability(
                name=ASGI_APPLICATION_WEBSOCKET,
                description="ASGI WebSocket protocol.",
                operations=(
                    CatalogOperation(
                        name=ASGI_APPLICATION_WEBSOCKET_SCOPE_INSPECT,
                        result_type="websocket.scope",
                    ),
                    CatalogOperation(
                        name=ASGI_APPLICATION_WEBSOCKET_CONNECT_RECEIVE,
                        result_type="websocket.connect",
                    ),
                    CatalogOperation(
                        name=ASGI_APPLICATION_WEBSOCKET_ACCEPT,
                        result_type="websocket.accepted",
                    ),
                    CatalogOperation(
                        name=ASGI_APPLICATION_WEBSOCKET_RECEIVE,
                        result_type="websocket.receive",
                    ),
                    CatalogOperation(
                        name=ASGI_APPLICATION_WEBSOCKET_SEND,
                        result_type="websocket.send",
                    ),
                    CatalogOperation(
                        name=ASGI_APPLICATION_WEBSOCKET_CLOSE,
                        result_type="websocket.closed",
                    ),
                    CatalogOperation(
                        name=ASGI_APPLICATION_WEBSOCKET_DISCONNECT_RECEIVE,
                        result_type="websocket.disconnect",
                    ),
                ),
                metadata_schema=AsgiWebSocketMetadata,
            ),
            CatalogCapability(
                name=ASGI_APPLICATION_LIFESPAN,
                description="ASGI lifespan protocol.",
                operations=(
                    CatalogOperation(
                        name=ASGI_APPLICATION_LIFESPAN_SCOPE_INSPECT,
                        result_type="lifespan.scope",
                    ),
                    CatalogOperation(
                        name=ASGI_APPLICATION_LIFESPAN_STARTUP_RECEIVE,
                        result_type="lifespan.startup",
                    ),
                    CatalogOperation(
                        name=ASGI_APPLICATION_LIFESPAN_STARTUP_COMPLETE,
                        result_type="lifespan.startup.complete",
                    ),
                    CatalogOperation(
                        name=ASGI_APPLICATION_LIFESPAN_STARTUP_FAILED,
                        result_type="lifespan.startup.failed",
                    ),
                    CatalogOperation(
                        name=ASGI_APPLICATION_LIFESPAN_SHUTDOWN_RECEIVE,
                        result_type="lifespan.shutdown",
                    ),
                    CatalogOperation(
                        name=ASGI_APPLICATION_LIFESPAN_SHUTDOWN_COMPLETE,
                        result_type="lifespan.shutdown.complete",
                    ),
                    CatalogOperation(
                        name=ASGI_APPLICATION_LIFESPAN_SHUTDOWN_FAILED,
                        result_type="lifespan.shutdown.failed",
                    ),
                ),
                metadata_schema=AsgiLifespanMetadata,
            ),
            CatalogCapability(
                name=ASGI_APPLICATION_TLS,
                description="ASGI TLS extension.",
                operations=(
                    CatalogOperation(
                        name=ASGI_APPLICATION_TLS_SCOPE_INSPECT,
                        result_type="tls.scope",
                    ),
                ),
                metadata_schema=AsgiTlsMetadata,
            ),
            CatalogCapability(
                name=ASGI_APPLICATION_WEBSOCKET_DENIAL_RESPONSE,
                description="HTTP denial response for WebSocket.",
                operations=(
                    CatalogOperation(
                        name=ASGI_APPLICATION_WEBSOCKET_HTTP_RESPONSE_START,
                        result_type="websocket.http.response.started",
                    ),
                    CatalogOperation(
                        name=ASGI_APPLICATION_WEBSOCKET_HTTP_RESPONSE_BODY,
                        result_type="websocket.http.response.body",
                    ),
                ),
            ),
            CatalogCapability(
                name=ASGI_APPLICATION_HTTP_SERVER_PUSH,
                description="ASGI HTTP server push support.",
                operations=(
                    CatalogOperation(
                        name=ASGI_APPLICATION_HTTP_PUSH,
                        result_type="http.response.push",
                    ),
                ),
            ),
            CatalogCapability(
                name=ASGI_APPLICATION_ZERO_COPY_SEND,
                description="ASGI zerocopysend extension.",
                operations=(
                    CatalogOperation(
                        name=ASGI_APPLICATION_HTTP_ZERO_COPY_SEND,
                        result_type="http.response.zerocopysend",
                    ),
                ),
            ),
            CatalogCapability(
                name=ASGI_APPLICATION_PATH_SEND,
                description="ASGI pathsend extension.",
                operations=(
                    CatalogOperation(
                        name=ASGI_APPLICATION_HTTP_PATH_SEND,
                        result_type="http.response.pathsend",
                    ),
                ),
            ),
            CatalogCapability(
                name=ASGI_APPLICATION_EARLY_HINTS,
                description="ASGI early hints extension.",
                operations=(
                    CatalogOperation(
                        name=ASGI_APPLICATION_HTTP_EARLY_HINT,
                        result_type="http.response.early_hint",
                    ),
                ),
            ),
            CatalogCapability(
                name=ASGI_APPLICATION_TRAILERS,
                description="ASGI trailers extension.",
                operations=(
                    CatalogOperation(
                        name=ASGI_APPLICATION_HTTP_TRAILERS,
                        result_type="http.response.trailers",
                    ),
                ),
            ),
        ),
        tiers=(
            ConformanceTier(
                name=ASGI_APPLICATION_HTTP_CORE_TIER,
                required_capabilities=(ASGI_APPLICATION_HTTP,),
                description="ASGI application with HTTP support.",
            ),
            ConformanceTier(
                name=ASGI_APPLICATION_WEB_CORE_TIER,
                required_capabilities=(
                    ASGI_APPLICATION_HTTP,
                    ASGI_APPLICATION_LIFESPAN,
                ),
                description="Web ASGI application with explicit lifecycle support.",
            ),
            ConformanceTier(
                name=ASGI_APPLICATION_REALTIME_TIER,
                required_capabilities=(
                    ASGI_APPLICATION_HTTP,
                    ASGI_APPLICATION_LIFESPAN,
                    ASGI_APPLICATION_WEBSOCKET,
                ),
                description="ASGI application with HTTP, lifespan, and WebSocket.",
            ),
        ),
    )
)

ASGI_APPLICATION_HTTP_CORE_PROFILE = CapabilityProfile(
    name=ASGI_APPLICATION_HTTP_CORE_PROFILE_NAME,
    interface=ASGI_APPLICATION_INTERFACE,
    description="Base ASGI HTTP profile.",
    requirements=(
        CapabilityRequirement(
            capability_name=ASGI_APPLICATION_HTTP,
            required_operations=(
                ASGI_APPLICATION_HTTP_SCOPE_INSPECT,
                ASGI_APPLICATION_HTTP_REQUEST_RECEIVE,
                ASGI_APPLICATION_HTTP_DISCONNECT_RECEIVE,
                ASGI_APPLICATION_HTTP_RESPONSE_START,
                ASGI_APPLICATION_HTTP_RESPONSE_BODY,
            ),
            required_metadata_keys=("specVersion", "httpVersions"),
        ),
    ),
)

ASGI_APPLICATION_LIFESPAN_PROFILE = CapabilityProfile(
    name=ASGI_APPLICATION_LIFESPAN_PROFILE_NAME,
    interface=ASGI_APPLICATION_INTERFACE,
    description="ASGI profile focused on explicit lifecycle support.",
    requirements=(
        CapabilityRequirement(
            capability_name=ASGI_APPLICATION_LIFESPAN,
            required_operations=(
                ASGI_APPLICATION_LIFESPAN_SCOPE_INSPECT,
                ASGI_APPLICATION_LIFESPAN_STARTUP_RECEIVE,
                ASGI_APPLICATION_LIFESPAN_STARTUP_COMPLETE,
                ASGI_APPLICATION_LIFESPAN_STARTUP_FAILED,
                ASGI_APPLICATION_LIFESPAN_SHUTDOWN_RECEIVE,
                ASGI_APPLICATION_LIFESPAN_SHUTDOWN_COMPLETE,
                ASGI_APPLICATION_LIFESPAN_SHUTDOWN_FAILED,
            ),
            required_metadata_keys=("specVersion",),
        ),
    ),
)

ASGI_APPLICATION_WEB_CORE_PROFILE = CapabilityProfile(
    name=ASGI_APPLICATION_WEB_CORE_PROFILE_NAME,
    interface=ASGI_APPLICATION_INTERFACE,
    description="Base web profile with HTTP and lifespan.",
    requirements=(
        *ASGI_APPLICATION_HTTP_CORE_PROFILE.requirements,
        *ASGI_APPLICATION_LIFESPAN_PROFILE.requirements,
    ),
)

ASGI_APPLICATION_REALTIME_PROFILE = CapabilityProfile(
    name=ASGI_APPLICATION_REALTIME_PROFILE_NAME,
    interface=ASGI_APPLICATION_INTERFACE,
    description="Realtime ASGI profile with WebSocket.",
    requirements=(
        *ASGI_APPLICATION_WEB_CORE_PROFILE.requirements,
        CapabilityRequirement(
            capability_name=ASGI_APPLICATION_WEBSOCKET,
            required_operations=(
                ASGI_APPLICATION_WEBSOCKET_SCOPE_INSPECT,
                ASGI_APPLICATION_WEBSOCKET_CONNECT_RECEIVE,
                ASGI_APPLICATION_WEBSOCKET_ACCEPT,
                ASGI_APPLICATION_WEBSOCKET_RECEIVE,
                ASGI_APPLICATION_WEBSOCKET_SEND,
                ASGI_APPLICATION_WEBSOCKET_CLOSE,
                ASGI_APPLICATION_WEBSOCKET_DISCONNECT_RECEIVE,
            ),
            required_metadata_keys=("specVersion", "subprotocols"),
        ),
    ),
)

ASGI_APPLICATION_TLS_AWARE_PROFILE = CapabilityProfile(
    name=ASGI_APPLICATION_TLS_AWARE_PROFILE_NAME,
    interface=ASGI_APPLICATION_INTERFACE,
    description="ASGI profile that requires TLS metadata awareness.",
    requirements=(
        CapabilityRequirement(
            capability_name=ASGI_APPLICATION_TLS,
            required_operations=(ASGI_APPLICATION_TLS_SCOPE_INSPECT,),
            required_metadata_keys=("scopeKeys",),
        ),
    ),
)

ASGI_APPLICATION_EXTENDED_HTTP_PROFILE = CapabilityProfile(
    name=ASGI_APPLICATION_EXTENDED_HTTP_PROFILE_NAME,
    interface=ASGI_APPLICATION_INTERFACE,
    description="ASGI profile with advanced HTTP extensions.",
    requirements=(
        CapabilityRequirement(
            capability_name=ASGI_APPLICATION_EARLY_HINTS,
            required_operations=(ASGI_APPLICATION_HTTP_EARLY_HINT,),
        ),
        CapabilityRequirement(
            capability_name=ASGI_APPLICATION_TRAILERS,
            required_operations=(ASGI_APPLICATION_HTTP_TRAILERS,),
        ),
        CapabilityRequirement(
            capability_name=ASGI_APPLICATION_ZERO_COPY_SEND,
            required_operations=(ASGI_APPLICATION_HTTP_ZERO_COPY_SEND,),
        ),
        CapabilityRequirement(
            capability_name=ASGI_APPLICATION_PATH_SEND,
            required_operations=(ASGI_APPLICATION_HTTP_PATH_SEND,),
        ),
        CapabilityRequirement(
            capability_name=ASGI_APPLICATION_HTTP_SERVER_PUSH,
            required_operations=(ASGI_APPLICATION_HTTP_PUSH,),
        ),
    ),
)

ASGI_APPLICATION_WEBSOCKET_DENIAL_PROFILE = CapabilityProfile(
    name=ASGI_APPLICATION_WEBSOCKET_DENIAL_PROFILE_NAME,
    interface=ASGI_APPLICATION_INTERFACE,
    description="ASGI profile with WebSocket denial HTTP response support.",
    requirements=(
        CapabilityRequirement(
            capability_name=ASGI_APPLICATION_WEBSOCKET_DENIAL_RESPONSE,
            required_operations=(
                ASGI_APPLICATION_WEBSOCKET_HTTP_RESPONSE_START,
                ASGI_APPLICATION_WEBSOCKET_HTTP_RESPONSE_BODY,
            ),
        ),
    ),
)

ASGI_APPLICATION_EARLY_HINTS_PROFILE = CapabilityProfile(
    name=ASGI_APPLICATION_EARLY_HINTS_PROFILE_NAME,
    interface=ASGI_APPLICATION_INTERFACE,
    description="Focused ASGI profile for early hints support.",
    requirements=(
        CapabilityRequirement(
            capability_name=ASGI_APPLICATION_EARLY_HINTS,
            required_operations=(ASGI_APPLICATION_HTTP_EARLY_HINT,),
        ),
    ),
)

__all__ = (
    "ASGI_APPLICATION_CATALOG",
    "ASGI_APPLICATION_EARLY_HINTS",
    "ASGI_APPLICATION_EARLY_HINTS_PROFILE",
    "ASGI_APPLICATION_EARLY_HINTS_PROFILE_NAME",
    "ASGI_APPLICATION_EXTENDED_HTTP_PROFILE",
    "ASGI_APPLICATION_EXTENDED_HTTP_PROFILE_NAME",
    "ASGI_APPLICATION_HTTP",
    "ASGI_APPLICATION_HTTP_CORE_PROFILE",
    "ASGI_APPLICATION_HTTP_CORE_PROFILE_NAME",
    "ASGI_APPLICATION_HTTP_CORE_TIER",
    "ASGI_APPLICATION_HTTP_DISCONNECT_RECEIVE",
    "ASGI_APPLICATION_HTTP_EARLY_HINT",
    "ASGI_APPLICATION_HTTP_PATH_SEND",
    "ASGI_APPLICATION_HTTP_PUSH",
    "ASGI_APPLICATION_HTTP_REQUEST_RECEIVE",
    "ASGI_APPLICATION_HTTP_RESPONSE_BODY",
    "ASGI_APPLICATION_HTTP_RESPONSE_START",
    "ASGI_APPLICATION_HTTP_SCOPE_INSPECT",
    "ASGI_APPLICATION_HTTP_SERVER_PUSH",
    "ASGI_APPLICATION_HTTP_TRAILERS",
    "ASGI_APPLICATION_HTTP_ZERO_COPY_SEND",
    "ASGI_APPLICATION_INTERFACE",
    "ASGI_APPLICATION_LIFESPAN",
    "ASGI_APPLICATION_LIFESPAN_PROFILE",
    "ASGI_APPLICATION_LIFESPAN_PROFILE_NAME",
    "ASGI_APPLICATION_LIFESPAN_SHUTDOWN_COMPLETE",
    "ASGI_APPLICATION_LIFESPAN_SHUTDOWN_FAILED",
    "ASGI_APPLICATION_LIFESPAN_SHUTDOWN_RECEIVE",
    "ASGI_APPLICATION_LIFESPAN_SCOPE_INSPECT",
    "ASGI_APPLICATION_LIFESPAN_STARTUP_COMPLETE",
    "ASGI_APPLICATION_LIFESPAN_STARTUP_FAILED",
    "ASGI_APPLICATION_LIFESPAN_STARTUP_RECEIVE",
    "ASGI_APPLICATION_PATH_SEND",
    "ASGI_APPLICATION_REALTIME_PROFILE",
    "ASGI_APPLICATION_REALTIME_PROFILE_NAME",
    "ASGI_APPLICATION_REALTIME_TIER",
    "ASGI_APPLICATION_TLS",
    "ASGI_APPLICATION_TLS_AWARE_PROFILE",
    "ASGI_APPLICATION_TLS_AWARE_PROFILE_NAME",
    "ASGI_APPLICATION_TLS_SCOPE_INSPECT",
    "ASGI_APPLICATION_TRAILERS",
    "ASGI_APPLICATION_WEBSOCKET",
    "ASGI_APPLICATION_WEBSOCKET_ACCEPT",
    "ASGI_APPLICATION_WEBSOCKET_CLOSE",
    "ASGI_APPLICATION_WEBSOCKET_CONNECT_RECEIVE",
    "ASGI_APPLICATION_WEBSOCKET_DENIAL_PROFILE",
    "ASGI_APPLICATION_WEBSOCKET_DENIAL_PROFILE_NAME",
    "ASGI_APPLICATION_WEBSOCKET_DENIAL_RESPONSE",
    "ASGI_APPLICATION_WEBSOCKET_DISCONNECT_RECEIVE",
    "ASGI_APPLICATION_WEBSOCKET_HTTP_RESPONSE_BODY",
    "ASGI_APPLICATION_WEBSOCKET_HTTP_RESPONSE_START",
    "ASGI_APPLICATION_WEBSOCKET_RECEIVE",
    "ASGI_APPLICATION_WEBSOCKET_SCOPE_INSPECT",
    "ASGI_APPLICATION_WEBSOCKET_SEND",
    "ASGI_APPLICATION_WEB_CORE_PROFILE",
    "ASGI_APPLICATION_WEB_CORE_PROFILE_NAME",
    "ASGI_APPLICATION_WEB_CORE_TIER",
    "ASGI_APPLICATION_ZERO_COPY_SEND",
)
