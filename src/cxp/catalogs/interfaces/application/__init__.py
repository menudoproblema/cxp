from __future__ import annotations

from cxp.catalogs.base import (
    CapabilityCatalog,
    CatalogCapability,
    ConformanceTier,
    register_catalog,
)

HTTP_APPLICATION_INTERFACE = "application/http"

HTTP_APPLICATION_ROUTING = "routing"
HTTP_APPLICATION_SCHEMA_VALIDATION = "schema_validation"
HTTP_APPLICATION_DEPENDENCY_INJECTION = "dependency_injection"
HTTP_APPLICATION_AUTH_PROCESSING = "auth_processing"

HTTP_APPLICATION_CATALOG = register_catalog(
    CapabilityCatalog(
        interface=HTTP_APPLICATION_INTERFACE,
        description="Catálogo canónico para aplicaciones HTTP.",
        capabilities=(
            CatalogCapability(name=HTTP_APPLICATION_ROUTING),
            CatalogCapability(name=HTTP_APPLICATION_SCHEMA_VALIDATION),
            CatalogCapability(name=HTTP_APPLICATION_DEPENDENCY_INJECTION),
            CatalogCapability(name=HTTP_APPLICATION_AUTH_PROCESSING),
        ),
        tiers=(
            ConformanceTier(
                name="core",
                required_capabilities=(
                    HTTP_APPLICATION_ROUTING,
                    HTTP_APPLICATION_SCHEMA_VALIDATION,
                ),
                description="Aplicación HTTP con routing y validación de schema.",
            ),
        ),
    )
)

__all__ = (
    "HTTP_APPLICATION_AUTH_PROCESSING",
    "HTTP_APPLICATION_CATALOG",
    "HTTP_APPLICATION_DEPENDENCY_INJECTION",
    "HTTP_APPLICATION_INTERFACE",
    "HTTP_APPLICATION_ROUTING",
    "HTTP_APPLICATION_SCHEMA_VALIDATION",
)
