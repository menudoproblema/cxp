from cxp.catalogs.base import (
    CapabilityCatalog,
    CatalogCapability,
    ConformanceTier,
    register_catalog,
)

HTTP_APPLICATION_FRAMEWORK_INTERFACE = "application/http-framework"

HTTP_APPLICATION_FRAMEWORK_ROUTING = "routing"
HTTP_APPLICATION_FRAMEWORK_SCHEMA_VALIDATION = "schema_validation"
HTTP_APPLICATION_FRAMEWORK_DEPENDENCY_INJECTION = "dependency_injection"
HTTP_APPLICATION_FRAMEWORK_AUTH_PROCESSING = "auth_processing"

HTTP_APPLICATION_FRAMEWORK_CORE_TIER = "core"

HTTP_APPLICATION_FRAMEWORK_CATALOG = register_catalog(
    CapabilityCatalog(
        interface=HTTP_APPLICATION_FRAMEWORK_INTERFACE,
        description=(
            "Canonical catalog for high-level HTTP framework semantics."
        ),
        capabilities=(
            CatalogCapability(name=HTTP_APPLICATION_FRAMEWORK_ROUTING),
            CatalogCapability(name=HTTP_APPLICATION_FRAMEWORK_SCHEMA_VALIDATION),
            CatalogCapability(name=HTTP_APPLICATION_FRAMEWORK_DEPENDENCY_INJECTION),
            CatalogCapability(name=HTTP_APPLICATION_FRAMEWORK_AUTH_PROCESSING),
        ),
        tiers=(
            ConformanceTier(
                name=HTTP_APPLICATION_FRAMEWORK_CORE_TIER,
                required_capabilities=(
                    HTTP_APPLICATION_FRAMEWORK_ROUTING,
                    HTTP_APPLICATION_FRAMEWORK_SCHEMA_VALIDATION,
                ),
                description="HTTP application with routing and schema validation.",
            ),
        ),
    )
)

__all__ = (
    "HTTP_APPLICATION_FRAMEWORK_AUTH_PROCESSING",
    "HTTP_APPLICATION_FRAMEWORK_CATALOG",
    "HTTP_APPLICATION_FRAMEWORK_CORE_TIER",
    "HTTP_APPLICATION_FRAMEWORK_DEPENDENCY_INJECTION",
    "HTTP_APPLICATION_FRAMEWORK_INTERFACE",
    "HTTP_APPLICATION_FRAMEWORK_ROUTING",
    "HTTP_APPLICATION_FRAMEWORK_SCHEMA_VALIDATION",
)
