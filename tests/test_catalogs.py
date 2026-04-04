import msgspec

from cxp import (
    EXECUTION_ENGINE_CATALOG,
    HTTP_APPLICATION_CATALOG,
    HTTP_TRANSPORT_CATALOG,
    MONGODB_CATALOG,
    Capability,
    CapabilityCatalog,
    CapabilityMatrix,
    CapabilityMatrixValidationResult,
    CatalogCapability,
    CatalogOperation,
    ConformanceTier,
    get_catalog,
)


def test_default_registry_exposes_mongodb_catalog():
    catalog = get_catalog("database/mongodb")

    assert catalog is MONGODB_CATALOG
    assert catalog is not None
    assert catalog.interface == "database/mongodb"


def test_catalog_validates_unknown_capabilities():
    unknown_capabilities = MONGODB_CATALOG.validate_capability_names(
        ("read", "write", "custom_feature")
    )

    assert unknown_capabilities == ("custom_feature",)


def test_catalog_reports_satisfied_tiers():
    satisfied_tiers = MONGODB_CATALOG.satisfied_tiers(
        (
            "read",
            "write",
            "aggregation",
        )
    )

    assert satisfied_tiers == ("core",)


def test_mongodb_catalog_reports_search_and_platform_tiers():
    satisfied_tiers = MONGODB_CATALOG.satisfied_tiers(
        (
            "read",
            "write",
            "aggregation",
            "search",
            "vector_search",
            "transactions",
            "change_streams",
            "collation",
            "persistence",
            "topology_discovery",
        )
    )

    assert satisfied_tiers == ("core", "search", "platform")


def test_default_registry_exposes_transport_and_application_catalogs():
    assert get_catalog("transport/http") is HTTP_TRANSPORT_CATALOG
    assert get_catalog("application/http") is HTTP_APPLICATION_CATALOG
    assert get_catalog("execution/engine") is EXECUTION_ENGINE_CATALOG


def test_custom_catalog_can_define_its_own_tiers():
    catalog = CapabilityCatalog(
        interface="transport/http",
        capabilities=(
            CatalogCapability(name="request"),
            CatalogCapability(name="streaming"),
        ),
        tiers=(
            ConformanceTier(
                name="core",
                required_capabilities=("request",),
            ),
        ),
    )

    assert catalog.has_capability("request")
    assert catalog.get_tier("core") is not None
    assert catalog.satisfied_tiers(("request", "streaming")) == ("core",)


def test_catalog_capability_can_define_operations() -> None:
    catalog = CapabilityCatalog(
        interface="execution/engine",
        capabilities=(
            CatalogCapability(
                name="planning",
                operations=(
                    CatalogOperation(
                        name="plan.analyze",
                        result_type="plan.analyzed",
                    ),
                    CatalogOperation(
                        name="plan.explain",
                        result_type="plan.explained",
                    ),
                ),
            ),
        ),
    )

    assert catalog.capability_operation_names("planning") == (
        "plan.analyze",
        "plan.explain",
    )
    assert catalog.has_operation("planning", "plan.analyze") is True

    operation = catalog.get_operation("planning", "plan.explain")
    assert operation is not None
    assert operation.result_type == "plan.explained"


def test_execution_engine_catalog_exposes_typed_operations() -> None:
    assert EXECUTION_ENGINE_CATALOG.has_operation("planning", "plan.analyze")
    assert EXECUTION_ENGINE_CATALOG.has_operation(
        "live_execution_observability",
        "execution.live_tail",
    )

    operation = EXECUTION_ENGINE_CATALOG.get_operation("run", "run")
    assert operation is not None
    assert operation.result_type == "run.result"


class PlanningMetadata(msgspec.Struct, frozen=True):
    mode: str
    explain: bool = False


def test_catalog_can_validate_metadata_against_declared_schema() -> None:
    catalog = CapabilityCatalog(
        interface="execution/engine",
        capabilities=(
            CatalogCapability(
                name="planning",
                metadata_schema=PlanningMetadata,
            ),
        ),
    )
    matrix = CapabilityMatrix(
        capabilities=(
            Capability(
                name="planning",
                metadata={"mode": "strict", "explain": True},
            ),
        ),
    )

    assert catalog.invalid_capability_metadata(matrix) == ()
    assert catalog.is_capability_matrix_compliant(matrix) is True


def test_catalog_can_return_rich_matrix_validation_result() -> None:
    catalog = CapabilityCatalog(
        interface="execution/engine",
        capabilities=(CatalogCapability(name="run"),),
        tiers=(
            ConformanceTier(
                name="core",
                required_capabilities=("run", "planning"),
            ),
        ),
    )
    matrix = CapabilityMatrix(
        capabilities=(
            Capability(name="run"),
            Capability(name="custom"),
        ),
    )

    validation = catalog.validate_capability_matrix(
        matrix,
        required_tier="core",
    )

    assert isinstance(validation, CapabilityMatrixValidationResult)
    assert validation.unknown_capabilities == ("custom",)
    assert validation.missing_tier_capabilities == ("planning",)
    assert validation.messages() == (
        "Unknown capabilities: custom",
        "Missing capabilities for required tier 'core': planning",
    )
    assert validation.is_valid() is False


def test_catalog_reports_invalid_metadata_when_schema_does_not_match() -> None:
    catalog = CapabilityCatalog(
        interface="execution/engine",
        capabilities=(
            CatalogCapability(
                name="planning",
                metadata_schema=PlanningMetadata,
            ),
        ),
    )
    matrix = CapabilityMatrix(
        capabilities=(
            Capability(
                name="planning",
                metadata={"mode": 3},
            ),
        ),
    )

    assert catalog.invalid_capability_metadata(matrix) == ("planning",)
    assert catalog.is_capability_matrix_compliant(matrix) is False


def test_catalog_reports_unknown_required_tier_in_matrix_validation() -> None:
    catalog = CapabilityCatalog(
        interface="execution/engine",
        capabilities=(CatalogCapability(name="run"),),
    )
    matrix = CapabilityMatrix(
        capabilities=(Capability(name="run"),),
    )

    validation = catalog.validate_capability_matrix(
        matrix,
        required_tier="advanced",
    )

    assert validation.unknown_required_tier == "advanced"
    assert validation.messages() == ("Unknown required tier: 'advanced'",)
