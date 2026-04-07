from __future__ import annotations

from cxp.catalogs.base import (
    CapabilityCatalog,
    CatalogCapability,
    CatalogOperation,
    ConformanceTier,
    register_catalog,
)
from cxp.catalogs.results import HttpResponse, TlsCertificate
from cxp.catalogs.inputs import HttpDispatch

HTTP_TRANSPORT_INTERFACE = "transport/http"
HTTP_TRANSPORT_FAMILY_INTERFACE = "transport/http-family"

# Base Operations
HTTP_OP_SEND = "http.send"
HTTP_OP_GET_CERT = "http.get_certificate"

HTTP_TRANSPORT_FAMILY_CATALOG = register_catalog(
    CapabilityCatalog(
        interface=HTTP_TRANSPORT_FAMILY_INTERFACE,
        abstract=True,
        description="Abstract base for all HTTP transport versions, including security and streaming.",
        capabilities=(
            CatalogCapability(
                name="request_dispatch",
                description="Atomic sending of HTTP requests.",
                operations=(
                    CatalogOperation(
                        name=HTTP_OP_SEND,
                        input_schema=HttpDispatch, # Input validation
                        result_type="http.response",
                        result_schema=HttpResponse,
                        idempotent=False,
                        timeout_seconds=60.0,
                    ),
                ),
            ),
            CatalogCapability(
                name="tls",
                description="Transport Layer Security (SSL/TLS).",
                operations=(
                    CatalogOperation(
                        name=HTTP_OP_GET_CERT,
                        result_type="security.certificate",
                        result_schema=TlsCertificate,
                        idempotent=True,
                    ),
                ),
            ),
        ),
        tiers=(
            ConformanceTier(
                name="core",
                required_capabilities=("request_dispatch",),
            ),
        ),
    ),
    replace=True,
)

__all__ = (
    "HTTP_TRANSPORT_FAMILY_CATALOG",
    "HTTP_TRANSPORT_FAMILY_INTERFACE",
    "HTTP_TRANSPORT_INTERFACE",
    "HTTP_OP_SEND",
)
