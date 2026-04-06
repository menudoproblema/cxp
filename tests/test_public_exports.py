import tomllib
from pathlib import Path

import cxp
import cxp.catalogs
import cxp.catalogs.interfaces
import cxp.catalogs.interfaces.cosecha.engine


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
        "COSECHA_REPORTER_CATALOG",
        "COSECHA_REPORTER_INTERFACE",
        "COSECHA_PLUGIN_CATALOG",
        "COSECHA_PLUGIN_INTERFACE",
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
        "MONGODB_TEXT_SEARCH_PROFILE",
        "MONGODB_TEXT_SEARCH_PROFILE_NAME",
    )
    interface_symbols = (
        "COSECHA_ENGINE_CATALOG",
        "COSECHA_ENGINE_INTERFACE",
        "COSECHA_ENGINE_LIFECYCLE",
        "COSECHA_ENGINE_TEST_LIFECYCLE",
        "COSECHA_REPORTER_CATALOG",
        "COSECHA_REPORTER_INTERFACE",
        "COSECHA_PLUGIN_CATALOG",
        "COSECHA_PLUGIN_INTERFACE",
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
        "MONGODB_TEXT_SEARCH_PROFILE",
        "MONGODB_TEXT_SEARCH_PROFILE_NAME",
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

    assert cxp.__version__ == project["version"]


def test_cosecha_engine_module_all_includes_lifecycle_capabilities() -> None:
    assert (
        "COSECHA_ENGINE_LIFECYCLE"
        in cxp.catalogs.interfaces.cosecha.engine.__all__
    )
    assert (
        "COSECHA_ENGINE_TEST_LIFECYCLE"
        in cxp.catalogs.interfaces.cosecha.engine.__all__
    )
