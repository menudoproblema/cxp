from __future__ import annotations

import msgspec

from cxp.catalogs.base import (
    CapabilityCatalog,
    CatalogCapability,
    CatalogOperation,
    ConformanceTier,
    register_catalog,
)
from cxp.catalogs.interfaces.transport.family import HTTP_TRANSPORT_INTERFACE
from cxp.catalogs.results import HttpPushPromise

HTTP2_TRANSPORT_INTERFACE = "transport/http2"

# H2 Specific Capabilities
HTTP2_MULTIPLEXING = "multiplexing"
HTTP2_SERVER_PUSH = "server_push"
HTTP2_HEADER_COMPRESSION = "header_compression"

class Http2Metadata(msgspec.Struct, frozen=True):
    max_concurrent_streams: int = 100
    initial_window_size_bytes: int = 65535

HTTP2_TRANSPORT_CATALOG = register_catalog(
    CapabilityCatalog(
        interface=HTTP2_TRANSPORT_INTERFACE,
        satisfies_interfaces=(HTTP_TRANSPORT_INTERFACE,),
        description="Standard catalog for HTTP/2 multiplexed transport.",
        capabilities=(
            CatalogCapability(
                name=HTTP2_MULTIPLEXING,
                description="Concurrent request streams over a single TCP connection.",
                metadata_schema=Http2Metadata,
            ),
            CatalogCapability(
                name=HTTP2_SERVER_PUSH,
                description="Ability to receive server push promises.",
                operations=(
                    CatalogOperation(
                        name="http2.receive_push",
                        result_type="http2.push_promise",
                        result_schema=HttpPushPromise,
                    ),
                ),
            ),
        ),
        tiers=(
            ConformanceTier(
                name="core",
                required_capabilities=(HTTP2_MULTIPLEXING,),
                description="Functional HTTP/2 transport.",
            ),
        ),
    ),
    replace=True,
)

__all__ = (
    "HTTP2_TRANSPORT_CATALOG",
    "HTTP2_TRANSPORT_INTERFACE",
)
