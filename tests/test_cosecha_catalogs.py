from cxp import (
    CapabilityDescriptor,
    CapabilityOperationBinding,
    ComponentCapabilitySnapshot,
    ComponentIdentity,
    get_catalog,
)
from cxp.catalogs.interfaces.cosecha import (
    COSECHA_ENGINE_CATALOG,
    COSECHA_ENGINE_DEPENDENCY_KNOWLEDGE,
    COSECHA_ENGINE_DRAFT_VALIDATION,
    COSECHA_ENGINE_INTERFACE,
    COSECHA_ENGINE_LIFECYCLE,
    COSECHA_ENGINE_ON_DEMAND_DEFINITION_MATERIALIZATION,
    COSECHA_ENGINE_PLAN_EXPLANATION,
    COSECHA_ENGINE_PLANNING_PROFILE,
    COSECHA_ENGINE_PROJECT_DEFINITION_KNOWLEDGE,
    COSECHA_ENGINE_PROJECT_REGISTRY_KNOWLEDGE,
    COSECHA_ENGINE_SELECTION_LABELS,
    COSECHA_ENGINE_STATIC_DEFINITION_DISCOVERY,
    COSECHA_ENGINE_TEST_EXECUTE,
    COSECHA_ENGINE_TEST_LIFECYCLE,
    COSECHA_ENGINE_TEST_PHASE,
    COSECHA_INSTRUMENTATION_BOOTSTRAP,
    COSECHA_INSTRUMENTATION_CATALOG,
    COSECHA_INSTRUMENTATION_INTERFACE,
    COSECHA_INSTRUMENTATION_SESSION_SUMMARY,
    COSECHA_INSTRUMENTATION_STRUCTURED_SUMMARY,
    COSECHA_PLUGIN_CATALOG,
    COSECHA_PLUGIN_INTERFACE,
    COSECHA_PLUGIN_REPORTING_SIDECAR_PROFILE,
    COSECHA_PLUGIN_REPORTING_SIDECAR_TIER,
    COSECHA_PLUGIN_TELEMETRY_EXPORT,
    COSECHA_PLUGIN_TELEMETRY_SIDECAR_PROFILE,
    COSECHA_PLUGIN_TELEMETRY_SIDECAR_TIER,
    COSECHA_PLUGIN_TIMING_SIDECAR_PROFILE,
    COSECHA_PLUGIN_TIMING_SIDECAR_TIER,
    COSECHA_PLUGIN_TIMING_SUMMARY,
    COSECHA_REPORTER_ARTIFACT_OUTPUT,
    COSECHA_REPORTER_ARTIFACT_PROFILE,
    COSECHA_REPORTER_ARTIFACT_TIER,
    COSECHA_REPORTER_CATALOG,
    COSECHA_REPORTER_HUMAN_OUTPUT,
    COSECHA_REPORTER_HUMAN_PROFILE,
    COSECHA_REPORTER_HUMAN_TIER,
    COSECHA_REPORTER_INTERFACE,
    COSECHA_REPORTER_RESULT_PROJECTION,
    COSECHA_REPORTER_STRUCTURED_OUTPUT,
    COSECHA_REPORTER_STRUCTURED_PROFILE,
    COSECHA_RUNTIME_CATALOG,
    COSECHA_RUNTIME_INTERFACE,
)


def test_cosecha_catalogs_are_registered() -> None:
    assert get_catalog(COSECHA_ENGINE_INTERFACE) is COSECHA_ENGINE_CATALOG
    assert get_catalog(COSECHA_REPORTER_INTERFACE) is COSECHA_REPORTER_CATALOG
    assert get_catalog(COSECHA_PLUGIN_INTERFACE) is COSECHA_PLUGIN_CATALOG
    assert get_catalog(COSECHA_RUNTIME_INTERFACE) is COSECHA_RUNTIME_CATALOG
    assert (
        get_catalog(COSECHA_INSTRUMENTATION_INTERFACE)
        is COSECHA_INSTRUMENTATION_CATALOG
    )


def test_cosecha_engine_catalog_validates_explicit_snapshot() -> None:
    snapshot = ComponentCapabilitySnapshot(
        component_name="gherkin",
        identity=ComponentIdentity(
            interface=COSECHA_ENGINE_INTERFACE,
            provider="gherkin",
            version="1",
        ),
        capabilities=(
            CapabilityDescriptor(
                name=COSECHA_ENGINE_LIFECYCLE,
                level="supported",
                operations=(
                    CapabilityOperationBinding("collect"),
                    CapabilityOperationBinding("session.start"),
                    CapabilityOperationBinding("session.finish"),
                ),
            ),
            CapabilityDescriptor(
                name=COSECHA_ENGINE_TEST_LIFECYCLE,
                level="supported",
                operations=(
                    CapabilityOperationBinding("test.start"),
                    CapabilityOperationBinding("test.finish"),
                    CapabilityOperationBinding(COSECHA_ENGINE_TEST_EXECUTE),
                    CapabilityOperationBinding(COSECHA_ENGINE_TEST_PHASE),
                ),
            ),
            CapabilityDescriptor(
                name=COSECHA_ENGINE_DRAFT_VALIDATION,
                level="supported",
                operations=(CapabilityOperationBinding("draft.validate"),),
            ),
            CapabilityDescriptor(
                name=COSECHA_ENGINE_SELECTION_LABELS,
                level="supported",
                metadata={
                    "label_sources": ["feature_tag", "scenario_tag"],
                    "supports_glob_matching": True,
                },
                operations=(
                    CapabilityOperationBinding("plan.analyze"),
                    CapabilityOperationBinding("plan.explain"),
                    CapabilityOperationBinding("plan.simulate"),
                ),
            ),
            CapabilityDescriptor(
                name=COSECHA_ENGINE_PROJECT_DEFINITION_KNOWLEDGE,
                level="supported",
                metadata={
                    "knowledge_origin_kind": ["project"],
                    "knowledge_scopes": ["project"],
                    "supports_fresh_resolution": True,
                    "supports_knowledge_base_projection": True,
                },
                operations=(
                    CapabilityOperationBinding("definition.resolve"),
                    CapabilityOperationBinding("knowledge.query_tests"),
                    CapabilityOperationBinding("knowledge.query_definitions"),
                ),
            ),
            CapabilityDescriptor(
                name=COSECHA_ENGINE_PROJECT_REGISTRY_KNOWLEDGE,
                level="supported",
                metadata={
                    "registry_scopes": ["project"],
                    "supports_knowledge_base_projection": True,
                },
                operations=(
                    CapabilityOperationBinding(
                        "knowledge.query_registry_items",
                    ),
                ),
            ),
            CapabilityDescriptor(
                name=COSECHA_ENGINE_PLAN_EXPLANATION,
                level="supported",
                operations=(
                    CapabilityOperationBinding("plan.analyze"),
                    CapabilityOperationBinding("plan.explain"),
                    CapabilityOperationBinding("plan.simulate"),
                ),
            ),
            CapabilityDescriptor(
                name=COSECHA_ENGINE_STATIC_DEFINITION_DISCOVERY,
                level="supported",
                metadata={"discovery_backends": ["ast"]},
                operations=(
                    CapabilityOperationBinding("knowledge.query_tests"),
                    CapabilityOperationBinding("knowledge.query_definitions"),
                ),
            ),
            CapabilityDescriptor(
                name=COSECHA_ENGINE_ON_DEMAND_DEFINITION_MATERIALIZATION,
                level="supported",
                metadata={"materialization_granularities": ["file"]},
                operations=(CapabilityOperationBinding("definition.resolve"),),
            ),
            CapabilityDescriptor(
                name=COSECHA_ENGINE_DEPENDENCY_KNOWLEDGE,
                level="supported",
                operations=(
                    CapabilityOperationBinding("dependencies.describe"),
                ),
            ),
        ),
    )

    assert COSECHA_ENGINE_CATALOG.is_component_snapshot_compliant(snapshot)


def test_cosecha_engine_catalog_rejects_legacy_dependency_operation_name() -> None:
    snapshot = ComponentCapabilitySnapshot(
        component_name="gherkin",
        identity=ComponentIdentity(
            interface=COSECHA_ENGINE_INTERFACE,
            provider="gherkin",
            version="1",
        ),
        capabilities=(
            CapabilityDescriptor(
                name=COSECHA_ENGINE_DEPENDENCY_KNOWLEDGE,
                level="supported",
                operations=(
                    CapabilityOperationBinding("engine_dependencies.describe"),
                ),
            ),
        ),
    )

    validation = COSECHA_ENGINE_CATALOG.validate_component_snapshot(snapshot)

    assert validation.is_valid() is False
    assert len(validation.unknown_operations) == 1
    assert validation.unknown_operations[0].operation_names == (
        "engine_dependencies.describe",
    )


def test_cosecha_reporter_catalog_distinguishes_human_and_structured_output() -> None:
    structured_snapshot = ComponentCapabilitySnapshot(
        component_name="json",
        identity=ComponentIdentity(
            interface=COSECHA_REPORTER_INTERFACE,
            provider="json",
            version="1",
        ),
        capabilities=(
            CapabilityDescriptor(
                name=COSECHA_REPORTER_RESULT_PROJECTION,
                level="supported",
                operations=(
                    CapabilityOperationBinding("reporter.add_test"),
                    CapabilityOperationBinding("reporter.add_test_result"),
                ),
            ),
            CapabilityDescriptor(
                name=COSECHA_REPORTER_ARTIFACT_OUTPUT,
                level="supported",
                metadata={
                    "artifact_formats": ["json"],
                },
                operations=(
                    CapabilityOperationBinding("reporter.print_report"),
                ),
            ),
            CapabilityDescriptor(
                name=COSECHA_REPORTER_STRUCTURED_OUTPUT,
                level="supported",
                metadata={
                    "output_kind": "structured",
                    "artifact_formats": ["json"],
                    "supports_engine_specific_projection": True,
                },
                operations=(
                    CapabilityOperationBinding("reporter.print_report"),
                ),
            ),
        ),
    )
    human_snapshot = ComponentCapabilitySnapshot(
        component_name="console",
        identity=ComponentIdentity(
            interface=COSECHA_REPORTER_INTERFACE,
            provider="console",
            version="1",
        ),
        capabilities=(
            CapabilityDescriptor(
                name=COSECHA_REPORTER_RESULT_PROJECTION,
                level="supported",
                operations=(
                    CapabilityOperationBinding("reporter.add_test"),
                    CapabilityOperationBinding("reporter.add_test_result"),
                ),
            ),
            CapabilityDescriptor(
                name=COSECHA_REPORTER_HUMAN_OUTPUT,
                level="supported",
                metadata={
                    "output_kind": "console",
                    "supports_engine_specific_projection": True,
                },
                operations=(
                    CapabilityOperationBinding("reporter.print_report"),
                ),
            ),
        ),
    )

    assert COSECHA_REPORTER_CATALOG.is_component_snapshot_compliant(
        structured_snapshot,
    )
    assert COSECHA_REPORTER_CATALOG.is_component_snapshot_compliant(
        human_snapshot,
    )


def test_cosecha_reporter_catalog_allows_human_and_artifact_output_together() -> None:
    snapshot = ComponentCapabilitySnapshot(
        component_name="html",
        identity=ComponentIdentity(
            interface=COSECHA_REPORTER_INTERFACE,
            provider="html",
            version="1",
        ),
        capabilities=(
            CapabilityDescriptor(
                name="report_lifecycle",
                level="supported",
                operations=(
                    CapabilityOperationBinding("reporter.start"),
                    CapabilityOperationBinding("reporter.print_report"),
                ),
            ),
            CapabilityDescriptor(
                name=COSECHA_REPORTER_RESULT_PROJECTION,
                level="supported",
                operations=(
                    CapabilityOperationBinding("reporter.add_test"),
                    CapabilityOperationBinding("reporter.add_test_result"),
                ),
            ),
            CapabilityDescriptor(
                name=COSECHA_REPORTER_ARTIFACT_OUTPUT,
                level="supported",
                metadata={"artifact_formats": ["html"]},
                operations=(
                    CapabilityOperationBinding("reporter.print_report"),
                ),
            ),
            CapabilityDescriptor(
                name=COSECHA_REPORTER_HUMAN_OUTPUT,
                level="supported",
                metadata={"output_kind": "html"},
                operations=(
                    CapabilityOperationBinding("reporter.print_report"),
                ),
            ),
        ),
    )

    assert COSECHA_REPORTER_CATALOG.is_component_snapshot_compliant(snapshot)
    assert COSECHA_REPORTER_CATALOG.is_component_snapshot_profile_compliant(
        snapshot,
        COSECHA_REPORTER_ARTIFACT_PROFILE,
    )
    assert COSECHA_REPORTER_CATALOG.is_component_snapshot_profile_compliant(
        snapshot,
        COSECHA_REPORTER_HUMAN_PROFILE,
    )
    human_tier_validation = COSECHA_REPORTER_CATALOG.validate_capability_set(
        tuple(capability.name for capability in snapshot.capabilities),
        required_tier=COSECHA_REPORTER_HUMAN_TIER,
    )
    artifact_tier_validation = (
        COSECHA_REPORTER_CATALOG.validate_capability_set(
            tuple(capability.name for capability in snapshot.capabilities),
            required_tier=COSECHA_REPORTER_ARTIFACT_TIER,
        )
    )

    assert human_tier_validation.is_valid()
    assert artifact_tier_validation.is_valid()


def test_cosecha_plugin_catalog_supports_declared_optional_capabilities() -> None:
    snapshot = ComponentCapabilitySnapshot(
        component_name="telemetry",
        identity=ComponentIdentity(
            interface=COSECHA_PLUGIN_INTERFACE,
            provider="telemetry",
            version="1",
        ),
        capabilities=(
            CapabilityDescriptor(name="plugin_lifecycle", level="supported"),
            CapabilityDescriptor(
                name="surface_publication",
                level="supported",
                metadata={"provided_surfaces": ["reporter"]},
            ),
            CapabilityDescriptor(
                name="capability_requirements",
                level="supported",
                metadata={"required_capabilities": []},
            ),
            CapabilityDescriptor(
                name=COSECHA_PLUGIN_TELEMETRY_EXPORT,
                level="supported",
                metadata={"output_formats": ["jsonl"]},
            ),
        ),
    )

    assert COSECHA_PLUGIN_CATALOG.is_component_snapshot_compliant(snapshot)
    telemetry_tier_validation = COSECHA_PLUGIN_CATALOG.validate_capability_set(
        tuple(capability.name for capability in snapshot.capabilities),
        required_tier=COSECHA_PLUGIN_TELEMETRY_SIDECAR_TIER,
    )

    assert telemetry_tier_validation.is_valid()
    assert COSECHA_PLUGIN_CATALOG.is_component_snapshot_profile_compliant(
        snapshot,
        COSECHA_PLUGIN_TELEMETRY_SIDECAR_PROFILE,
    )


def test_cosecha_plugin_catalog_supports_timing_sidecars_independently() -> None:
    snapshot = ComponentCapabilitySnapshot(
        component_name="timing",
        identity=ComponentIdentity(
            interface=COSECHA_PLUGIN_INTERFACE,
            provider="timing",
            version="1",
        ),
        capabilities=(
            CapabilityDescriptor(name="plugin_lifecycle", level="supported"),
            CapabilityDescriptor(
                name="surface_publication",
                level="supported",
                metadata={"provided_surfaces": ["reporter"]},
            ),
            CapabilityDescriptor(
                name="capability_requirements",
                level="supported",
                metadata={"required_capabilities": []},
            ),
            CapabilityDescriptor(
                name=COSECHA_PLUGIN_TIMING_SUMMARY,
                level="supported",
                metadata={"output_formats": ["table"]},
            ),
        ),
    )

    assert COSECHA_PLUGIN_CATALOG.is_component_snapshot_compliant(snapshot)
    timing_tier_validation = COSECHA_PLUGIN_CATALOG.validate_capability_set(
        tuple(capability.name for capability in snapshot.capabilities),
        required_tier=COSECHA_PLUGIN_TIMING_SIDECAR_TIER,
    )
    reporting_tier_validation = COSECHA_PLUGIN_CATALOG.validate_capability_set(
        tuple(capability.name for capability in snapshot.capabilities),
        required_tier=COSECHA_PLUGIN_REPORTING_SIDECAR_TIER,
    )

    assert timing_tier_validation.is_valid()
    assert COSECHA_PLUGIN_CATALOG.is_component_snapshot_profile_compliant(
        snapshot,
        COSECHA_PLUGIN_TIMING_SIDECAR_PROFILE,
    )
    assert reporting_tier_validation.is_valid() is False
    assert reporting_tier_validation.missing_tier_capabilities == (
        COSECHA_PLUGIN_TELEMETRY_EXPORT,
    )


def test_cosecha_plugin_reporting_sidecar_profile_requires_both_sidecars() -> None:
    snapshot = ComponentCapabilitySnapshot(
        component_name="combined-sidecar",
        identity=ComponentIdentity(
            interface=COSECHA_PLUGIN_INTERFACE,
            provider="combined-sidecar",
            version="1",
        ),
        capabilities=(
            CapabilityDescriptor(name="plugin_lifecycle", level="supported"),
            CapabilityDescriptor(
                name="surface_publication",
                level="supported",
                metadata={"provided_surfaces": ["reporter"]},
            ),
            CapabilityDescriptor(
                name="capability_requirements",
                level="supported",
                metadata={"required_capabilities": []},
            ),
            CapabilityDescriptor(
                name=COSECHA_PLUGIN_TIMING_SUMMARY,
                level="supported",
                metadata={"output_formats": ["table"]},
            ),
            CapabilityDescriptor(
                name=COSECHA_PLUGIN_TELEMETRY_EXPORT,
                level="supported",
                metadata={"output_formats": ["jsonl"]},
            ),
        ),
    )

    assert COSECHA_PLUGIN_CATALOG.is_component_snapshot_profile_compliant(
        snapshot,
        COSECHA_PLUGIN_REPORTING_SIDECAR_PROFILE,
    )


def test_cosecha_runtime_catalog_validates_observable_runtime() -> None:
    snapshot = ComponentCapabilitySnapshot(
        component_name="process",
        identity=ComponentIdentity(
            interface=COSECHA_RUNTIME_INTERFACE,
            provider="process",
            version="1",
        ),
        capabilities=(
            CapabilityDescriptor(
                name="injected_execution_plans",
                level="supported",
                operations=(CapabilityOperationBinding("run"),),
            ),
            CapabilityDescriptor(
                name="run_scoped_resources",
                level="supported",
                metadata={"supported_scopes": ["run", "worker", "test"]},
            ),
            CapabilityDescriptor(
                name="live_execution_observability",
                level="supported",
                metadata={
                    "delivery_mode": "poll_by_cursor",
                    "granularity": "streaming",
                    "live_channels": ["events", "logs"],
                },
                operations=(
                    CapabilityOperationBinding("execution.subscribe"),
                    CapabilityOperationBinding("execution.live_status"),
                    CapabilityOperationBinding("execution.live_tail"),
                ),
            ),
        ),
    )

    assert COSECHA_RUNTIME_CATALOG.is_component_snapshot_compliant(snapshot)


def test_cosecha_instrumentation_catalog_validates_coverage_summary() -> None:
    snapshot = ComponentCapabilitySnapshot(
        component_name="coverage",
        identity=ComponentIdentity(
            interface=COSECHA_INSTRUMENTATION_INTERFACE,
            provider="coverage",
            version="1",
        ),
        capabilities=(
            CapabilityDescriptor(
                name=COSECHA_INSTRUMENTATION_BOOTSTRAP,
                level="supported",
                operations=(
                    CapabilityOperationBinding("instrumentation.prepare"),
                ),
            ),
            CapabilityDescriptor(
                name=COSECHA_INSTRUMENTATION_SESSION_SUMMARY,
                level="supported",
                metadata={
                    "instrumentation_name": "coverage",
                    "summary_kind": "coverage.py",
                    "measurement_scope": "controller_process",
                },
                operations=(
                    CapabilityOperationBinding("instrumentation.collect"),
                ),
            ),
            CapabilityDescriptor(
                name=COSECHA_INSTRUMENTATION_STRUCTURED_SUMMARY,
                level="supported",
                metadata={"payload_formats": ["json"], "serializable": True},
                operations=(
                    CapabilityOperationBinding("instrumentation.collect"),
                ),
            ),
        ),
    )

    assert COSECHA_INSTRUMENTATION_CATALOG.is_component_snapshot_compliant(
        snapshot,
    )


def test_cosecha_engine_planning_profile_does_not_require_run_labels() -> None:
    snapshot = ComponentCapabilitySnapshot(
        component_name="planner-only",
        identity=ComponentIdentity(
            interface=COSECHA_ENGINE_INTERFACE,
            provider="planner-only",
            version="1",
        ),
        capabilities=(
            CapabilityDescriptor(
                name=COSECHA_ENGINE_SELECTION_LABELS,
                level="supported",
                metadata={
                    "label_sources": ["analysis"],
                    "supports_glob_matching": False,
                },
                operations=(
                    CapabilityOperationBinding("plan.analyze"),
                    CapabilityOperationBinding("plan.explain"),
                    CapabilityOperationBinding("plan.simulate"),
                ),
            ),
            CapabilityDescriptor(
                name=COSECHA_ENGINE_PLAN_EXPLANATION,
                level="supported",
                operations=(
                    CapabilityOperationBinding("plan.analyze"),
                    CapabilityOperationBinding("plan.explain"),
                    CapabilityOperationBinding("plan.simulate"),
                ),
            ),
        ),
    )

    assert COSECHA_ENGINE_CATALOG.is_component_snapshot_profile_compliant(
        snapshot,
        COSECHA_ENGINE_PLANNING_PROFILE,
    )


def test_cosecha_reporter_structured_profile_requires_output_kind() -> None:
    snapshot = ComponentCapabilitySnapshot(
        component_name="json",
        identity=ComponentIdentity(
            interface=COSECHA_REPORTER_INTERFACE,
            provider="json",
            version="1",
        ),
        capabilities=(
            CapabilityDescriptor(
                name=COSECHA_REPORTER_STRUCTURED_OUTPUT,
                level="supported",
                metadata={
                    "output_kind": "structured",
                    "artifact_formats": ["json"],
                },
                operations=(
                    CapabilityOperationBinding("reporter.print_report"),
                ),
            ),
            CapabilityDescriptor(
                name=COSECHA_REPORTER_ARTIFACT_OUTPUT,
                level="supported",
                metadata={"artifact_formats": ["json"]},
                operations=(
                    CapabilityOperationBinding("reporter.print_report"),
                ),
            ),
        ),
    )

    assert COSECHA_REPORTER_CATALOG.is_component_snapshot_profile_compliant(
        snapshot,
        COSECHA_REPORTER_STRUCTURED_PROFILE,
    )
