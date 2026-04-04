import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from cxp import (
    Capability,
    CapabilityDescriptor,
    CapabilityMatrix,
    CapabilityOperationBinding,
    ComponentCapabilitySnapshot,
    ComponentDependencyRule,
    ComponentIdentity,
    collect_provider_capability_snapshot,
)

identity = ComponentIdentity(
    interface="execution/engine",
    provider="gherkin",
    version="1.0.0",
)

matrix = CapabilityMatrix(
    capabilities=(
        Capability(name="run"),
        Capability(name="planning"),
    ),
)

snapshot = ComponentCapabilitySnapshot(
    component_name="gherkin",
    component_kind="engine",
    identity=identity,
    capabilities=(
        CapabilityDescriptor(
            name="run",
            level="supported",
            summary="Executes materialized tests.",
            operations=(
                CapabilityOperationBinding(
                    operation_name="run",
                    result_type="run.result",
                ),
            ),
        ),
        CapabilityDescriptor(
            name="planning",
            level="supported",
            summary="Analyzes and explains execution plans.",
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
            metadata={"mode": "strict"},
        ),
    ),
)

dependency = ComponentDependencyRule(
    source_component="gherkin",
    target_component="pytest",
    dependency_kind="knowledge",
    projection_policy="diagnostic_only",
    required_capabilities=("planning",),
    required_operations=("plan.explain", "knowledge.query_definitions"),
)


class GherkinDescriptorProvider:
    def cxp_identity(self) -> ComponentIdentity:
        return identity

    def cxp_capability_snapshot(self) -> ComponentCapabilitySnapshot:
        return snapshot

print(matrix)
print(snapshot)
print(snapshot.as_negotiated_capability_matrix())
print(dependency)
print(collect_provider_capability_snapshot(GherkinDescriptorProvider()))
