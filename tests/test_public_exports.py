import tomllib
from pathlib import Path

import cxp
import cxp.catalogs
import cxp.catalogs.interfaces
import cxp.catalogs.interfaces.cosecha.engine


def _assert_public_attr(module: object, symbol: str) -> None:
    assert hasattr(module, symbol)


def _assert_module_exports(module: object, symbol: str) -> None:
    _assert_public_attr(module, symbol)
    assert symbol in module.__all__


def test_asgi_lifespan_operations_are_exported_across_public_modules() -> None:
    lifespan_symbols = (
        "ASGI_APPLICATION_LIFESPAN_STARTUP_RECEIVE",
        "ASGI_APPLICATION_LIFESPAN_STARTUP_COMPLETE",
        "ASGI_APPLICATION_LIFESPAN_STARTUP_FAILED",
        "ASGI_APPLICATION_LIFESPAN_SHUTDOWN_RECEIVE",
        "ASGI_APPLICATION_LIFESPAN_SHUTDOWN_COMPLETE",
        "ASGI_APPLICATION_LIFESPAN_SHUTDOWN_FAILED",
    )

    for module in (cxp, cxp.catalogs, cxp.catalogs.interfaces):
        for symbol in lifespan_symbols:
            _assert_module_exports(module, symbol)


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
        "COSECHA_ENGINE_CATALOG",
        "COSECHA_ENGINE_INTERFACE",
        "COSECHA_ENGINE_LIFECYCLE",
        "COSECHA_ENGINE_TEST_LIFECYCLE",
        "COSECHA_ENGINE_PROJECT_DEFINITION_KNOWLEDGE",
        "COSECHA_ENGINE_LIBRARY_DEFINITION_KNOWLEDGE",
        "COSECHA_ENGINE_PROJECT_REGISTRY_KNOWLEDGE",
        "COSECHA_REPORTER_CATALOG",
        "COSECHA_REPORTER_INTERFACE",
        "COSECHA_REPORTER_STRUCTURED_OUTPUT",
        "COSECHA_REPORTER_HUMAN_OUTPUT",
        "COSECHA_PLUGIN_CATALOG",
        "COSECHA_PLUGIN_INTERFACE",
        "COSECHA_PLUGIN_TELEMETRY_SIDECAR_TIER",
        "COSECHA_PLUGIN_TIMING_SIDECAR_TIER",
        "COSECHA_RUNTIME_CATALOG",
        "COSECHA_RUNTIME_INTERFACE",
        "COSECHA_RUNTIME_LIVE_EXECUTION_OBSERVABILITY",
        "COSECHA_INSTRUMENTATION_CATALOG",
        "COSECHA_INSTRUMENTATION_COMPOSABLE_PROFILE",
        "COSECHA_INSTRUMENTATION_COMPOSABLE_PROFILE_NAME",
        "COSECHA_INSTRUMENTATION_COMPOSABLE_TIER",
        "COSECHA_INSTRUMENTATION_INTERFACE",
        "COSECHA_INSTRUMENTATION_STRUCTURED_SUMMARY",
        "BROWSER_AUTOMATION_CATALOG",
        "BROWSER_AUTOMATION_INTERFACE",
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
        "PLAN_RUN_EXECUTION_CORE_PROFILE",
        "PLAN_RUN_EXECUTION_CORE_PROFILE_NAME",
        "PLAN_RUN_EXECUTION_PLANNED_PROFILE",
        "PLAN_RUN_EXECUTION_PLANNED_PROFILE_NAME",
        "PLAN_RUN_EXECUTION_ADVANCED_PROFILE",
        "PLAN_RUN_EXECUTION_ADVANCED_PROFILE_NAME",
        "PLAN_RUN_EXECUTION_INTERFACE",
        "PLAN_RUN_EXECUTION_RUN",
        "PLAN_RUN_EXECUTION_PLANNING",
        "PLAN_RUN_EXECUTION_INPUT_VALIDATION",
        "PLAN_RUN_EXECUTION_EXECUTION_STATUS",
        "PLAN_RUN_EXECUTION_EXECUTION_STREAM",
        "PLAYWRIGHT_BROWSER_CATALOG",
        "PLAYWRIGHT_BROWSER_CORE_PROFILE",
        "PLAYWRIGHT_BROWSER_CORE_PROFILE_NAME",
        "PLAYWRIGHT_BROWSER_INTERFACE",
        "PLAYWRIGHT_BROWSER_OBSERVABLE_PROFILE",
        "PLAYWRIGHT_BROWSER_OBSERVABLE_PROFILE_NAME",
        "ASGI_APPLICATION_LIFESPAN_STARTUP_RECEIVE",
        "ASGI_APPLICATION_LIFESPAN_STARTUP_COMPLETE",
        "ASGI_APPLICATION_LIFESPAN_STARTUP_FAILED",
        "ASGI_APPLICATION_LIFESPAN_SHUTDOWN_RECEIVE",
        "ASGI_APPLICATION_LIFESPAN_SHUTDOWN_COMPLETE",
        "ASGI_APPLICATION_LIFESPAN_SHUTDOWN_FAILED",
        "MONGODB_TEXT_SEARCH_PROFILE",
        "MONGODB_TEXT_SEARCH_PROFILE_NAME",
    )
    interface_symbols = (
        "COSECHA_ENGINE_CATALOG",
        "COSECHA_ENGINE_INTERFACE",
        "COSECHA_ENGINE_LIFECYCLE",
        "COSECHA_ENGINE_TEST_LIFECYCLE",
        "COSECHA_ENGINE_PROJECT_DEFINITION_KNOWLEDGE",
        "COSECHA_ENGINE_LIBRARY_DEFINITION_KNOWLEDGE",
        "COSECHA_ENGINE_PROJECT_REGISTRY_KNOWLEDGE",
        "COSECHA_REPORTER_CATALOG",
        "COSECHA_REPORTER_INTERFACE",
        "COSECHA_REPORTER_STRUCTURED_OUTPUT",
        "COSECHA_REPORTER_HUMAN_OUTPUT",
        "COSECHA_PLUGIN_CATALOG",
        "COSECHA_PLUGIN_INTERFACE",
        "COSECHA_PLUGIN_TELEMETRY_SIDECAR_TIER",
        "COSECHA_PLUGIN_TIMING_SIDECAR_TIER",
        "COSECHA_RUNTIME_CATALOG",
        "COSECHA_RUNTIME_INTERFACE",
        "COSECHA_RUNTIME_LIVE_EXECUTION_OBSERVABILITY",
        "COSECHA_INSTRUMENTATION_CATALOG",
        "COSECHA_INSTRUMENTATION_COMPOSABLE_PROFILE",
        "COSECHA_INSTRUMENTATION_COMPOSABLE_PROFILE_NAME",
        "COSECHA_INSTRUMENTATION_COMPOSABLE_TIER",
        "COSECHA_INSTRUMENTATION_INTERFACE",
        "COSECHA_INSTRUMENTATION_STRUCTURED_SUMMARY",
        "BROWSER_AUTOMATION_CATALOG",
        "BROWSER_AUTOMATION_INTERFACE",
        "HTTP_APPLICATION_CATALOG",
        "HTTP_APPLICATION_INTERFACE",
        "HTTP_APPLICATION_FRAMEWORK_CATALOG",
        "HTTP_APPLICATION_FRAMEWORK_INTERFACE",
        "WSGI_APPLICATION_CATALOG",
        "WSGI_APPLICATION_INTERFACE",
        "ASGI_APPLICATION_CATALOG",
        "ASGI_APPLICATION_INTERFACE",
        "ASGI_APPLICATION_LIFESPAN_STARTUP_RECEIVE",
        "ASGI_APPLICATION_LIFESPAN_STARTUP_COMPLETE",
        "ASGI_APPLICATION_LIFESPAN_STARTUP_FAILED",
        "ASGI_APPLICATION_LIFESPAN_SHUTDOWN_RECEIVE",
        "ASGI_APPLICATION_LIFESPAN_SHUTDOWN_COMPLETE",
        "ASGI_APPLICATION_LIFESPAN_SHUTDOWN_FAILED",
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
        "PLAN_RUN_EXECUTION_CORE_PROFILE",
        "PLAN_RUN_EXECUTION_CORE_PROFILE_NAME",
        "PLAN_RUN_EXECUTION_PLANNED_PROFILE",
        "PLAN_RUN_EXECUTION_PLANNED_PROFILE_NAME",
        "PLAN_RUN_EXECUTION_ADVANCED_PROFILE",
        "PLAN_RUN_EXECUTION_ADVANCED_PROFILE_NAME",
        "PLAN_RUN_EXECUTION_INTERFACE",
        "PLAN_RUN_EXECUTION_RUN",
        "PLAN_RUN_EXECUTION_PLANNING",
        "PLAN_RUN_EXECUTION_INPUT_VALIDATION",
        "PLAN_RUN_EXECUTION_EXECUTION_STATUS",
        "PLAN_RUN_EXECUTION_EXECUTION_STREAM",
        "PLAYWRIGHT_BROWSER_CATALOG",
        "PLAYWRIGHT_BROWSER_CORE_PROFILE",
        "PLAYWRIGHT_BROWSER_CORE_PROFILE_NAME",
        "PLAYWRIGHT_BROWSER_INTERFACE",
        "PLAYWRIGHT_BROWSER_OBSERVABLE_PROFILE",
        "PLAYWRIGHT_BROWSER_OBSERVABLE_PROFILE_NAME",
        "MONGODB_TEXT_SEARCH_PROFILE",
        "MONGODB_TEXT_SEARCH_PROFILE_NAME",
    )

    for module in (cxp, cxp.catalogs):
        for symbol in root_and_catalog_symbols:
            _assert_public_attr(module, symbol)

    for symbol in interface_symbols:
        _assert_module_exports(cxp.catalogs.interfaces, symbol)


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


def test_legacy_execution_engine_symbols_are_not_exported_by_submodules() -> None:
    import cxp.catalogs.interfaces.execution
    import cxp.catalogs.interfaces.execution.engine

    for module in (
        cxp.catalogs.interfaces.execution,
        cxp.catalogs.interfaces.execution.engine,
    ):
        assert hasattr(module, "EXECUTION_ENGINE_DRAFT_VALIDATION") is False
        assert (
            hasattr(module, "EXECUTION_ENGINE_LIVE_EXECUTION_OBSERVABILITY")
            is False
        )


def test_package_version_matches_project_metadata() -> None:
    pyproject = Path(__file__).resolve().parent.parent / "pyproject.toml"
    project = tomllib.loads(pyproject.read_text(encoding="utf-8"))["project"]
    dynamic = tomllib.loads(pyproject.read_text(encoding="utf-8"))["tool"][
        "setuptools"
    ]["dynamic"]

    assert project["dynamic"] == ["version"]
    assert dynamic["version"]["attr"] == "cxp._version.__version__"
    assert cxp.__version__ == "3.1.0"


def test_cosecha_engine_module_all_includes_lifecycle_capabilities() -> None:
    assert (
        "COSECHA_ENGINE_LIFECYCLE"
        in cxp.catalogs.interfaces.cosecha.engine.__all__
    )
    assert (
        "COSECHA_ENGINE_TEST_LIFECYCLE"
        in cxp.catalogs.interfaces.cosecha.engine.__all__
    )


def test_compliance_bridge_symbols_are_exported_from_root_package() -> None:
    for symbol in (
        "CatalogComplianceReport",
        "NegotiatedCatalogDecision",
        "evaluate_capability_matrix_against_catalog",
        "evaluate_handshake_response_against_catalog",
        "negotiate_with_provider_catalog_report",
        "negotiate_with_async_provider_catalog_report",
    ):
        _assert_module_exports(cxp, symbol)
