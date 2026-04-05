from pytest import raises

from cxp import (
    BROWSER_AUTOMATION_CATALOG,
    BROWSER_AUTOMATION_INTERFACE,
    PLAYWRIGHT_BROWSER_CATALOG,
    PLAYWRIGHT_BROWSER_CONTEXT_MANAGEMENT,
    PLAYWRIGHT_BROWSER_CORE_TIER,
    PLAYWRIGHT_BROWSER_DIALOG_HANDLING,
    PLAYWRIGHT_BROWSER_DOM_INTERACTION,
    PLAYWRIGHT_BROWSER_INTERFACE,
    PLAYWRIGHT_BROWSER_LIFECYCLE,
    PLAYWRIGHT_BROWSER_NETWORK_OBSERVATION,
    PLAYWRIGHT_BROWSER_OBSERVABLE_TIER,
    PLAYWRIGHT_BROWSER_PAGE_GOTO,
    PLAYWRIGHT_BROWSER_PAGE_NAVIGATION,
    PLAYWRIGHT_BROWSER_SCREENSHOT_CAPTURE,
    PLAYWRIGHT_BROWSER_SCRIPT_EVALUATION,
    PLAYWRIGHT_BROWSER_WAIT_CONDITIONS,
    CapabilityCatalog,
    CapabilityMatrix,
    CatalogRegistry,
    ComponentIdentity,
    HandshakeRequest,
    catalog_satisfies_interface,
    get_catalog,
    negotiate_capabilities,
)


def test_browser_family_and_playwright_catalogs_are_registered() -> None:
    assert get_catalog(BROWSER_AUTOMATION_INTERFACE) is BROWSER_AUTOMATION_CATALOG
    assert get_catalog(PLAYWRIGHT_BROWSER_INTERFACE) is PLAYWRIGHT_BROWSER_CATALOG


def test_browser_family_catalog_is_abstract() -> None:
    with raises(ValueError, match="Abstract catalog"):
        BROWSER_AUTOMATION_CATALOG.validate_capability_matrix(CapabilityMatrix())


def test_browser_catalog_hierarchy_reports_playwright_compatibility() -> None:
    assert catalog_satisfies_interface(
        PLAYWRIGHT_BROWSER_INTERFACE,
        BROWSER_AUTOMATION_INTERFACE,
    )
    assert (
        catalog_satisfies_interface(
            BROWSER_AUTOMATION_INTERFACE,
            PLAYWRIGHT_BROWSER_INTERFACE,
        )
        is False
    )


def test_handshake_accepts_playwright_for_browser_family() -> None:
    request = HandshakeRequest(
        client_identity=ComponentIdentity(
            interface=BROWSER_AUTOMATION_INTERFACE,
            provider="cosecha",
            version="1.0.0",
        ),
        required_capabilities=(),
    )
    provider_identity = ComponentIdentity(
        interface=PLAYWRIGHT_BROWSER_INTERFACE,
        provider="playwright",
        version="1.0.0",
    )

    response = negotiate_capabilities(
        request,
        provider_identity,
        CapabilityMatrix(),
    )

    assert response.status == "accepted"


def test_handshake_rejects_abstract_browser_family_for_playwright_requirement() -> None:
    request = HandshakeRequest(
        client_identity=ComponentIdentity(
            interface=PLAYWRIGHT_BROWSER_INTERFACE,
            provider="cosecha",
            version="1.0.0",
        ),
        required_capabilities=(),
    )
    provider_identity = ComponentIdentity(
        interface=BROWSER_AUTOMATION_INTERFACE,
        provider="generic-browser",
        version="1.0.0",
    )

    response = negotiate_capabilities(
        request,
        provider_identity,
        CapabilityMatrix(),
    )

    assert response.status == "rejected"


def test_playwright_catalog_reports_core_and_observable_tiers() -> None:
    satisfied_tiers = PLAYWRIGHT_BROWSER_CATALOG.satisfied_tiers(
        (
            PLAYWRIGHT_BROWSER_LIFECYCLE,
            PLAYWRIGHT_BROWSER_CONTEXT_MANAGEMENT,
            PLAYWRIGHT_BROWSER_PAGE_NAVIGATION,
            "locator_resolution",
            PLAYWRIGHT_BROWSER_DOM_INTERACTION,
            PLAYWRIGHT_BROWSER_WAIT_CONDITIONS,
            PLAYWRIGHT_BROWSER_SCRIPT_EVALUATION,
            PLAYWRIGHT_BROWSER_NETWORK_OBSERVATION,
            PLAYWRIGHT_BROWSER_SCREENSHOT_CAPTURE,
            PLAYWRIGHT_BROWSER_DIALOG_HANDLING,
        )
    )

    assert satisfied_tiers == (
        PLAYWRIGHT_BROWSER_CORE_TIER,
        PLAYWRIGHT_BROWSER_OBSERVABLE_TIER,
    )


def test_playwright_observable_tier_requires_observability_capabilities() -> None:
    validation = PLAYWRIGHT_BROWSER_CATALOG.validate_capability_set(
        (
            PLAYWRIGHT_BROWSER_LIFECYCLE,
            PLAYWRIGHT_BROWSER_CONTEXT_MANAGEMENT,
            PLAYWRIGHT_BROWSER_PAGE_NAVIGATION,
            "locator_resolution",
            PLAYWRIGHT_BROWSER_DOM_INTERACTION,
            PLAYWRIGHT_BROWSER_WAIT_CONDITIONS,
        ),
        required_tier=PLAYWRIGHT_BROWSER_OBSERVABLE_TIER,
    )

    assert validation.missing_tier_capabilities == (
        PLAYWRIGHT_BROWSER_SCRIPT_EVALUATION,
        PLAYWRIGHT_BROWSER_NETWORK_OBSERVATION,
        PLAYWRIGHT_BROWSER_SCREENSHOT_CAPTURE,
        PLAYWRIGHT_BROWSER_DIALOG_HANDLING,
    )


def test_playwright_catalog_exposes_canonical_operations() -> None:
    assert (
        PLAYWRIGHT_BROWSER_CATALOG.has_operation(
            PLAYWRIGHT_BROWSER_PAGE_NAVIGATION,
            PLAYWRIGHT_BROWSER_PAGE_GOTO,
        )
        is True
    )
    assert (
        PLAYWRIGHT_BROWSER_CATALOG.has_operation(
            PLAYWRIGHT_BROWSER_DOM_INTERACTION,
            "element.click",
        )
        is True
    )


def test_browser_registry_rejects_unknown_or_cyclic_hierarchy() -> None:
    registry = CatalogRegistry(
        catalogs=(
            CapabilityCatalog(
                interface=BROWSER_AUTOMATION_INTERFACE,
                abstract=True,
            ),
        )
    )

    with raises(ValueError, match="unknown satisfied interface"):
        registry.register(
            CapabilityCatalog(
                interface=PLAYWRIGHT_BROWSER_INTERFACE,
                satisfies_interfaces=("browser/missing",),
            )
        )

    registry.register(
        CapabilityCatalog(
            interface=PLAYWRIGHT_BROWSER_INTERFACE,
            satisfies_interfaces=(BROWSER_AUTOMATION_INTERFACE,),
        )
    )

    with raises(ValueError, match="cannot contain cycles"):
        registry.register(
            CapabilityCatalog(
                interface=BROWSER_AUTOMATION_INTERFACE,
                abstract=True,
                satisfies_interfaces=(PLAYWRIGHT_BROWSER_INTERFACE,),
            ),
            replace=True,
        )
