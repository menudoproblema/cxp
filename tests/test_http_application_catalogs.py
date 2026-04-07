from pytest import raises

from cxp import (
    ASGI_APPLICATION_CATALOG,
    ASGI_APPLICATION_HTTP_CORE_PROFILE,
    ASGI_APPLICATION_INTERFACE,
    ASGI_APPLICATION_LIFESPAN,
    ASGI_APPLICATION_LIFESPAN_PROFILE,
    ASGI_APPLICATION_REALTIME_PROFILE,
    ASGI_APPLICATION_WEB_CORE_PROFILE,
    ASGI_APPLICATION_WEBSOCKET,
    ASGI_APPLICATION_WEBSOCKET_ACCEPT,
    ASGI_APPLICATION_WEBSOCKET_CLOSE,
    ASGI_APPLICATION_WEBSOCKET_CONNECT_RECEIVE,
    ASGI_APPLICATION_WEBSOCKET_DISCONNECT_RECEIVE,
    ASGI_APPLICATION_WEBSOCKET_RECEIVE,
    ASGI_APPLICATION_WEBSOCKET_SCOPE_INSPECT,
    ASGI_APPLICATION_WEBSOCKET_SEND,
    HTTP_APPLICATION_CATALOG,
    HTTP_APPLICATION_FRAMEWORK_CATALOG,
    WSGI_APPLICATION_CATALOG,
    WSGI_APPLICATION_CORE_PROFILE,
    WSGI_APPLICATION_FILE_WRAPPER_PROFILE,
    WSGI_APPLICATION_INTERFACE,
    Capability,
    CapabilityCatalog,
    CapabilityDescriptor,
    CapabilityMatrix,
    CapabilityOperationBinding,
    CatalogRegistry,
    ComponentCapabilitySnapshot,
    ComponentIdentity,
    HandshakeRequest,
    catalog_satisfies_interface,
    get_catalog,
    negotiate_capabilities,
)


def test_application_family_catalogs_are_registered() -> None:
    assert get_catalog("application/http") is HTTP_APPLICATION_CATALOG
    assert (
        get_catalog("application/http-framework")
        is HTTP_APPLICATION_FRAMEWORK_CATALOG
    )
    assert get_catalog("application/wsgi") is WSGI_APPLICATION_CATALOG
    assert get_catalog("application/asgi") is ASGI_APPLICATION_CATALOG


def test_application_family_catalog_is_abstract() -> None:
    with raises(ValueError, match="Abstract catalog"):
        HTTP_APPLICATION_CATALOG.validate_capability_matrix(CapabilityMatrix())


def test_catalog_hierarchy_reports_http_family_compatibility() -> None:
    assert catalog_satisfies_interface("application/asgi", "application/http")
    assert catalog_satisfies_interface("application/wsgi", "application/http")
    assert catalog_satisfies_interface("application/http", "application/asgi") is False
    assert catalog_satisfies_interface("application/wsgi", "application/asgi") is False


def test_handshake_accepts_concrete_http_application_for_abstract_family() -> None:
    request = HandshakeRequest(
        client_identity=ComponentIdentity(
            interface="application/http",
            provider="cosecha",
            version="1.0.0",
        ),
        required_capabilities=(),
    )
    provider_identity = ComponentIdentity(
        interface="application/asgi",
        provider="users-app",
        version="1.0.0",
    )

    response = negotiate_capabilities(
        request,
        provider_identity,
        CapabilityMatrix(),
    )

    assert response.status == "accepted"


def test_handshake_rejects_incompatible_http_application_protocols() -> None:
    request = HandshakeRequest(
        client_identity=ComponentIdentity(
            interface=ASGI_APPLICATION_INTERFACE,
            provider="cosecha",
            version="1.0.0",
        ),
        required_capabilities=(),
    )
    provider_identity = ComponentIdentity(
        interface=WSGI_APPLICATION_INTERFACE,
        provider="legacy-app",
        version="1.0.0",
    )

    response = negotiate_capabilities(
        request,
        provider_identity,
        CapabilityMatrix(),
    )

    assert response.status == "rejected"
    assert response.reason is not None
    assert "Interface mismatch" in response.reason


def test_handshake_keeps_exact_match_for_uncataloged_interfaces() -> None:
    request = HandshakeRequest(
        client_identity=ComponentIdentity(
            interface="custom/http-app",
            provider="cosecha",
            version="1.0.0",
        ),
        required_capabilities=(),
    )
    provider_identity = ComponentIdentity(
        interface="custom/http-family",
        provider="users-app",
        version="1.0.0",
    )

    response = negotiate_capabilities(
        request,
        provider_identity,
        CapabilityMatrix(),
    )

    assert response.status == "rejected"


def test_registry_rejects_unknown_or_cyclic_interface_hierarchy() -> None:
    registry = CatalogRegistry(
        catalogs=(
            CapabilityCatalog(
                interface="application/http",
                abstract=True,
            ),
        )
    )

    with raises(ValueError, match="unknown satisfied interface"):
        registry.register(
            CapabilityCatalog(
                interface="application/asgi",
                satisfies_interfaces=("application/missing",),
            )
        )

    registry.register(
        CapabilityCatalog(
            interface="application/asgi",
            satisfies_interfaces=("application/http",),
        )
    )

    with raises(ValueError, match="cannot contain cycles"):
        registry.register(
            CapabilityCatalog(
                interface="application/http",
                abstract=True,
                satisfies_interfaces=("application/asgi",),
            ),
            replace=True,
        )


def test_wsgi_profiles_validate_complete_snapshot() -> None:
    snapshot = ComponentCapabilitySnapshot(
        component_name="legacy-app",
        capabilities=(
            CapabilityDescriptor(
                name="http",
                level="supported",
                operations=(
                    CapabilityOperationBinding("request.environ.inspect"),
                    CapabilityOperationBinding("request.body.read"),
                    CapabilityOperationBinding("response.start"),
                    CapabilityOperationBinding("response.body.iterable"),
                    CapabilityOperationBinding("response.body.write"),
                ),
                metadata={
                    "specVersion": "1.0.1",
                    "urlSchemes": ("http", "https"),
                    "mountAware": True,
                    "expectContinue": False,
                    "concurrencyHints": ("multi_thread",),
                },
            ),
            CapabilityDescriptor(
                name="file_wrapper",
                level="supported",
                operations=(
                    CapabilityOperationBinding("response.body.file_wrapper"),
                ),
            ),
        ),
    )

    assert WSGI_APPLICATION_CATALOG.is_component_snapshot_profile_compliant(
        snapshot,
        WSGI_APPLICATION_CORE_PROFILE,
    )
    assert WSGI_APPLICATION_CATALOG.is_component_snapshot_profile_compliant(
        snapshot,
        WSGI_APPLICATION_FILE_WRAPPER_PROFILE,
    )


def test_asgi_profiles_validate_http_lifespan_and_websocket() -> None:
    snapshot = ComponentCapabilitySnapshot(
        component_name="realtime-app",
        identity=ComponentIdentity(
            interface=ASGI_APPLICATION_INTERFACE,
            provider="realtime-app",
            version="1.0.0",
        ),
        capabilities=(
            CapabilityDescriptor(
                name="http",
                level="supported",
                operations=(
                    CapabilityOperationBinding("http.scope.inspect"),
                    CapabilityOperationBinding("http.request.receive"),
                    CapabilityOperationBinding("http.disconnect.receive"),
                    CapabilityOperationBinding("http.response.start"),
                    CapabilityOperationBinding("http.response.body"),
                ),
                metadata={
                    "specVersion": "2.3",
                    "httpVersions": ("1.1", "2"),
                },
            ),
            CapabilityDescriptor(
                name=ASGI_APPLICATION_LIFESPAN,
                level="supported",
                operations=(
                    CapabilityOperationBinding("lifespan.scope.inspect"),
                    CapabilityOperationBinding("lifespan.startup.receive"),
                    CapabilityOperationBinding("lifespan.startup.complete"),
                    CapabilityOperationBinding("lifespan.startup.failed"),
                    CapabilityOperationBinding("lifespan.shutdown.receive"),
                    CapabilityOperationBinding("lifespan.shutdown.complete"),
                    CapabilityOperationBinding("lifespan.shutdown.failed"),
                ),
                metadata={"specVersion": "2.0"},
            ),
            CapabilityDescriptor(
                name=ASGI_APPLICATION_WEBSOCKET,
                level="supported",
                operations=(
                    CapabilityOperationBinding(ASGI_APPLICATION_WEBSOCKET_SCOPE_INSPECT),
                    CapabilityOperationBinding(ASGI_APPLICATION_WEBSOCKET_CONNECT_RECEIVE),
                    CapabilityOperationBinding(ASGI_APPLICATION_WEBSOCKET_ACCEPT),
                    CapabilityOperationBinding(ASGI_APPLICATION_WEBSOCKET_RECEIVE),
                    CapabilityOperationBinding(ASGI_APPLICATION_WEBSOCKET_SEND),
                    CapabilityOperationBinding(ASGI_APPLICATION_WEBSOCKET_CLOSE),
                    CapabilityOperationBinding(
                        ASGI_APPLICATION_WEBSOCKET_DISCONNECT_RECEIVE
                    ),
                ),
                metadata={
                    "specVersion": "2.3",
                    "subprotocols": ("chat.v1",),
                },
            ),
        ),
    )

    assert ASGI_APPLICATION_CATALOG.is_component_snapshot_profile_compliant(
        snapshot,
        ASGI_APPLICATION_HTTP_CORE_PROFILE,
    )
    assert ASGI_APPLICATION_CATALOG.is_component_snapshot_profile_compliant(
        snapshot,
        ASGI_APPLICATION_LIFESPAN_PROFILE,
    )
    assert ASGI_APPLICATION_CATALOG.is_component_snapshot_profile_compliant(
        snapshot,
        ASGI_APPLICATION_WEB_CORE_PROFILE,
    )
    assert ASGI_APPLICATION_CATALOG.is_component_snapshot_profile_compliant(
        snapshot,
        ASGI_APPLICATION_REALTIME_PROFILE,
    )


def test_asgi_catalog_validates_realtime_tier() -> None:
    validation = ASGI_APPLICATION_CATALOG.validate_capability_matrix(
        CapabilityMatrix(
            capabilities=(
                Capability(name="http"),
                Capability(name="lifespan"),
                Capability(name="websocket"),
            ),
        ),
        required_tier="realtime",
        validate_metadata=False,
    )

    assert validation.is_valid() is True
