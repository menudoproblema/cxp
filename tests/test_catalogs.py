import msgspec
from pytest import raises

from cxp import (
    EXECUTION_ENGINE_CATALOG,
    EXECUTION_ENGINE_FAMILY_CATALOG,
    MongoAggregationMetadata,
    MongoCollationMetadata,
    MongoPersistenceMetadata,
    MongoSearchMetadata,
    MongoTopologyDiscoveryMetadata,
    MongoVectorSearchMetadata,
    MONGODB_AGGREGATE,
    MONGODB_COUNT_DOCUMENTS,
    MONGODB_DELETE_MANY,
    MONGODB_DELETE_ONE,
    MONGODB_DISTINCT,
    MONGODB_ESTIMATED_DOCUMENT_COUNT,
    MONGODB_INSERT_MANY,
    MONGODB_INSERT_ONE,
    MONGODB_REPLACE_ONE,
    MONGODB_START_SESSION,
    MONGODB_UPDATE_MANY,
    MONGODB_UPDATE_ONE,
    CapabilityOperationBinding,
    PLAN_RUN_EXECUTION_CATALOG,
    HTTP_APPLICATION_CATALOG,
    HTTP_TRANSPORT_CATALOG,
    MONGODB_CATALOG,
    MONGODB_CORE_PROFILE,
    MONGODB_PLATFORM_PROFILE,
    MONGODB_TEXT_SEARCH_PROFILE,
    MONGODB_SEARCH_PROFILE,
    PLAN_RUN_EXECUTION_ADVANCED_PROFILE,
    Capability,
    CapabilityCatalog,
    CapabilityMatrix,
    CapabilityMatrixValidationResult,
    CapabilityProfile,
    CatalogCapability,
    CatalogOperation,
    CapabilityRequirement,
    ConformanceTier,
    ComponentCapabilitySnapshot,
    CapabilityDescriptor,
    get_catalog,
    PLAYWRIGHT_BROWSER_CORE_PROFILE,
    PLAYWRIGHT_BROWSER_OBSERVABLE_PROFILE,
    PLAN_RUN_EXECUTION_CORE_PROFILE,
    PLAN_RUN_EXECUTION_PLANNED_PROFILE,
)
from cxp.catalogs.base import _metadata_key_set


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


def test_mongodb_search_and_platform_tiers_require_aggregation() -> None:
    search_validation = MONGODB_CATALOG.validate_capability_set(
        (
            "read",
            "write",
            "search",
            "vector_search",
        ),
        required_tier="search",
    )
    platform_validation = MONGODB_CATALOG.validate_capability_set(
        (
            "read",
            "write",
            "transactions",
            "change_streams",
            "collation",
            "persistence",
            "topology_discovery",
        ),
        required_tier="platform",
    )

    assert search_validation.missing_tier_capabilities == ("aggregation",)
    assert platform_validation.missing_tier_capabilities == ("aggregation",)


def test_mongodb_catalog_exposes_canonical_first_level_operations() -> None:
    assert MONGODB_CATALOG.has_operation("aggregation", MONGODB_AGGREGATE) is True
    assert MONGODB_CATALOG.has_operation("read", "find") is True
    assert MONGODB_CATALOG.has_operation("write", "update_one") is True
    assert MONGODB_CATALOG.has_operation("change_streams", "watch") is True


def test_mongodb_profiles_validate_snapshot_requirements() -> None:
    snapshot = ComponentCapabilitySnapshot(
        component_name="provider",
        identity=None,
        capabilities=(
            CapabilityDescriptor(
                name="read",
                level="supported",
                operations=(
                    CapabilityOperationBinding("find"),
                    CapabilityOperationBinding("find_one"),
                    CapabilityOperationBinding("count_documents"),
                    CapabilityOperationBinding("estimated_document_count"),
                    CapabilityOperationBinding("distinct"),
                ),
            ),
            CapabilityDescriptor(
                name="write",
                level="supported",
                operations=(
                    CapabilityOperationBinding("insert_one"),
                    CapabilityOperationBinding("insert_many"),
                    CapabilityOperationBinding("update_one"),
                    CapabilityOperationBinding("update_many"),
                    CapabilityOperationBinding("replace_one"),
                    CapabilityOperationBinding("delete_one"),
                    CapabilityOperationBinding("delete_many"),
                    CapabilityOperationBinding("bulk_write"),
                ),
            ),
            CapabilityDescriptor(
                name="aggregation",
                level="supported",
                operations=(CapabilityOperationBinding("aggregate"),),
                metadata={"supportedStages": ["$match", "$group"]},
            ),
            CapabilityDescriptor(
                name="search",
                level="supported",
                operations=(CapabilityOperationBinding("aggregate"),),
                metadata={"operators": ["text"], "aggregateStage": "$search"},
            ),
            CapabilityDescriptor(
                name="vector_search",
                level="supported",
                operations=(CapabilityOperationBinding("aggregate"),),
                metadata={
                    "similarities": ["cosine"],
                    "aggregateStage": "$vectorSearch",
                },
            ),
            CapabilityDescriptor(
                name="transactions",
                level="supported",
                operations=(
                    CapabilityOperationBinding("start_session"),
                    CapabilityOperationBinding("with_transaction"),
                ),
            ),
            CapabilityDescriptor(
                name="change_streams",
                level="supported",
                operations=(CapabilityOperationBinding("watch"),),
            ),
            CapabilityDescriptor(
                name="collation",
                level="supported",
                metadata={"backend": {}, "capabilities": {}},
            ),
            CapabilityDescriptor(
                name="persistence",
                level="supported",
                metadata={"persistent": True, "storageEngine": "sqlite"},
            ),
            CapabilityDescriptor(
                name="topology_discovery",
                level="supported",
                metadata={"topologyType": "single", "serverCount": 1, "sdam": {}},
            ),
        ),
    )

    assert MONGODB_CATALOG.is_component_snapshot_profile_compliant(
        snapshot,
        MONGODB_CORE_PROFILE,
    )
    assert MONGODB_CATALOG.is_component_snapshot_profile_compliant(
        snapshot,
        MONGODB_TEXT_SEARCH_PROFILE,
    )
    assert MONGODB_CATALOG.is_component_snapshot_profile_compliant(
        snapshot,
        MONGODB_SEARCH_PROFILE,
    )
    assert MONGODB_CATALOG.is_component_snapshot_profile_compliant(
        snapshot,
        MONGODB_PLATFORM_PROFILE,
    )


def test_profile_definition_rejects_unknown_operations() -> None:
    with raises(ValueError, match="Unknown profile operations"):
        CapabilityProfile(
            name="invalid-read-profile",
            interface="database/mongodb",
            requirements=(
                CapabilityRequirement(
                    capability_name="read",
                    required_operations=("read_all",),
                ),
            ),
        )


def test_profile_definition_rejects_unknown_metadata_keys() -> None:
    with raises(ValueError, match="Unknown profile metadata keys"):
        CapabilityProfile(
            name="invalid-aggregation-profile",
            interface="database/mongodb",
            requirements=(
                CapabilityRequirement(
                    capability_name="aggregation",
                    required_metadata_keys=("nonCanonicalKey",),
                ),
            ),
        )


def test_profile_definition_rejects_unregistered_interfaces() -> None:
    with raises(ValueError, match="references unregistered interface"):
        CapabilityProfile(
            name="invalid-interface-profile",
            interface="application/unknown",
            requirements=(),
        )


def test_mongodb_core_profile_requires_complete_read_and_write_operations() -> None:
    snapshot = ComponentCapabilitySnapshot(
        component_name="provider",
        capabilities=(
            CapabilityDescriptor(
                name="read",
                level="supported",
                operations=(
                    CapabilityOperationBinding("find"),
                    CapabilityOperationBinding("find_one"),
                    CapabilityOperationBinding("count_documents"),
                ),
            ),
            CapabilityDescriptor(
                name="write",
                level="supported",
                operations=(
                    CapabilityOperationBinding("insert_one"),
                    CapabilityOperationBinding("update_one"),
                    CapabilityOperationBinding("delete_one"),
                ),
            ),
            CapabilityDescriptor(
                name="aggregation",
                level="supported",
                operations=(CapabilityOperationBinding("aggregate"),),
                metadata={"supportedStages": ["$match"]},
            ),
        ),
    )

    validation = MONGODB_CATALOG.validate_component_snapshot_against_profile(
        snapshot,
        MONGODB_CORE_PROFILE,
    )

    assert tuple(
        (missing.capability_name, missing.operation_names)
        for missing in validation.missing_operations
    ) == (
        ("read", ("estimated_document_count", "distinct")),
        (
            "write",
            (
                "insert_many",
                "update_many",
                "replace_one",
                "delete_many",
                "bulk_write",
            ),
        ),
    )


def test_mongodb_catalog_and_profiles_validate_metadata_shape() -> None:
    snapshot = ComponentCapabilitySnapshot(
        component_name="provider",
        capabilities=(
            CapabilityDescriptor(
                name="aggregation",
                level="supported",
                operations=(CapabilityOperationBinding("aggregate"),),
                metadata={"supportedStages": "$match"},
            ),
            CapabilityDescriptor(
                name="collation",
                level="supported",
                metadata={"backend": 1, "capabilities": "invalid"},
            ),
            CapabilityDescriptor(
                name="persistence",
                level="supported",
                metadata={"persistent": "yes", "storageEngine": []},
            ),
            CapabilityDescriptor(
                name="topology_discovery",
                level="supported",
                metadata={"topologyType": 0, "serverCount": "one", "sdam": []},
            ),
        ),
    )
    matrix = CapabilityMatrix(
        capabilities=(
            Capability(
                name="aggregation",
                metadata={"supportedStages": "$match"},
            ),
            Capability(
                name="collation",
                metadata={"backend": 1, "capabilities": "invalid"},
            ),
            Capability(
                name="persistence",
                metadata={"persistent": "yes", "storageEngine": []},
            ),
            Capability(
                name="topology_discovery",
                metadata={"topologyType": 0, "serverCount": "one", "sdam": []},
            ),
        ),
    )

    descriptor_validation = MONGODB_CATALOG.validate_component_snapshot(snapshot)
    matrix_validation = MONGODB_CATALOG.validate_capability_matrix(matrix)
    profile_validation = MONGODB_CATALOG.validate_component_snapshot_against_profile(
        snapshot,
        MONGODB_PLATFORM_PROFILE,
    )

    assert descriptor_validation.invalid_metadata == (
        "aggregation",
        "collation",
        "persistence",
        "topology_discovery",
    )
    assert matrix_validation.invalid_metadata == (
        "aggregation",
        "collation",
        "persistence",
        "topology_discovery",
    )
    assert profile_validation.invalid_metadata == (
        "aggregation",
        "collation",
        "persistence",
        "topology_discovery",
    )
    assert profile_validation.is_valid() is False


def test_public_api_reexports_complete_mongodb_contract() -> None:
    assert MONGODB_COUNT_DOCUMENTS == "count_documents"
    assert MONGODB_DELETE_MANY == "delete_many"
    assert MONGODB_DELETE_ONE == "delete_one"
    assert MONGODB_DISTINCT == "distinct"
    assert MONGODB_ESTIMATED_DOCUMENT_COUNT == "estimated_document_count"
    assert MONGODB_INSERT_MANY == "insert_many"
    assert MONGODB_INSERT_ONE == "insert_one"
    assert MONGODB_REPLACE_ONE == "replace_one"
    assert MONGODB_START_SESSION == "start_session"
    assert MONGODB_UPDATE_MANY == "update_many"
    assert MONGODB_UPDATE_ONE == "update_one"
    assert MongoAggregationMetadata(supportedStages=("$match",)).supportedStages == (
        "$match",
    )
    assert MongoSearchMetadata(operators=("text",)).aggregateStage == "$search"
    assert MongoVectorSearchMetadata(similarities=("cosine",)).aggregateStage == "$vectorSearch"
    assert MongoCollationMetadata().backend == {}
    assert MongoPersistenceMetadata(persistent=True, storageEngine="sqlite").storageEngine == "sqlite"
    assert MongoTopologyDiscoveryMetadata(topologyType="single", serverCount=1).serverCount == 1


def test_mongodb_search_profile_supports_consumer_style_snapshot_validation() -> None:
    snapshot = ComponentCapabilitySnapshot(
        component_name="provider",
        capabilities=(
            CapabilityDescriptor(
                name="read",
                level="supported",
                operations=tuple(
                    CapabilityOperationBinding(name)
                    for name in (
                        "find",
                        "find_one",
                        "count_documents",
                        "estimated_document_count",
                        "distinct",
                    )
                ),
            ),
            CapabilityDescriptor(
                name="write",
                level="supported",
                operations=tuple(
                    CapabilityOperationBinding(name)
                    for name in (
                        "insert_one",
                        "insert_many",
                        "update_one",
                        "update_many",
                        "replace_one",
                        "delete_one",
                        "delete_many",
                        "bulk_write",
                    )
                ),
            ),
            CapabilityDescriptor(
                name="aggregation",
                level="supported",
                operations=(CapabilityOperationBinding("aggregate"),),
                metadata=MongoAggregationMetadata(
                    supportedStages=("$match", "$search", "$vectorSearch"),
                    supportedExpressionOperators=("$eq",),
                ),
            ),
            CapabilityDescriptor(
                name="search",
                level="supported",
                operations=(CapabilityOperationBinding("aggregate"),),
                metadata=MongoSearchMetadata(operators=("text", "compound")),
            ),
            CapabilityDescriptor(
                name="vector_search",
                level="supported",
                operations=(CapabilityOperationBinding("aggregate"),),
                metadata=MongoVectorSearchMetadata(similarities=("cosine",)),
            ),
        ),
    )

    validation = MONGODB_CATALOG.validate_component_snapshot_against_profile(
        snapshot,
        MONGODB_SEARCH_PROFILE,
    )

    assert validation.is_valid() is True
    assert validation.missing_capabilities == ()
    assert validation.invalid_metadata == ()


def test_mongodb_text_search_profile_does_not_require_vector_search() -> None:
    snapshot = ComponentCapabilitySnapshot(
        component_name="provider",
        capabilities=(
            CapabilityDescriptor(
                name="read",
                level="supported",
                operations=tuple(
                    CapabilityOperationBinding(name)
                    for name in (
                        "find",
                        "find_one",
                        "count_documents",
                        "estimated_document_count",
                        "distinct",
                    )
                ),
            ),
            CapabilityDescriptor(
                name="write",
                level="supported",
                operations=tuple(
                    CapabilityOperationBinding(name)
                    for name in (
                        "insert_one",
                        "insert_many",
                        "update_one",
                        "update_many",
                        "replace_one",
                        "delete_one",
                        "delete_many",
                        "bulk_write",
                    )
                ),
            ),
            CapabilityDescriptor(
                name="aggregation",
                level="supported",
                operations=(CapabilityOperationBinding("aggregate"),),
                metadata=MongoAggregationMetadata(
                    supportedStages=("$match", "$search"),
                ),
            ),
            CapabilityDescriptor(
                name="search",
                level="supported",
                operations=(CapabilityOperationBinding("aggregate"),),
                metadata=MongoSearchMetadata(operators=("text", "phrase")),
            ),
        ),
    )

    text_search_validation = MONGODB_CATALOG.validate_component_snapshot_against_profile(
        snapshot,
        MONGODB_TEXT_SEARCH_PROFILE,
    )
    search_validation = MONGODB_CATALOG.validate_component_snapshot_against_profile(
        snapshot,
        MONGODB_SEARCH_PROFILE,
    )

    assert text_search_validation.is_valid() is True
    assert search_validation.missing_capabilities == ("vector_search",)


def test_plan_run_profiles_validate_progressive_execution_snapshots() -> None:
    core_snapshot = ComponentCapabilitySnapshot(
        component_name="engine",
        capabilities=(
            CapabilityDescriptor(
                name="run",
                level="supported",
                operations=(CapabilityOperationBinding("run"),),
            ),
        ),
    )
    planned_snapshot = ComponentCapabilitySnapshot(
        component_name="engine",
        capabilities=core_snapshot.capabilities
        + (
            CapabilityDescriptor(
                name="planning",
                level="supported",
                operations=(
                    CapabilityOperationBinding("plan.analyze"),
                    CapabilityOperationBinding("plan.explain"),
                    CapabilityOperationBinding("plan.simulate"),
                ),
            ),
        ),
    )
    advanced_snapshot = ComponentCapabilitySnapshot(
        component_name="engine",
        capabilities=planned_snapshot.capabilities
        + (
            CapabilityDescriptor(
                name="input_validation",
                level="supported",
                operations=(CapabilityOperationBinding("input.validate"),),
            ),
            CapabilityDescriptor(
                name="execution_status",
                level="supported",
                operations=(
                    CapabilityOperationBinding("execution.status"),
                    CapabilityOperationBinding("execution.cancel"),
                ),
            ),
            CapabilityDescriptor(
                name="execution_stream",
                level="supported",
                operations=(
                    CapabilityOperationBinding("execution.subscribe"),
                    CapabilityOperationBinding("execution.tail"),
                ),
            ),
        ),
    )

    assert PLAN_RUN_EXECUTION_CATALOG.is_component_snapshot_profile_compliant(
        core_snapshot,
        PLAN_RUN_EXECUTION_CORE_PROFILE,
    )
    assert PLAN_RUN_EXECUTION_CATALOG.is_component_snapshot_profile_compliant(
        planned_snapshot,
        PLAN_RUN_EXECUTION_PLANNED_PROFILE,
    )
    assert PLAN_RUN_EXECUTION_CATALOG.is_component_snapshot_profile_compliant(
        advanced_snapshot,
        PLAN_RUN_EXECUTION_ADVANCED_PROFILE,
    )


def test_playwright_profiles_validate_core_and_observable_snapshots() -> None:
    core_snapshot = ComponentCapabilitySnapshot(
        component_name="browser",
        capabilities=(
            CapabilityDescriptor(
                name="browser_lifecycle",
                level="supported",
                operations=(
                    CapabilityOperationBinding("browser.launch"),
                    CapabilityOperationBinding("browser.close"),
                ),
            ),
            CapabilityDescriptor(
                name="context_management",
                level="supported",
                operations=(
                    CapabilityOperationBinding("context.create"),
                    CapabilityOperationBinding("context.close"),
                ),
            ),
            CapabilityDescriptor(
                name="page_navigation",
                level="supported",
                operations=(
                    CapabilityOperationBinding("page.goto"),
                    CapabilityOperationBinding("page.reload"),
                    CapabilityOperationBinding("page.go_back"),
                ),
            ),
            CapabilityDescriptor(
                name="locator_resolution",
                level="supported",
                operations=(
                    CapabilityOperationBinding("locator.query"),
                    CapabilityOperationBinding("locator.filter"),
                ),
            ),
            CapabilityDescriptor(
                name="dom_interaction",
                level="supported",
                operations=(
                    CapabilityOperationBinding("element.click"),
                    CapabilityOperationBinding("element.fill"),
                    CapabilityOperationBinding("element.press"),
                    CapabilityOperationBinding("element.select_option"),
                ),
            ),
            CapabilityDescriptor(
                name="wait_conditions",
                level="supported",
                operations=(
                    CapabilityOperationBinding("wait.for_selector"),
                    CapabilityOperationBinding("wait.for_url"),
                    CapabilityOperationBinding("wait.for_response"),
                ),
            ),
        ),
    )
    observable_snapshot = ComponentCapabilitySnapshot(
        component_name="browser",
        capabilities=core_snapshot.capabilities
        + (
            CapabilityDescriptor(
                name="script_evaluation",
                level="supported",
                operations=(
                    CapabilityOperationBinding("page.evaluate"),
                    CapabilityOperationBinding("element.evaluate"),
                ),
            ),
            CapabilityDescriptor(
                name="network_observation",
                level="supported",
                operations=(
                    CapabilityOperationBinding("network.request.observe"),
                    CapabilityOperationBinding("network.response.observe"),
                ),
            ),
            CapabilityDescriptor(
                name="screenshot_capture",
                level="supported",
                operations=(
                    CapabilityOperationBinding("page.screenshot"),
                    CapabilityOperationBinding("element.screenshot"),
                ),
            ),
            CapabilityDescriptor(
                name="dialog_handling",
                level="supported",
                operations=(
                    CapabilityOperationBinding("dialog.accept"),
                    CapabilityOperationBinding("dialog.dismiss"),
                ),
            ),
        ),
    )

    assert get_catalog("browser/playwright").is_component_snapshot_profile_compliant(
        core_snapshot,
        PLAYWRIGHT_BROWSER_CORE_PROFILE,
    )
    assert get_catalog("browser/playwright").is_component_snapshot_profile_compliant(
        observable_snapshot,
        PLAYWRIGHT_BROWSER_OBSERVABLE_PROFILE,
    )


def test_metadata_key_set_supports_mappings_structs_and_fallback_values() -> None:
    assert _metadata_key_set({"supportedStages": []}) == frozenset({"supportedStages"})
    assert _metadata_key_set(MongoSearchMetadata(operators=("text",))) == frozenset(
        {"operators", "aggregateStage"}
    )
    assert _metadata_key_set(1) == frozenset()


def test_default_registry_exposes_transport_and_application_catalogs():
    assert get_catalog("transport/http") is HTTP_TRANSPORT_CATALOG
    assert get_catalog("application/http") is HTTP_APPLICATION_CATALOG
    assert get_catalog("execution/engine") is EXECUTION_ENGINE_FAMILY_CATALOG
    assert EXECUTION_ENGINE_CATALOG is PLAN_RUN_EXECUTION_CATALOG
    assert get_catalog("execution/plan-run") is PLAN_RUN_EXECUTION_CATALOG


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
        interface="execution/plan-run",
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
    assert PLAN_RUN_EXECUTION_CATALOG.has_operation("planning", "plan.analyze")
    assert PLAN_RUN_EXECUTION_CATALOG.has_operation("execution_stream", "execution.tail")

    operation = PLAN_RUN_EXECUTION_CATALOG.get_operation("run", "run")
    assert operation is not None
    assert operation.result_type == "run.result"


class PlanningMetadata(msgspec.Struct, frozen=True):
    mode: str
    explain: bool = False


def test_catalog_can_validate_metadata_against_declared_schema() -> None:
    catalog = CapabilityCatalog(
        interface="execution/plan-run",
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
        interface="execution/plan-run",
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
        interface="execution/plan-run",
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
        interface="execution/plan-run",
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
