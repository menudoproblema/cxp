import cxp
import cxp.catalogs
import cxp.catalogs.interfaces


def test_http_application_family_symbols_are_publicly_exported() -> None:
    root_and_catalog_symbols = (
        "catalog_satisfies_interface",
        "CapabilityProfileDefinitionValidationResult",
        "HTTP_APPLICATION_CATALOG",
        "HTTP_APPLICATION_INTERFACE",
        "HTTP_APPLICATION_FRAMEWORK_CATALOG",
        "HTTP_APPLICATION_FRAMEWORK_INTERFACE",
        "WSGI_APPLICATION_CATALOG",
        "WSGI_APPLICATION_INTERFACE",
        "ASGI_APPLICATION_CATALOG",
        "ASGI_APPLICATION_INTERFACE",
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
