from __future__ import annotations

import msgspec

from cxp.catalogs.base import (
    CapabilityCatalog,
    CapabilityTelemetry,
    CatalogCapability,
    CatalogOperation,
    TelemetryFieldRequirement,
    TelemetrySpanSpec,
    register_catalog,
)

COSECHA_ENGINE_INTERFACE = 'cosecha/engine'

COSECHA_ENGINE_LIFECYCLE = 'engine_lifecycle'
COSECHA_ENGINE_TEST_LIFECYCLE = 'test_lifecycle'
COSECHA_ENGINE_DRAFT_VALIDATION = 'draft_validation'
COSECHA_ENGINE_SELECTION_LABELS = 'selection_labels'
COSECHA_ENGINE_DEFINITION_KNOWLEDGE = 'definition_knowledge'
COSECHA_ENGINE_PLAN_EXPLANATION = 'plan_explanation'
COSECHA_ENGINE_STATIC_DEFINITION_DISCOVERY = 'static_definition_discovery'
COSECHA_ENGINE_ON_DEMAND_DEFINITION_MATERIALIZATION = (
    'on_demand_definition_materialization'
)
COSECHA_ENGINE_DEPENDENCY_KNOWLEDGE = 'engine_dependency_knowledge'

COSECHA_ENGINE_COLLECT = 'collect'
COSECHA_ENGINE_SESSION_START = 'session.start'
COSECHA_ENGINE_SESSION_FINISH = 'session.finish'
COSECHA_ENGINE_TEST_START = 'test.start'
COSECHA_ENGINE_TEST_FINISH = 'test.finish'
COSECHA_ENGINE_TEST_EXECUTE = 'test.execute'
COSECHA_ENGINE_TEST_PHASE = 'test.phase'
COSECHA_ENGINE_DRAFT_VALIDATE = 'draft.validate'
COSECHA_ENGINE_DEFINITION_RESOLVE = 'definition.resolve'
COSECHA_ENGINE_KNOWLEDGE_QUERY_TESTS = 'knowledge.query_tests'
COSECHA_ENGINE_KNOWLEDGE_QUERY_DEFINITIONS = 'knowledge.query_definitions'
COSECHA_ENGINE_KNOWLEDGE_QUERY_REGISTRY_ITEMS = (
    'knowledge.query_registry_items'
)
COSECHA_ENGINE_PLAN_ANALYZE = 'plan.analyze'
COSECHA_ENGINE_PLAN_EXPLAIN = 'plan.explain'
COSECHA_ENGINE_PLAN_SIMULATE = 'plan.simulate'
COSECHA_ENGINE_DEPENDENCIES_DESCRIBE = 'dependencies.describe'

_ENGINE_NAME_FIELD = TelemetryFieldRequirement(name='cosecha.engine.name')
_OPERATION_NAME_FIELD = TelemetryFieldRequirement(name='cosecha.operation.name')
_OUTCOME_FIELD = TelemetryFieldRequirement(name='cosecha.outcome')
_NODE_ID_FIELD = TelemetryFieldRequirement(name='cosecha.node.id')
_NODE_STABLE_ID_FIELD = TelemetryFieldRequirement(
    name='cosecha.node.stable_id'
)
_PHASE_FIELD = TelemetryFieldRequirement(name='cosecha.phase')


class SelectionLabelsMetadata(msgspec.Struct, frozen=True):
    label_sources: tuple[str, ...]
    supports_glob_matching: bool = False


class DefinitionKnowledgeMetadata(msgspec.Struct, frozen=True):
    knowledge_origin_kinds: tuple[str, ...]
    knowledge_scopes: tuple[str, ...]
    supports_fresh_resolution: bool = False
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
            'Canonical catalog for Cosecha engines with normalized knowledge, '
            'planning, execution, and dependency semantics.'
        ),
        capabilities=(
            CatalogCapability(
                name=COSECHA_ENGINE_DRAFT_VALIDATION,
                description='Validate draft content before collection or run.',
                telemetry=_engine_span(
                    'engine.draft.validate',
                    _ENGINE_NAME_FIELD,
                    _OPERATION_NAME_FIELD,
                    _OUTCOME_FIELD,
                    description='Engine draft validation span.',
                ),
                operations=(
                    CatalogOperation(
                        name=COSECHA_ENGINE_DRAFT_VALIDATE,
                        result_type='draft.validation',
                    ),
                ),
            ),
            CatalogCapability(
                name=COSECHA_ENGINE_SELECTION_LABELS,
                description='Publish selection labels used in planning and run.',
                metadata_schema=SelectionLabelsMetadata,
                operations=(
                    CatalogOperation(
                        name=COSECHA_ENGINE_PLAN_ANALYZE,
                        result_type='plan.analysis',
                    ),
                    CatalogOperation(
                        name=COSECHA_ENGINE_PLAN_EXPLAIN,
                        result_type='plan.explanation',
                    ),
                    CatalogOperation(
                        name=COSECHA_ENGINE_PLAN_SIMULATE,
                        result_type='plan.simulation',
                    ),
                ),
            ),
            CatalogCapability(
                name=COSECHA_ENGINE_DEFINITION_KNOWLEDGE,
                description=(
                    'Publish definition knowledge from project, library, '
                    'or registry sources.'
                ),
                metadata_schema=DefinitionKnowledgeMetadata,
                telemetry=_engine_span(
                    'engine.definition.resolve',
                    _ENGINE_NAME_FIELD,
                    _OPERATION_NAME_FIELD,
                    _OUTCOME_FIELD,
                    description='Engine definition-resolution span.',
                ),
                operations=(
                    CatalogOperation(
                        name=COSECHA_ENGINE_DEFINITION_RESOLVE,
                        result_type='definition.resolution',
                    ),
                    CatalogOperation(
                        name=COSECHA_ENGINE_KNOWLEDGE_QUERY_TESTS,
                        result_type='knowledge.tests',
                    ),
                    CatalogOperation(
                        name=COSECHA_ENGINE_KNOWLEDGE_QUERY_DEFINITIONS,
                        result_type='knowledge.definitions',
                    ),
                    CatalogOperation(
                        name=COSECHA_ENGINE_KNOWLEDGE_QUERY_REGISTRY_ITEMS,
                        result_type='knowledge.registry_items',
                    ),
                ),
            ),
            CatalogCapability(
                name=COSECHA_ENGINE_PLAN_EXPLANATION,
                description='Analyze, explain, or simulate execution plans.',
                telemetry=CapabilityTelemetry(
                    spans=(
                        TelemetrySpanSpec(
                            name='engine.plan.analyze',
                            required_attributes=(
                                _ENGINE_NAME_FIELD,
                                _OPERATION_NAME_FIELD,
                                _OUTCOME_FIELD,
                            ),
                        ),
                        TelemetrySpanSpec(
                            name='engine.plan.explain',
                            required_attributes=(
                                _ENGINE_NAME_FIELD,
                                _OPERATION_NAME_FIELD,
                                _OUTCOME_FIELD,
                            ),
                        ),
                        TelemetrySpanSpec(
                            name='engine.plan.simulate',
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
                        result_type='plan.analysis',
                    ),
                    CatalogOperation(
                        name=COSECHA_ENGINE_PLAN_EXPLAIN,
                        result_type='plan.explanation',
                    ),
                    CatalogOperation(
                        name=COSECHA_ENGINE_PLAN_SIMULATE,
                        result_type='plan.simulation',
                    ),
                ),
            ),
            CatalogCapability(
                name=COSECHA_ENGINE_STATIC_DEFINITION_DISCOVERY,
                description=(
                    'Discover executable artifacts or definitions without '
                    'running the full engine.'
                ),
                metadata_schema=StaticDefinitionDiscoveryMetadata,
                operations=(
                    CatalogOperation(
                        name=COSECHA_ENGINE_KNOWLEDGE_QUERY_TESTS,
                        result_type='knowledge.tests',
                    ),
                    CatalogOperation(
                        name=COSECHA_ENGINE_KNOWLEDGE_QUERY_DEFINITIONS,
                        result_type='knowledge.definitions',
                    ),
                ),
            ),
            CatalogCapability(
                name=COSECHA_ENGINE_ON_DEMAND_DEFINITION_MATERIALIZATION,
                description=(
                    'Materialize definition knowledge on demand instead of '
                    'eagerly.'
                ),
                metadata_schema=OnDemandDefinitionMaterializationMetadata,
                operations=(
                    CatalogOperation(
                        name=COSECHA_ENGINE_DEFINITION_RESOLVE,
                        result_type='definition.resolution',
                    ),
                ),
            ),
            CatalogCapability(
                name=COSECHA_ENGINE_DEPENDENCY_KNOWLEDGE,
                description=(
                    'Publish cross-engine dependency knowledge and '
                    'projection policies.'
                ),
                telemetry=_engine_span(
                    'engine.dependencies.describe',
                    _ENGINE_NAME_FIELD,
                    _OPERATION_NAME_FIELD,
                    _OUTCOME_FIELD,
                    description='Engine dependency-description span.',
                ),
                operations=(
                    CatalogOperation(
                        name=COSECHA_ENGINE_DEPENDENCIES_DESCRIBE,
                        result_type='engine.dependencies',
                    ),
                ),
            ),
            CatalogCapability(
                name=COSECHA_ENGINE_LIFECYCLE,
                description='Collect tests and manage engine session lifecycle.',
                telemetry=CapabilityTelemetry(
                    spans=(
                        TelemetrySpanSpec(
                            name='engine.collect',
                            required_attributes=(
                                _ENGINE_NAME_FIELD,
                                _OPERATION_NAME_FIELD,
                                _OUTCOME_FIELD,
                            ),
                        ),
                        TelemetrySpanSpec(
                            name='engine.session.start',
                            required_attributes=(
                                _ENGINE_NAME_FIELD,
                                _OPERATION_NAME_FIELD,
                                _OUTCOME_FIELD,
                            ),
                        ),
                        TelemetrySpanSpec(
                            name='engine.session.finish',
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
                        result_type='collection.result',
                    ),
                    CatalogOperation(
                        name=COSECHA_ENGINE_SESSION_START,
                        result_type='none',
                    ),
                    CatalogOperation(
                        name=COSECHA_ENGINE_SESSION_FINISH,
                        result_type='none',
                    ),
                ),
            ),
            CatalogCapability(
                name=COSECHA_ENGINE_TEST_LIFECYCLE,
                description='Start, execute phases, and finish engine-owned tests.',
                telemetry=CapabilityTelemetry(
                    spans=(
                        TelemetrySpanSpec(
                            name='engine.test.start',
                            required_attributes=(
                                _ENGINE_NAME_FIELD,
                                _OPERATION_NAME_FIELD,
                                _OUTCOME_FIELD,
                                _NODE_ID_FIELD,
                                _NODE_STABLE_ID_FIELD,
                            ),
                        ),
                        TelemetrySpanSpec(
                            name='engine.test.finish',
                            required_attributes=(
                                _ENGINE_NAME_FIELD,
                                _OPERATION_NAME_FIELD,
                                _OUTCOME_FIELD,
                                _NODE_ID_FIELD,
                                _NODE_STABLE_ID_FIELD,
                            ),
                        ),
                        TelemetrySpanSpec(
                            name='engine.test.execute',
                            required_attributes=(
                                _ENGINE_NAME_FIELD,
                                _OPERATION_NAME_FIELD,
                                _OUTCOME_FIELD,
                                _NODE_ID_FIELD,
                                _NODE_STABLE_ID_FIELD,
                            ),
                        ),
                        TelemetrySpanSpec(
                            name='engine.test.phase',
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
                        result_type='none',
                    ),
                    CatalogOperation(
                        name=COSECHA_ENGINE_TEST_FINISH,
                        result_type='none',
                    ),
                    CatalogOperation(
                        name=COSECHA_ENGINE_TEST_EXECUTE,
                        result_type='test.execution',
                    ),
                    CatalogOperation(
                        name=COSECHA_ENGINE_TEST_PHASE,
                        result_type='test.phase',
                    ),
                ),
            ),
        ),
    )
)

__all__ = (
    'COSECHA_ENGINE_CATALOG',
    'COSECHA_ENGINE_COLLECT',
    'COSECHA_ENGINE_DEFINITION_KNOWLEDGE',
    'COSECHA_ENGINE_DEFINITION_RESOLVE',
    'COSECHA_ENGINE_DEPENDENCIES_DESCRIBE',
    'COSECHA_ENGINE_DEPENDENCY_KNOWLEDGE',
    'COSECHA_ENGINE_DRAFT_VALIDATE',
    'COSECHA_ENGINE_DRAFT_VALIDATION',
    'COSECHA_ENGINE_INTERFACE',
    'COSECHA_ENGINE_KNOWLEDGE_QUERY_DEFINITIONS',
    'COSECHA_ENGINE_KNOWLEDGE_QUERY_REGISTRY_ITEMS',
    'COSECHA_ENGINE_KNOWLEDGE_QUERY_TESTS',
    'COSECHA_ENGINE_LIFECYCLE',
    'COSECHA_ENGINE_ON_DEMAND_DEFINITION_MATERIALIZATION',
    'COSECHA_ENGINE_PLAN_ANALYZE',
    'COSECHA_ENGINE_PLAN_EXPLAIN',
    'COSECHA_ENGINE_PLAN_EXPLANATION',
    'COSECHA_ENGINE_PLAN_SIMULATE',
    'COSECHA_ENGINE_SELECTION_LABELS',
    'COSECHA_ENGINE_SESSION_FINISH',
    'COSECHA_ENGINE_SESSION_START',
    'COSECHA_ENGINE_STATIC_DEFINITION_DISCOVERY',
    'COSECHA_ENGINE_TEST_FINISH',
    'COSECHA_ENGINE_TEST_EXECUTE',
    'COSECHA_ENGINE_TEST_LIFECYCLE',
    'COSECHA_ENGINE_TEST_PHASE',
    'COSECHA_ENGINE_TEST_START',
)
