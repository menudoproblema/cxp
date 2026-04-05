from __future__ import annotations

import msgspec

from cxp import (
    PLAN_RUN_EXECUTION_CATALOG,
    CapabilityAttribute,
    CapabilityCatalog,
    CapabilityDescriptor,
    CapabilityOperationBinding,
    CatalogCapability,
    CatalogOperation,
    ComponentCapabilitySnapshot,
    ComponentDependencyRule,
    ComponentIdentity,
    ConformanceTier,
    DescriptorValidationResult,
    UnknownCapabilityOperations,
)


class PlanningMetadata(msgspec.Struct, frozen=True):
    mode: str
    explain: bool = False


def test_capability_descriptor_exposes_helpers() -> None:
    descriptor = CapabilityDescriptor(
        name="planning",
        level="supported",
        attributes=(CapabilityAttribute(name="mode", value="strict"),),
        operations=(
            CapabilityOperationBinding(
                operation_name="plan.analyze",
                result_type="plan.analyzed",
            ),
            CapabilityOperationBinding(
                operation_name="plan.explain",
                result_type="plan.explained",
            ),
        ),
    )

    assert descriptor.attribute_names() == ("mode",)
    assert descriptor.operation_names() == ("plan.analyze", "plan.explain")
    assert descriptor.has_operation("plan.analyze") is True
    assert descriptor.get_operation("plan.explain") is not None
    assert descriptor.is_offered() is True


def test_component_snapshot_can_project_to_negotiated_capability_matrix() -> None:
    snapshot = ComponentCapabilitySnapshot(
        component_name="gherkin",
        identity=ComponentIdentity(
            interface="execution/plan-run",
            provider="gherkin",
            version="1.0.0",
        ),
        capabilities=(
            CapabilityDescriptor(name="run", level="supported"),
            CapabilityDescriptor(name="planning", level="accepted_noop"),
            CapabilityDescriptor(name="input_validation", level="unsupported"),
        ),
    )

    matrix = snapshot.as_negotiated_capability_matrix()

    assert snapshot.capability_names() == (
        "run",
        "planning",
        "input_validation",
    )
    assert snapshot.capability_names(include_unsupported=False) == (
        "run",
        "planning",
    )
    assert tuple(capability.name for capability in matrix.capabilities) == ("run",)
    assert tuple(
        capability.name
        for capability in snapshot.as_capability_matrix_with_noop().capabilities
    ) == ("run", "planning")


def test_catalog_validates_component_snapshot_operations_and_metadata() -> None:
    catalog = CapabilityCatalog(
        interface="execution/plan-run",
        capabilities=(
            CatalogCapability(
                name="planning",
                operations=(
                    CatalogOperation(name="plan.analyze"),
                    CatalogOperation(name="plan.explain"),
                ),
                metadata_schema=PlanningMetadata,
            ),
            CatalogCapability(
                name="run",
                operations=(CatalogOperation(name="run"),),
            ),
        ),
        tiers=(
            ConformanceTier(
                name="core",
                required_capabilities=("run", "planning"),
            ),
        ),
    )
    snapshot = ComponentCapabilitySnapshot(
        component_name="pytest",
        capabilities=(
            CapabilityDescriptor(
                name="planning",
                level="supported",
                operations=(
                    CapabilityOperationBinding(
                        operation_name="plan.analyze",
                    ),
                    CapabilityOperationBinding(
                        operation_name="plan.explain",
                    ),
                ),
                metadata={"mode": "strict", "explain": True},
            ),
            CapabilityDescriptor(
                name="run",
                level="supported",
                operations=(CapabilityOperationBinding(operation_name="run"),),
            ),
        ),
    )

    validation = catalog.validate_component_snapshot(snapshot)

    assert isinstance(validation, DescriptorValidationResult)
    assert validation.is_valid() is True
    assert (
        catalog.is_component_snapshot_compliant(
            snapshot,
            required_tier="core",
        )
        is True
    )


def test_catalog_reports_unknown_operations_for_descriptor_snapshot() -> None:
    snapshot = ComponentCapabilitySnapshot(
        component_name="pytest",
        capabilities=(
            CapabilityDescriptor(
                name="planning",
                level="supported",
                operations=(
                    CapabilityOperationBinding(
                        operation_name="plan.unknown",
                    ),
                ),
            ),
        ),
    )

    validation = PLAN_RUN_EXECUTION_CATALOG.validate_component_snapshot(snapshot)

    assert validation.unknown_capabilities == ()
    assert validation.invalid_metadata == ()
    assert validation.interface_mismatch is None
    assert validation.unknown_operations == (
        UnknownCapabilityOperations(
            capability_name="planning",
            operation_names=("plan.unknown",),
        ),
    )
    assert validation.messages() == (
        "Unknown operations for capability 'planning': plan.unknown",
    )
    assert PLAN_RUN_EXECUTION_CATALOG.is_component_snapshot_compliant(snapshot) is False


def test_catalog_reports_invalid_metadata_for_descriptor_snapshot() -> None:
    catalog = CapabilityCatalog(
        interface="execution/plan-run",
        capabilities=(
            CatalogCapability(
                name="planning",
                operations=(CatalogOperation(name="plan.analyze"),),
                metadata_schema=PlanningMetadata,
            ),
        ),
    )
    snapshot = ComponentCapabilitySnapshot(
        component_name="pytest",
        capabilities=(
            CapabilityDescriptor(
                name="planning",
                level="supported",
                operations=(
                    CapabilityOperationBinding(
                        operation_name="plan.analyze",
                    ),
                ),
                metadata={"mode": 3},
            ),
        ),
    )

    validation = catalog.validate_component_snapshot(snapshot)

    assert validation.invalid_metadata == ("planning",)
    assert validation.interface_mismatch is None
    assert validation.messages() == ("Invalid metadata for capabilities: planning",)
    assert catalog.is_component_snapshot_compliant(snapshot) is False


def test_catalog_reports_interface_mismatch_for_component_snapshot() -> None:
    snapshot = ComponentCapabilitySnapshot(
        component_name="pytest",
        identity=ComponentIdentity(
            interface="database/mongodb",
            provider="pytest",
            version="1.0.0",
        ),
        capabilities=(
            CapabilityDescriptor(name="run", level="supported"),
            CapabilityDescriptor(name="planning", level="supported"),
        ),
    )

    validation = PLAN_RUN_EXECUTION_CATALOG.validate_component_snapshot(snapshot)

    assert validation.interface_mismatch == "database/mongodb"
    assert validation.expected_interface == "execution/plan-run"
    assert validation.interface_mismatch_message == (
        "Interface mismatch: expected 'execution/plan-run' but received "
        "'database/mongodb'"
    )
    assert validation.messages() == (
        "Interface mismatch: expected 'execution/plan-run' but received "
        "'database/mongodb'",
    )
    assert validation.is_valid() is False
    assert PLAN_RUN_EXECUTION_CATALOG.is_component_snapshot_compliant(snapshot) is False


def test_unsupported_capabilities_do_not_count_for_tier_compliance() -> None:
    snapshot = ComponentCapabilitySnapshot(
        component_name="pytest",
        capabilities=(
            CapabilityDescriptor(name="run", level="supported"),
            CapabilityDescriptor(name="planning", level="unsupported"),
        ),
    )

    assert (
        PLAN_RUN_EXECUTION_CATALOG.is_component_snapshot_compliant(
            snapshot,
            required_tier="planned",
        )
        is False
    )


def test_accepted_noop_counts_for_structural_compliance() -> None:
    snapshot = ComponentCapabilitySnapshot(
        component_name="pytest",
        capabilities=(
            CapabilityDescriptor(name="run", level="supported"),
            CapabilityDescriptor(name="planning", level="accepted_noop"),
        ),
    )

    assert (
        PLAN_RUN_EXECUTION_CATALOG.is_component_snapshot_compliant(
            snapshot,
            required_tier="planned",
        )
        is True
    )


def test_descriptors_roundtrip_with_msgspec() -> None:
    snapshot = ComponentCapabilitySnapshot(
        component_name="gherkin",
        component_kind="engine",
        identity=ComponentIdentity(
            interface="execution/plan-run",
            provider="gherkin",
            version="1.0.0",
        ),
        capabilities=(
            CapabilityDescriptor(
                name="planning",
                level="supported",
                operations=(
                    CapabilityOperationBinding(
                        operation_name="plan.analyze",
                        result_type="plan.analyzed",
                    ),
                ),
            ),
        ),
    )

    encoded = msgspec.json.encode(snapshot)
    decoded = msgspec.json.decode(encoded, type=ComponentCapabilitySnapshot)

    assert decoded.component_name == "gherkin"
    assert decoded.identity is not None
    assert decoded.capabilities[0].operations[0].operation_name == "plan.analyze"


def test_component_dependency_rule_supports_generic_relationships() -> None:
    rule = ComponentDependencyRule(
        source_component="gherkin",
        target_component="pytest",
        dependency_kind="knowledge",
        projection_policy="diagnostic_only",
        required_capabilities=("planning",),
        required_operations=("plan.explain", "knowledge.query_definitions"),
    )

    assert rule.source_component == "gherkin"
    assert rule.required_capabilities == ("planning",)
    assert rule.required_operations == (
        "plan.explain",
        "knowledge.query_definitions",
    )
