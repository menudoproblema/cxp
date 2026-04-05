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

WSGI_APPLICATION_INTERFACE = "application/wsgi"

WSGI_APPLICATION_HTTP = "http"
WSGI_APPLICATION_FILE_WRAPPER = "file_wrapper"

WSGI_APPLICATION_REQUEST_ENVIRON_INSPECT = "request.environ.inspect"
WSGI_APPLICATION_REQUEST_BODY_READ = "request.body.read"
WSGI_APPLICATION_RESPONSE_START = "response.start"
WSGI_APPLICATION_RESPONSE_BODY_ITERABLE = "response.body.iterable"
WSGI_APPLICATION_RESPONSE_BODY_WRITE = "response.body.write"
WSGI_APPLICATION_RESPONSE_BODY_FILE_WRAPPER = "response.body.file_wrapper"

WSGI_APPLICATION_CORE_TIER = "core"
WSGI_APPLICATION_OPTIMIZED_TIER = "optimized"

WSGI_APPLICATION_CORE_PROFILE_NAME = "wsgi-core"
WSGI_APPLICATION_FILE_WRAPPER_PROFILE_NAME = "wsgi-file-optimized"


class WsgiHttpMetadata(msgspec.Struct, frozen=True):
    specVersion: str
    urlSchemes: tuple[str, ...]
    mountAware: bool
    expectContinue: bool
    concurrencyHints: tuple[str, ...]


WSGI_APPLICATION_CATALOG = register_catalog(
    CapabilityCatalog(
        interface=WSGI_APPLICATION_INTERFACE,
        description="Canonical catalog for WSGI-compatible applications.",
        satisfies_interfaces=(HTTP_APPLICATION_INTERFACE,),
        capabilities=(
            CatalogCapability(
                name=WSGI_APPLICATION_HTTP,
                description="Synchronous WSGI application HTTP contract.",
                operations=(
                    CatalogOperation(
                        name=WSGI_APPLICATION_REQUEST_ENVIRON_INSPECT,
                        result_type="request.environ",
                    ),
                    CatalogOperation(
                        name=WSGI_APPLICATION_REQUEST_BODY_READ,
                        result_type="request.body",
                    ),
                    CatalogOperation(
                        name=WSGI_APPLICATION_RESPONSE_START,
                        result_type="response.started",
                    ),
                    CatalogOperation(
                        name=WSGI_APPLICATION_RESPONSE_BODY_ITERABLE,
                        result_type="response.body.iterable",
                    ),
                    CatalogOperation(
                        name=WSGI_APPLICATION_RESPONSE_BODY_WRITE,
                        result_type="response.body.write",
                    ),
                ),
                metadata_schema=WsgiHttpMetadata,
            ),
            CatalogCapability(
                name=WSGI_APPLICATION_FILE_WRAPPER,
                description="Optional optimization via wsgi.file_wrapper.",
                operations=(
                    CatalogOperation(
                        name=WSGI_APPLICATION_RESPONSE_BODY_FILE_WRAPPER,
                        result_type="response.body.file_wrapper",
                    ),
                ),
            ),
        ),
        tiers=(
            ConformanceTier(
                name=WSGI_APPLICATION_CORE_TIER,
                required_capabilities=(WSGI_APPLICATION_HTTP,),
                description="Basic interoperable WSGI application.",
            ),
            ConformanceTier(
                name=WSGI_APPLICATION_OPTIMIZED_TIER,
                required_capabilities=(
                    WSGI_APPLICATION_HTTP,
                    WSGI_APPLICATION_FILE_WRAPPER,
                ),
                description="WSGI application with file_wrapper optimization.",
            ),
        ),
    )
)

WSGI_APPLICATION_CORE_PROFILE = CapabilityProfile(
    name=WSGI_APPLICATION_CORE_PROFILE_NAME,
    interface=WSGI_APPLICATION_INTERFACE,
    description="Base profile for complete WSGI HTTP applications.",
    requirements=(
        CapabilityRequirement(
            capability_name=WSGI_APPLICATION_HTTP,
            required_operations=(
                WSGI_APPLICATION_REQUEST_ENVIRON_INSPECT,
                WSGI_APPLICATION_REQUEST_BODY_READ,
                WSGI_APPLICATION_RESPONSE_START,
                WSGI_APPLICATION_RESPONSE_BODY_ITERABLE,
                WSGI_APPLICATION_RESPONSE_BODY_WRITE,
            ),
            required_metadata_keys=(
                "specVersion",
                "urlSchemes",
                "mountAware",
                "expectContinue",
                "concurrencyHints",
            ),
        ),
    ),
)

WSGI_APPLICATION_FILE_WRAPPER_PROFILE = CapabilityProfile(
    name=WSGI_APPLICATION_FILE_WRAPPER_PROFILE_NAME,
    interface=WSGI_APPLICATION_INTERFACE,
    description="Optimized WSGI profile with file_wrapper support.",
    requirements=(
        *WSGI_APPLICATION_CORE_PROFILE.requirements,
        CapabilityRequirement(
            capability_name=WSGI_APPLICATION_FILE_WRAPPER,
            required_operations=(WSGI_APPLICATION_RESPONSE_BODY_FILE_WRAPPER,),
        ),
    ),
)

__all__ = (
    "WSGI_APPLICATION_CATALOG",
    "WSGI_APPLICATION_CORE_PROFILE",
    "WSGI_APPLICATION_CORE_PROFILE_NAME",
    "WSGI_APPLICATION_CORE_TIER",
    "WSGI_APPLICATION_FILE_WRAPPER",
    "WSGI_APPLICATION_FILE_WRAPPER_PROFILE",
    "WSGI_APPLICATION_FILE_WRAPPER_PROFILE_NAME",
    "WSGI_APPLICATION_HTTP",
    "WSGI_APPLICATION_INTERFACE",
    "WSGI_APPLICATION_OPTIMIZED_TIER",
    "WSGI_APPLICATION_REQUEST_BODY_READ",
    "WSGI_APPLICATION_REQUEST_ENVIRON_INSPECT",
    "WSGI_APPLICATION_RESPONSE_BODY_FILE_WRAPPER",
    "WSGI_APPLICATION_RESPONSE_BODY_ITERABLE",
    "WSGI_APPLICATION_RESPONSE_BODY_WRITE",
    "WSGI_APPLICATION_RESPONSE_START",
)
