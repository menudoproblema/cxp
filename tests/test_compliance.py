import asyncio

import msgspec

from cxp import (
    BROWSER_AUTOMATION_CATALOG,
    BROWSER_AUTOMATION_INTERFACE,
    MONGODB_CATALOG,
    PLAYWRIGHT_BROWSER_CATALOG,
    PLAYWRIGHT_BROWSER_LIFECYCLE,
    PLAYWRIGHT_BROWSER_OBSERVABLE_TIER,
    Capability,
    CapabilityCatalog,
    CapabilityMatrix,
    CatalogCapability,
    evaluate_capability_matrix_against_catalog,
    evaluate_handshake_response_against_catalog,
    negotiate_with_async_provider_catalog_report,
    negotiate_with_provider_catalog,
    negotiate_with_provider_catalog_report,
)


def test_evaluate_capability_matrix_against_catalog_accepts_exact_interface() -> None:
    report = evaluate_capability_matrix_against_catalog(
        "database/mongodb",
        CapabilityMatrix(capabilities=(Capability(name="read"),)),
        MONGODB_CATALOG,
    )

    assert report.compliant is True
    assert report.catalog_interface == "database/mongodb"
    assert report.offered_interface == "database/mongodb"
    assert report.validation is not None
    assert report.validation.is_valid() is True
    assert report.messages == ()
    assert report.reason is None


def test_evaluate_capability_matrix_against_catalog_accepts_family_compatibility() -> (
    None
):
    report = evaluate_capability_matrix_against_catalog(
        "browser/playwright",
        CapabilityMatrix(
            capabilities=(Capability(name=PLAYWRIGHT_BROWSER_LIFECYCLE),)
        ),
        BROWSER_AUTOMATION_CATALOG,
    )

    assert report.compliant is True
    assert report.catalog_interface == BROWSER_AUTOMATION_INTERFACE
    assert report.offered_interface == "browser/playwright"


def test_evaluate_capability_matrix_against_catalog_reports_missing_tier() -> None:
    report = evaluate_capability_matrix_against_catalog(
        "browser/playwright",
        CapabilityMatrix(capabilities=(Capability(name=PLAYWRIGHT_BROWSER_LIFECYCLE),)),
        PLAYWRIGHT_BROWSER_CATALOG,
        required_tier=PLAYWRIGHT_BROWSER_OBSERVABLE_TIER,
    )

    assert report.compliant is False
    assert report.required_tier == PLAYWRIGHT_BROWSER_OBSERVABLE_TIER
    assert report.validation is not None
    assert report.validation.missing_tier_capabilities
    assert "Missing capabilities for required tier" in (report.reason or "")


def test_evaluate_capability_matrix_against_catalog_reports_invalid_metadata() -> None:
    class PlanningMetadata(msgspec.Struct, frozen=True):
        mode: str

    catalog = CapabilityCatalog(
        interface="execution/plan-run",
        capabilities=(
            CatalogCapability(
                name="planning",
                metadata_schema=PlanningMetadata,
            ),
        ),
    )

    report = evaluate_capability_matrix_against_catalog(
        "execution/plan-run",
        CapabilityMatrix(
            capabilities=(
                Capability(
                    name="planning",
                    metadata={"mode": 3},
                ),
            ),
        ),
        catalog,
    )

    assert report.compliant is False
    assert report.validation is not None
    assert report.validation.invalid_metadata == ("planning",)
    assert report.messages == ("Invalid metadata for capabilities: planning",)


def test_evaluate_capability_matrix_against_catalog_reports_interface_mismatch() -> (
    None
):
    report = evaluate_capability_matrix_against_catalog(
        "database/mongodb",
        CapabilityMatrix(capabilities=(Capability(name="read"),)),
        BROWSER_AUTOMATION_CATALOG,
    )

    assert report.compliant is False
    assert report.validation is None
    assert report.messages == (
        "Interface mismatch: provider exposes 'database/mongodb' but catalog "
        "requires 'browser/automation'",
    )


def test_evaluate_handshake_response_against_catalog_preserves_rejected_handshake_reason(  # noqa: E501
    mongo_request_factory,
    sync_mongo_provider_factory,
) -> None:
    response = negotiate_with_provider_catalog(
        mongo_request_factory(interface="execution/plan-run"),
        sync_mongo_provider_factory(("read", "write")),
        MONGODB_CATALOG,
    )
    report = evaluate_handshake_response_against_catalog(response, MONGODB_CATALOG)

    assert response.status == "rejected"
    assert report.compliant is False
    assert report.validation is None
    assert report.reason == response.reason
    assert report.messages == (response.reason,)


def test_negotiate_with_provider_catalog_report_returns_response_and_compliance(
    mongo_request_factory,
    sync_mongo_provider_factory,
) -> None:
    decision = negotiate_with_provider_catalog_report(
        mongo_request_factory(required_capabilities=("read",)),
        sync_mongo_provider_factory(("read", "write")),
        MONGODB_CATALOG,
    )

    assert decision.response.status == "accepted"
    assert decision.compliance.compliant is True
    assert decision.compliance.validation is not None
    assert decision.compliance.validation.is_valid() is True


def test_negotiate_with_provider_catalog_remains_strict_for_catalog_errors(
    mongo_request_factory,
) -> None:
    class UnknownCapabilityProvider:
        def cxp_identity(self):
            from cxp import ComponentIdentity

            return ComponentIdentity(
                interface="database/mongodb",
                provider="example-mongodb",
                version="3.0.0",
            )

        def cxp_capabilities(self):
            return CapabilityMatrix(
                capabilities=(
                    Capability(name="read"),
                    Capability(name="custom_x"),
                ),
            )

    response = negotiate_with_provider_catalog(
        mongo_request_factory(required_capabilities=("read",)),
        UnknownCapabilityProvider(),
        MONGODB_CATALOG,
    )

    assert response.status == "rejected"
    assert response.offered_capabilities == CapabilityMatrix()
    assert response.reason is not None
    assert "Unknown capabilities: custom_x" in response.reason


def test_negotiate_with_async_provider_catalog_report_returns_response_and_compliance(
    mongo_request_factory,
    async_mongo_provider_factory,
) -> None:
    decision = asyncio.run(
        negotiate_with_async_provider_catalog_report(
            mongo_request_factory(required_capabilities=("read",)),
            async_mongo_provider_factory(("read", "write")),
            MONGODB_CATALOG,
        )
    )

    assert decision.response.status == "accepted"
    assert decision.compliance.compliant is True
    assert decision.compliance.validation is not None
    assert decision.compliance.validation.is_valid() is True
