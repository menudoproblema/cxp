from __future__ import annotations

import msgspec

from cxp.catalogs.base import (
    CapabilityCatalog,
    CapabilityProfile,
    CapabilityRequirement,
    CapabilityTelemetry,
    CatalogCapability,
    CatalogOperation,
    ConformanceTier,
    TelemetryFieldRequirement,
    TelemetrySpanSpec,
    register_catalog,
)

COSECHA_ENGINE_INTERFACE = "cosecha/engine"

COSECHA_ENGINE_LIFECYCLE = "engine_lifecycle"
COSECHA_ENGINE_TEST_LIFECYCLE = "test_lifecycle"
COSECHA_ENGINE_DRAFT_VALIDATION = "draft_validation"
COSECHA_ENGINE_SELECTION_LABELS = "selection_labels"
COSECHA_ENGINE_PROJECT_DEFINITION_KNOWLEDGE = (
    "project_definition_knowledge"
)
COSECHA_ENGINE_LIBRARY_DEFINITION_KNOWLEDGE = (
    "library_definition_knowledge"
)
COSECHA_ENGINE_PROJECT_REGISTRY_KNOWLEDGE = (
    "project_registry_knowledge"
)
COSECHA_ENGINE_PLAN_EXPLANATION = "plan_explanation"
COSECHA_ENGINE_STATIC_DEFINITION_DISCOVERY = (
    "static_definition_discovery"
)
COSECHA_ENGINE_ON_DEMAND_DEFINITION_MATERIALIZATION = (
    "on_demand_definition_materialization"
)
COSECHA_ENGINE_DEPENDENCY_KNOWLEDGE = "engine_dependency_knowledge"

COSECHA_ENGINE_COLLECT = "collect"
COSECHA_ENGINE_RUN = "run"
COSECHA_ENGINE_SESSION_START = "session.start"
COSECHA_ENGINE_SESSION_FINISH = "session.finish"
COSECHA_ENGINE_TEST_START = "test.start"
COSECHA_ENGINE_TEST_FINISH = "test.finish"
COSECHA_ENGINE_TEST_EXECUTE = "test.execute"
COSECHA_ENGINE_TEST_PHASE = "test.phase"
COSECHA_ENGINE_DRAFT_VALIDATE = "draft.validate"
COSECHA_ENGINE_DEFINITION_RESOLVE = "definition.resolve"
COSECHA_ENGINE_KNOWLEDGE_QUERY_TESTS = "knowledge.query_tests"
COSECHA_ENGINE_KNOWLEDGE_QUERY_DEFINITIONS = "knowledge.query_definitions"
COSECHA_ENGINE_KNOWLEDGE_QUERY_REGISTRY_ITEMS = (
    "knowledge.query_registry_items"
)
COSECHA_ENGINE_PLAN_ANALYZE = "plan.analyze"
COSECHA_ENGINE_PLAN_EXPLAIN = "plan.explain"
COSECHA_ENGINE_PLAN_SIMULATE = "plan.simulate"
COSECHA_ENGINE_DEPENDENCIES_DESCRIBE = "dependencies.describe"

COSECHA_ENGINE_CORE_TIER = "core"
COSECHA_ENGINE_KNOWLEDGE_TIER = "knowledge"
COSECHA_ENGINE_PLANNING_TIER = "planning"
COSECHA_ENGINE_INTEGRATED_TIER = "integrated"

COSECHA_ENGINE_CORE_PROFILE_NAME = "cosecha-engine-core"
COSECHA_ENGINE_KNOWLEDGE_PROFILE_NAME = "cosecha-engine-knowledge"
COSECHA_ENGINE_PLANNING_PROFILE_NAME = "cosecha-engine-planning"
COSECHA_ENGINE_INTEGRATED_PROFILE_NAME = "cosecha-engine-integrated"

_ENGINE_NAME_FIELD = TelemetryFieldRequirement(name="cosecha.engine.name")
_OPERATION_NAME_FIELD = TelemetryFieldRequirement(name="cosecha.operation.name")
_OUTCOME_FIELD = TelemetryFieldRequirement(name="cosecha.outcome")
_NODE_ID_FIELD = TelemetryFieldRequirement(name="cosecha.node.id")
_NODE_STABLE_ID_FIELD = TelemetryFieldRequirement(
    name="cosecha.node.stable_id"
)
_PHASE_FIELD = TelemetryFieldRequirement(name="cosecha.phase")


class SelectionLabelsMetadata(msgspec.Struct, frozen=True):
    label_sources: tuple[str, ...]
    supports_glob_matching: bool = False


class DefinitionKnowledgeMetadata(msgspec.Struct, frozen=True):
    knowledge_origin_kind: tuple[str, ...]
    knowledge_scopes: tuple[str, ...]
    supports_fresh_resolution: bool = False
    supports_knowledge_base_projection: bool = False


class RegistryKnowledgeMetadata(msgspec.Struct, frozen=True):
    registry_scopes: tuple[str, ...]
    supports_knowledge_base_projection: bool = False


class StaticDefinitionDiscoveryMetadata(msgspec.Struct, frozen=True):
    discovery_backends: tuple[str, ...]


class OnDemandDefinitionMaterializationMetadata(msgspec.Struct, frozen=True):
    materialization_granularities: tuple[str, ...]


def _engine_span(
    name: str,
    *required_attributes: TelemetryFieldRequirement,
    description: str,
) -> CapabilityTelemetry:
    return CapabilityTelemetry(
        spans=(
            TelemetrySpanSpec(
                name=name,
                required_attributes=required_attributes,
                description=description,
            ),
        ),
    )


COSECHA_ENGINE_CATALOG = register_catalog(
    CapabilityCatalog(
        interface=COSECHA_ENGINE_INTERFACE,
        description=(
            "Canonical catalog for Cosecha engines with explicit knowledge, "
            "planning, lifecycle and cross-engine dependency semantics."
        ),
        capabilities=(
            CatalogCapability(
                name=COSECHA_ENGINE_LIFECYCLE,
                description="Collect tests and manage engine session lifecycle.",
                telemetry=CapabilityTelemetry(
                    spans=(
                        TelemetrySpanSpec(
                            name="engine.collect",
                            required_attributes=(
                                _ENGINE_NAME_FIELD,
                                _OPERATION_NAME_FIELD,
                                _OUTCOME_FIELD,
                            ),
                        ),
                        TelemetrySpanSpec(
                            name="engine.session.start",
                            required_attributes=(
                                _ENGINE_NAME_FIELD,
                                _OPERATION_NAME_FIELD,
                                _OUTCOME_FIELD,
                            ),
                        ),
                        TelemetrySpanSpec(
                            name="engine.session.finish",
                            required_attributes=(
                                _ENGINE_NAME_FIELD,
                                _OPERATION_NAME_FIELD,
                                _OUTCOME_FIELD,
                            ),
                        ),
                    ),
                ),
                operations=(
                    CatalogOperation(
                        name=COSECHA_ENGINE_COLLECT,
                        result_type="collection.result",
                    ),
                    CatalogOperation(
                        name=COSECHA_ENGINE_SESSION_START,
                        result_type="none",
                    ),
                    CatalogOperation(
                        name=COSECHA_ENGINE_SESSION_FINISH,
                        result_type="none",
                    ),
                ),
            ),
            CatalogCapability(
                name=COSECHA_ENGINE_TEST_LIFECYCLE,
                description="Execute and track test phases for a collected node.",
                telemetry=CapabilityTelemetry(
                    spans=(
                        TelemetrySpanSpec(
                            name="engine.test.start",
                            required_attributes=(
                                _ENGINE_NAME_FIELD,
                                _OPERATION_NAME_FIELD,
                                _OUTCOME_FIELD,
                                _NODE_ID_FIELD,
                                _NODE_STABLE_ID_FIELD,
                            ),
                        ),
                        TelemetrySpanSpec(
                            name="engine.test.finish",
                            required_attributes=(
                                _ENGINE_NAME_FIELD,
                                _OPERATION_NAME_FIELD,
                                _OUTCOME_FIELD,
                                _NODE_ID_FIELD,
                                _NODE_STABLE_ID_FIELD,
                            ),
                        ),
                        TelemetrySpanSpec(
                            name="engine.test.execute",
                            required_attributes=(
                                _ENGINE_NAME_FIELD,
                                _OPERATION_NAME_FIELD,
                                _OUTCOME_FIELD,
                                _NODE_ID_FIELD,
                                _NODE_STABLE_ID_FIELD,
                            ),
                        ),
                        TelemetrySpanSpec(
                            name="engine.test.phase",
                            required_attributes=(
                                _ENGINE_NAME_FIELD,
                                _OPERATION_NAME_FIELD,
                                _OUTCOME_FIELD,
                                _NODE_ID_FIELD,
                                _NODE_STABLE_ID_FIELD,
                                _PHASE_FIELD,
                            ),
                        ),
                    ),
                ),
                operations=(
                    CatalogOperation(
                        name=COSECHA_ENGINE_TEST_START,
                        result_type="none",
                    ),
                    CatalogOperation(
                        name=COSECHA_ENGINE_TEST_FINISH,
                        result_type="none",
                    ),
                    CatalogOperation(
                        name=COSECHA_ENGINE_TEST_EXECUTE,
                        result_type="test.result",
                    ),
                    CatalogOperation(
                        name=COSECHA_ENGINE_TEST_PHASE,
                        result_type="test.phase",
                    ),
                ),
            ),
            CatalogCapability(
                name=COSECHA_ENGINE_DRAFT_VALIDATION,
                description="Validate draft content before collection or run.",
                telemetry=_engine_span(
                    "engine.draft.validate",
                    _ENGINE_NAME_FIELD,
                    _OPERATION_NAME_FIELD,
                    _OUTCOME_FIELD,
                    description="Engine draft validation span.",
                ),
                operations=(
                    CatalogOperation(
                        name=COSECHA_ENGINE_DRAFT_VALIDATE,
                        result_type="draft.validation",
                    ),
                ),
            ),
            CatalogCapability(
                name=COSECHA_ENGINE_SELECTION_LABELS,
                description="Publish labels used in filtering, planning and run.",
                metadata_schema=SelectionLabelsMetadata,
                operations=(
                    CatalogOperation(
                        name=COSECHA_ENGINE_RUN,
                        result_type="run.result",
                    ),
                    CatalogOperation(
                        name=COSECHA_ENGINE_PLAN_ANALYZE,
                        result_type="plan.analysis",
                    ),
                    CatalogOperation(
                        name=COSECHA_ENGINE_PLAN_EXPLAIN,
                        result_type="plan.explanation",
                    ),
                    CatalogOperation(
                        name=COSECHA_ENGINE_PLAN_SIMULATE,
                        result_type="plan.simulation",
                    ),
                ),
            ),
            CatalogCapability(
                name=COSECHA_ENGINE_PROJECT_DEFINITION_KNOWLEDGE,
                description="Publish definition knowledge discovered from the project.",
                metadata_schema=DefinitionKnowledgeMetadata,
                telemetry=_engine_span(
                    "engine.definition.resolve",
                    _ENGINE_NAME_FIELD,
                    _OPERATION_NAME_FIELD,
                    _OUTCOME_FIELD,
                    description="Engine definition resolution span.",
                ),
                operations=(
                    CatalogOperation(
                        name=COSECHA_ENGINE_DEFINITION_RESOLVE,
                        result_type="definition.resolution",
                    ),
                    CatalogOperation(
                        name=COSECHA_ENGINE_KNOWLEDGE_QUERY_TESTS,
                        result_type="knowledge.tests",
                    ),
                    CatalogOperation(
                        name=COSECHA_ENGINE_KNOWLEDGE_QUERY_DEFINITIONS,
                        result_type="knowledge.definitions",
                    ),
                ),
            ),
            CatalogCapability(
                name=COSECHA_ENGINE_LIBRARY_DEFINITION_KNOWLEDGE,
                description="Publish definition knowledge discovered from libraries.",
                metadata_schema=DefinitionKnowledgeMetadata,
                operations=(
                    CatalogOperation(
                        name=COSECHA_ENGINE_DEFINITION_RESOLVE,
                        result_type="definition.resolution",
                    ),
                    CatalogOperation(
                        name=COSECHA_ENGINE_KNOWLEDGE_QUERY_DEFINITIONS,
                        result_type="knowledge.definitions",
                    ),
                ),
            ),
            CatalogCapability(
                name=COSECHA_ENGINE_PROJECT_REGISTRY_KNOWLEDGE,
                description="Publish project registry entries and indexed declarative context.",
                metadata_schema=RegistryKnowledgeMetadata,
                operations=(
                    CatalogOperation(
                        name=COSECHA_ENGINE_KNOWLEDGE_QUERY_REGISTRY_ITEMS,
                        result_type="knowledge.registry_items",
                    ),
                ),
            ),
            CatalogCapability(
                name=COSECHA_ENGINE_PLAN_EXPLANATION,
                description="Analyze, explain or simulate execution plans.",
                telemetry=CapabilityTelemetry(
                    spans=(
                        TelemetrySpanSpec(
                            name="engine.plan.analyze",
                            required_attributes=(
                                _ENGINE_NAME_FIELD,
                                _OPERATION_NAME_FIELD,
                                _OUTCOME_FIELD,
                            ),
                        ),
                        TelemetrySpanSpec(
                            name="engine.plan.explain",
                            required_attributes=(
                                _ENGINE_NAME_FIELD,
                                _OPERATION_NAME_FIELD,
                                _OUTCOME_FIELD,
                            ),
                        ),
                        TelemetrySpanSpec(
                            name="engine.plan.simulate",
                            required_attributes=(
                                _ENGINE_NAME_FIELD,
                                _OPERATION_NAME_FIELD,
                                _OUTCOME_FIELD,
                            ),
                        ),
                    ),
                ),
                operations=(
                    CatalogOperation(
                        name=COSECHA_ENGINE_PLAN_ANALYZE,
                        result_type="plan.analysis",
                    ),
                    CatalogOperation(
                        name=COSECHA_ENGINE_PLAN_EXPLAIN,
                        result_type="plan.explanation",
                    ),
                    CatalogOperation(
                        name=COSECHA_ENGINE_PLAN_SIMULATE,
                        result_type="plan.simulation",
                    ),
                ),
            ),
            CatalogCapability(
                name=COSECHA_ENGINE_STATIC_DEFINITION_DISCOVERY,
                description="Discover tests or definitions without executing the full engine.",
                metadata_schema=StaticDefinitionDiscoveryMetadata,
                operations=(
                    CatalogOperation(
                        name=COSECHA_ENGINE_KNOWLEDGE_QUERY_TESTS,
                        result_type="knowledge.tests",
                    ),
                    CatalogOperation(
                        name=COSECHA_ENGINE_KNOWLEDGE_QUERY_DEFINITIONS,
                        result_type="knowledge.definitions",
                    ),
                ),
            ),
            CatalogCapability(
                name=COSECHA_ENGINE_ON_DEMAND_DEFINITION_MATERIALIZATION,
                description="Materialize definition knowledge on demand.",
                metadata_schema=OnDemandDefinitionMaterializationMetadata,
                operations=(
                    CatalogOperation(
                        name=COSECHA_ENGINE_DEFINITION_RESOLVE,
                        result_type="definition.resolution",
                    ),
                ),
            ),
            CatalogCapability(
                name=COSECHA_ENGINE_DEPENDENCY_KNOWLEDGE,
                description="Publish dependency rules between engines within a mixed plan.",
                telemetry=_engine_span(
                    "engine.dependencies.describe",
                    _ENGINE_NAME_FIELD,
                    _OPERATION_NAME_FIELD,
                    _OUTCOME_FIELD,
                    description="Engine dependency description span.",
                ),
                operations=(
                    CatalogOperation(
                        name=COSECHA_ENGINE_DEPENDENCIES_DESCRIBE,
                        result_type="engine.dependencies",
                    ),
                ),
            ),
        ),
        tiers=(
            ConformanceTier(
                name=COSECHA_ENGINE_CORE_TIER,
                required_capabilities=(
                    COSECHA_ENGINE_LIFECYCLE,
                    COSECHA_ENGINE_TEST_LIFECYCLE,
                    COSECHA_ENGINE_DRAFT_VALIDATION,
                ),
                description="Minimal executable engine contract.",
            ),
            ConformanceTier(
                name=COSECHA_ENGINE_KNOWLEDGE_TIER,
                required_capabilities=(
                    COSECHA_ENGINE_LIFECYCLE,
                    COSECHA_ENGINE_TEST_LIFECYCLE,
                    COSECHA_ENGINE_DRAFT_VALIDATION,
                    COSECHA_ENGINE_PROJECT_DEFINITION_KNOWLEDGE,
                    COSECHA_ENGINE_STATIC_DEFINITION_DISCOVERY,
                ),
                description="Engine with explicit project knowledge publication.",
            ),
            ConformanceTier(
                name=COSECHA_ENGINE_PLANNING_TIER,
                required_capabilities=(
                    COSECHA_ENGINE_LIFECYCLE,
                    COSECHA_ENGINE_TEST_LIFECYCLE,
                    COSECHA_ENGINE_DRAFT_VALIDATION,
                    COSECHA_ENGINE_SELECTION_LABELS,
                    COSECHA_ENGINE_PROJECT_DEFINITION_KNOWLEDGE,
                    COSECHA_ENGINE_STATIC_DEFINITION_DISCOVERY,
                    COSECHA_ENGINE_PLAN_EXPLANATION,
                ),
                description="Engine that explains and simulates plans.",
            ),
            ConformanceTier(
                name=COSECHA_ENGINE_INTEGRATED_TIER,
                required_capabilities=(
                    COSECHA_ENGINE_LIFECYCLE,
                    COSECHA_ENGINE_TEST_LIFECYCLE,
                    COSECHA_ENGINE_DRAFT_VALIDATION,
                    COSECHA_ENGINE_PROJECT_DEFINITION_KNOWLEDGE,
                    COSECHA_ENGINE_STATIC_DEFINITION_DISCOVERY,
                    COSECHA_ENGINE_PLAN_EXPLANATION,
                    COSECHA_ENGINE_DEPENDENCY_KNOWLEDGE,
                    COSECHA_ENGINE_ON_DEMAND_DEFINITION_MATERIALIZATION,
                ),
                description="Engine integrated with knowledge and cross-engine coordination.",
            ),
        ),
    )
)

COSECHA_ENGINE_CORE_PROFILE = CapabilityProfile(
    name=COSECHA_ENGINE_CORE_PROFILE_NAME,
    interface=COSECHA_ENGINE_INTERFACE,
    requirements=(
        CapabilityRequirement(
            capability_name=COSECHA_ENGINE_LIFECYCLE,
            required_operations=(
                COSECHA_ENGINE_COLLECT,
                COSECHA_ENGINE_SESSION_START,
                COSECHA_ENGINE_SESSION_FINISH,
            ),
        ),
        CapabilityRequirement(
            capability_name=COSECHA_ENGINE_TEST_LIFECYCLE,
            required_operations=(
                COSECHA_ENGINE_TEST_START,
                COSECHA_ENGINE_TEST_FINISH,
                COSECHA_ENGINE_TEST_EXECUTE,
                COSECHA_ENGINE_TEST_PHASE,
            ),
        ),
        CapabilityRequirement(
            capability_name=COSECHA_ENGINE_DRAFT_VALIDATION,
            required_operations=(COSECHA_ENGINE_DRAFT_VALIDATE,),
        ),
    ),
    description="Core engine execution and draft validation profile.",
)

COSECHA_ENGINE_KNOWLEDGE_PROFILE = CapabilityProfile(
    name=COSECHA_ENGINE_KNOWLEDGE_PROFILE_NAME,
    interface=COSECHA_ENGINE_INTERFACE,
    requirements=(
        CapabilityRequirement(
            capability_name=COSECHA_ENGINE_PROJECT_DEFINITION_KNOWLEDGE,
            required_operations=(
                COSECHA_ENGINE_DEFINITION_RESOLVE,
                COSECHA_ENGINE_KNOWLEDGE_QUERY_DEFINITIONS,
            ),
            required_metadata_keys=(
                "knowledge_origin_kind",
                "knowledge_scopes",
            ),
        ),
        CapabilityRequirement(
            capability_name=COSECHA_ENGINE_STATIC_DEFINITION_DISCOVERY,
            required_metadata_keys=("discovery_backends",),
        ),
    ),
    description="Knowledge publishing profile for engines.",
)

COSECHA_ENGINE_PLANNING_PROFILE = CapabilityProfile(
    name=COSECHA_ENGINE_PLANNING_PROFILE_NAME,
    interface=COSECHA_ENGINE_INTERFACE,
    requirements=(
        CapabilityRequirement(
            capability_name=COSECHA_ENGINE_SELECTION_LABELS,
            required_operations=(
                COSECHA_ENGINE_PLAN_ANALYZE,
                COSECHA_ENGINE_PLAN_EXPLAIN,
                COSECHA_ENGINE_PLAN_SIMULATE,
            ),
            required_metadata_keys=(
                "label_sources",
                "supports_glob_matching",
            ),
        ),
        CapabilityRequirement(
            capability_name=COSECHA_ENGINE_PLAN_EXPLANATION,
            required_operations=(
                COSECHA_ENGINE_PLAN_ANALYZE,
                COSECHA_ENGINE_PLAN_EXPLAIN,
                COSECHA_ENGINE_PLAN_SIMULATE,
            ),
        ),
    ),
    description="Planning and selection profile for engines.",
)

COSECHA_ENGINE_INTEGRATED_PROFILE = CapabilityProfile(
    name=COSECHA_ENGINE_INTEGRATED_PROFILE_NAME,
    interface=COSECHA_ENGINE_INTERFACE,
    requirements=(
        CapabilityRequirement(
            capability_name=COSECHA_ENGINE_LIBRARY_DEFINITION_KNOWLEDGE,
            required_operations=(
                COSECHA_ENGINE_KNOWLEDGE_QUERY_DEFINITIONS,
            ),
            required_metadata_keys=(
                "knowledge_origin_kind",
                "knowledge_scopes",
            ),
        ),
        CapabilityRequirement(
            capability_name=COSECHA_ENGINE_PROJECT_REGISTRY_KNOWLEDGE,
            required_operations=(
                COSECHA_ENGINE_KNOWLEDGE_QUERY_REGISTRY_ITEMS,
            ),
            required_metadata_keys=("registry_scopes",),
        ),
        CapabilityRequirement(
            capability_name=COSECHA_ENGINE_ON_DEMAND_DEFINITION_MATERIALIZATION,
            required_operations=(COSECHA_ENGINE_DEFINITION_RESOLVE,),
            required_metadata_keys=("materialization_granularities",),
        ),
        CapabilityRequirement(
            capability_name=COSECHA_ENGINE_DEPENDENCY_KNOWLEDGE,
            required_operations=(COSECHA_ENGINE_DEPENDENCIES_DESCRIBE,),
        ),
    ),
    description="Integrated engine profile with dependency and multi-source knowledge semantics.",
)

__all__ = (
    "COSECHA_ENGINE_CATALOG",
    "COSECHA_ENGINE_COLLECT",
    "COSECHA_ENGINE_CORE_PROFILE",
    "COSECHA_ENGINE_CORE_PROFILE_NAME",
    "COSECHA_ENGINE_CORE_TIER",
    "COSECHA_ENGINE_DEPENDENCIES_DESCRIBE",
    "COSECHA_ENGINE_DEPENDENCY_KNOWLEDGE",
    "COSECHA_ENGINE_DRAFT_VALIDATE",
    "COSECHA_ENGINE_DRAFT_VALIDATION",
    "COSECHA_ENGINE_INTEGRATED_PROFILE",
    "COSECHA_ENGINE_INTEGRATED_PROFILE_NAME",
    "COSECHA_ENGINE_INTEGRATED_TIER",
    "COSECHA_ENGINE_INTERFACE",
    "COSECHA_ENGINE_KNOWLEDGE_PROFILE",
    "COSECHA_ENGINE_KNOWLEDGE_PROFILE_NAME",
    "COSECHA_ENGINE_KNOWLEDGE_TIER",
    "COSECHA_ENGINE_KNOWLEDGE_QUERY_DEFINITIONS",
    "COSECHA_ENGINE_KNOWLEDGE_QUERY_REGISTRY_ITEMS",
    "COSECHA_ENGINE_KNOWLEDGE_QUERY_TESTS",
    "COSECHA_ENGINE_LIBRARY_DEFINITION_KNOWLEDGE",
    "COSECHA_ENGINE_LIFECYCLE",
    "COSECHA_ENGINE_ON_DEMAND_DEFINITION_MATERIALIZATION",
    "COSECHA_ENGINE_PLAN_ANALYZE",
    "COSECHA_ENGINE_PLAN_EXPLAIN",
    "COSECHA_ENGINE_PLAN_EXPLANATION",
    "COSECHA_ENGINE_PLANNING_PROFILE",
    "COSECHA_ENGINE_PLANNING_PROFILE_NAME",
    "COSECHA_ENGINE_PLANNING_TIER",
    "COSECHA_ENGINE_PLAN_SIMULATE",
    "COSECHA_ENGINE_PROJECT_DEFINITION_KNOWLEDGE",
    "COSECHA_ENGINE_PROJECT_REGISTRY_KNOWLEDGE",
    "COSECHA_ENGINE_RUN",
    "COSECHA_ENGINE_SELECTION_LABELS",
    "COSECHA_ENGINE_SESSION_FINISH",
    "COSECHA_ENGINE_SESSION_START",
    "COSECHA_ENGINE_STATIC_DEFINITION_DISCOVERY",
    "COSECHA_ENGINE_TEST_EXECUTE",
    "COSECHA_ENGINE_TEST_FINISH",
    "COSECHA_ENGINE_TEST_LIFECYCLE",
    "COSECHA_ENGINE_TEST_PHASE",
    "COSECHA_ENGINE_TEST_START",
    "DefinitionKnowledgeMetadata",
    "OnDemandDefinitionMaterializationMetadata",
    "RegistryKnowledgeMetadata",
    "SelectionLabelsMetadata",
    "StaticDefinitionDiscoveryMetadata",
)
