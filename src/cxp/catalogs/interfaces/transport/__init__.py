from __future__ import annotations

from cxp.catalogs.base import (
    CapabilityCatalog,
    CatalogCapability,
    ConformanceTier,
    register_catalog,
)

HTTP_TRANSPORT_INTERFACE = "transport/http"

HTTP_TRANSPORT_HEADERS = "headers"
HTTP_TRANSPORT_COOKIES = "cookies"
HTTP_TRANSPORT_AUTH_PROPAGATION = "auth_propagation"
HTTP_TRANSPORT_MIDDLEWARE_OBSERVABLE = "middleware_observable"
HTTP_TRANSPORT_STREAMING = "streaming"
HTTP_TRANSPORT_NETWORK_TRANSPORT = "network_transport"

HTTP_TRANSPORT_CORE_TIER = "core"

HTTP_TRANSPORT_CATALOG = register_catalog(
    CapabilityCatalog(
        interface=HTTP_TRANSPORT_INTERFACE,
        description="Canonical catalog for HTTP transport.",
        capabilities=(
            CatalogCapability(name=HTTP_TRANSPORT_HEADERS),
            CatalogCapability(name=HTTP_TRANSPORT_COOKIES),
            CatalogCapability(name=HTTP_TRANSPORT_AUTH_PROPAGATION),
            CatalogCapability(name=HTTP_TRANSPORT_MIDDLEWARE_OBSERVABLE),
            CatalogCapability(name=HTTP_TRANSPORT_STREAMING),
            CatalogCapability(name=HTTP_TRANSPORT_NETWORK_TRANSPORT),
        ),
        tiers=(
            ConformanceTier(
                name=HTTP_TRANSPORT_CORE_TIER,
                required_capabilities=(
                    HTTP_TRANSPORT_HEADERS,
                    HTTP_TRANSPORT_NETWORK_TRANSPORT,
                ),
                description="Basic interoperable HTTP transport.",
            ),
        ),
    )
)

__all__ = (
    "HTTP_TRANSPORT_AUTH_PROPAGATION",
    "HTTP_TRANSPORT_CATALOG",
    "HTTP_TRANSPORT_COOKIES",
    "HTTP_TRANSPORT_CORE_TIER",
    "HTTP_TRANSPORT_HEADERS",
    "HTTP_TRANSPORT_INTERFACE",
    "HTTP_TRANSPORT_MIDDLEWARE_OBSERVABLE",
    "HTTP_TRANSPORT_NETWORK_TRANSPORT",
    "HTTP_TRANSPORT_STREAMING",
)
