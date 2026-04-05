import cxp
import cxp.catalogs
import cxp.catalogs.interfaces


def test_family_and_concrete_catalog_symbols_are_publicly_exported() -> None:
    root_and_catalog_symbols = (
        "catalog_satisfies_interface",
        "CapabilityProfileDefinitionValidationResult",
        "CapabilityTelemetry",
        "TelemetryFieldRequirement",
        "TelemetrySpanSpec",
        "TelemetryMetricSpec",
        "TelemetryEventSpec",
        "TelemetryValidationResult",
        "HTTP_APPLICATION_CATALOG",
        "HTTP_APPLICATION_INTERFACE",
        "HTTP_APPLICATION_FRAMEWORK_CATALOG",
        "HTTP_APPLICATION_FRAMEWORK_INTERFACE",
        "WSGI_APPLICATION_CATALOG",
        "WSGI_APPLICATION_INTERFACE",
        "ASGI_APPLICATION_CATALOG",
        "ASGI_APPLICATION_INTERFACE",
        "EXECUTION_ENGINE_CATALOG",
        "EXECUTION_ENGINE_EXECUTION_STATUS",
        "EXECUTION_ENGINE_EXECUTION_STREAM",
        "EXECUTION_ENGINE_FAMILY_CATALOG",
        "EXECUTION_ENGINE_FAMILY_INTERFACE",
        "EXECUTION_ENGINE_INPUT_VALIDATION",
        "EXECUTION_ENGINE_INTERFACE",
        "EXECUTION_ENGINE_PLANNING",
        "EXECUTION_ENGINE_RUN",
        "PLAN_RUN_EXECUTION_CATALOG",
        "PLAN_RUN_EXECUTION_INTERFACE",
        "PLAN_RUN_EXECUTION_RUN",
        "PLAN_RUN_EXECUTION_PLANNING",
        "PLAN_RUN_EXECUTION_INPUT_VALIDATION",
        "PLAN_RUN_EXECUTION_EXECUTION_STATUS",
        "PLAN_RUN_EXECUTION_EXECUTION_STREAM",
    )
    interface_symbols = (
        "HTTP_APPLICATION_CATALOG",
        "HTTP_APPLICATION_INTERFACE",
        "HTTP_APPLICATION_FRAMEWORK_CATALOG",
        "HTTP_APPLICATION_FRAMEWORK_INTERFACE",
        "WSGI_APPLICATION_CATALOG",
        "WSGI_APPLICATION_INTERFACE",
        "ASGI_APPLICATION_CATALOG",
        "ASGI_APPLICATION_INTERFACE",
        "EXECUTION_ENGINE_CATALOG",
        "EXECUTION_ENGINE_EXECUTION_STATUS",
        "EXECUTION_ENGINE_EXECUTION_STREAM",
        "EXECUTION_ENGINE_FAMILY_CATALOG",
        "EXECUTION_ENGINE_FAMILY_INTERFACE",
        "EXECUTION_ENGINE_INPUT_VALIDATION",
        "EXECUTION_ENGINE_INTERFACE",
        "EXECUTION_ENGINE_PLANNING",
        "EXECUTION_ENGINE_RUN",
        "PLAN_RUN_EXECUTION_CATALOG",
        "PLAN_RUN_EXECUTION_INTERFACE",
        "PLAN_RUN_EXECUTION_RUN",
        "PLAN_RUN_EXECUTION_PLANNING",
        "PLAN_RUN_EXECUTION_INPUT_VALIDATION",
        "PLAN_RUN_EXECUTION_EXECUTION_STATUS",
        "PLAN_RUN_EXECUTION_EXECUTION_STREAM",
    )

    for module in (cxp, cxp.catalogs):
        for symbol in root_and_catalog_symbols:
            assert hasattr(module, symbol)

    for symbol in interface_symbols:
        assert hasattr(cxp.catalogs.interfaces, symbol)


def test_legacy_http_application_symbols_are_no_longer_exported() -> None:
    legacy_symbols = (
        "HTTP_APPLICATION_ROUTING",
        "HTTP_APPLICATION_SCHEMA_VALIDATION",
        "HTTP_APPLICATION_DEPENDENCY_INJECTION",
        "HTTP_APPLICATION_AUTH_PROCESSING",
    )

    for module in (cxp, cxp.catalogs, cxp.catalogs.interfaces):
        for symbol in legacy_symbols:
            assert hasattr(module, symbol) is False


def test_legacy_execution_engine_symbols_are_no_longer_exported() -> None:
    legacy_symbols = (
        "EXECUTION_ENGINE_DRAFT_VALIDATION",
        "EXECUTION_ENGINE_LIVE_EXECUTION_OBSERVABILITY",
    )

    for module in (cxp, cxp.catalogs, cxp.catalogs.interfaces):
        for symbol in legacy_symbols:
            assert hasattr(module, symbol) is False
