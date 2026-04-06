from __future__ import annotations

from typing import Literal

import msgspec

from cxp.catalogs.base import (
    CapabilityCatalog,
    CapabilityProfile,
    CapabilityRequirement,
    CapabilityTelemetry,
    CatalogCapability,
    CatalogOperation,
    ConformanceTier,
    TelemetryEventSpec,
    TelemetryFieldRequirement,
    TelemetryMetricSpec,
    TelemetrySpanSpec,
    register_catalog,
)

MONGODB_INTERFACE = 'database/mongodb'


class MongoAggregationMetadata(msgspec.Struct, frozen=True):
    supportedStages: tuple[str, ...]
    supportedExpressionOperators: tuple[str, ...] = ()
    supportedGroupAccumulators: tuple[str, ...] = ()
    supportedWindowAccumulators: tuple[str, ...] = ()


class MongoSearchMetadata(msgspec.Struct, frozen=True):
    operators: tuple[str, ...]
    aggregateStage: Literal['$search'] = '$search'


class MongoVectorSearchMetadata(msgspec.Struct, frozen=True):
    similarities: tuple[str, ...]
    aggregateStage: Literal['$vectorSearch'] = '$vectorSearch'


class MongoCollationMetadata(msgspec.Struct, frozen=True):
    backend: dict[str, object] = msgspec.field(default_factory=dict)
    capabilities: dict[str, object] = msgspec.field(default_factory=dict)


class MongoPersistenceMetadata(msgspec.Struct, frozen=True):
    persistent: bool
    storageEngine: str


class MongoTopologyDiscoveryMetadata(msgspec.Struct, frozen=True):
    topologyType: str
    serverCount: int
    sdam: dict[str, object] = msgspec.field(default_factory=dict)


MONGODB_READ = 'read'
MONGODB_WRITE = 'write'
MONGODB_PERSISTENCE = 'persistence'
MONGODB_TRANSACTIONS = 'transactions'
MONGODB_CHANGE_STREAMS = 'change_streams'
MONGODB_AGGREGATION = 'aggregation'
MONGODB_SEARCH = 'search'
MONGODB_VECTOR_SEARCH = 'vector_search'
MONGODB_COLLATION = 'collation'
MONGODB_TOPOLOGY_DISCOVERY = 'topology_discovery'

MONGODB_FIND = 'find'
MONGODB_FIND_ONE = 'find_one'
MONGODB_COUNT_DOCUMENTS = 'count_documents'
MONGODB_ESTIMATED_DOCUMENT_COUNT = 'estimated_document_count'
MONGODB_DISTINCT = 'distinct'
MONGODB_INSERT_ONE = 'insert_one'
MONGODB_INSERT_MANY = 'insert_many'
MONGODB_UPDATE_ONE = 'update_one'
MONGODB_UPDATE_MANY = 'update_many'
MONGODB_REPLACE_ONE = 'replace_one'
MONGODB_DELETE_ONE = 'delete_one'
MONGODB_DELETE_MANY = 'delete_many'
MONGODB_BULK_WRITE = 'bulk_write'
MONGODB_AGGREGATE = 'aggregate'
MONGODB_WATCH = 'watch'
MONGODB_START_SESSION = 'start_session'
MONGODB_WITH_TRANSACTION = 'with_transaction'

MONGODB_CORE_TIER = 'core'
MONGODB_SEARCH_TIER = 'search'
MONGODB_PLATFORM_TIER = 'platform'

MONGODB_CORE_PROFILE_NAME = 'mongodb-core'
MONGODB_TEXT_SEARCH_PROFILE_NAME = 'mongodb-text-search'
MONGODB_SEARCH_PROFILE_NAME = 'mongodb-search'
MONGODB_PLATFORM_PROFILE_NAME = 'mongodb-platform'
MONGODB_AGGREGATE_RICH_PROFILE_NAME = 'mongodb-aggregate-rich'

_READ_OPERATIONS = (
    CatalogOperation(
        name=MONGODB_FIND,
        result_type='cursor',
        description='Stream matching documents.',
    ),
    CatalogOperation(
        name=MONGODB_FIND_ONE,
        result_type='document',
        description='Return a single matching document.',
    ),
    CatalogOperation(
        name=MONGODB_COUNT_DOCUMENTS,
        result_type='count',
        description='Count matching documents.',
    ),
    CatalogOperation(
        name=MONGODB_ESTIMATED_DOCUMENT_COUNT,
        result_type='count',
        description='Return a fast estimated document count.',
    ),
    CatalogOperation(
        name=MONGODB_DISTINCT,
        result_type='array',
        description='Return distinct values for a path.',
    ),
)

_WRITE_OPERATIONS = (
    CatalogOperation(name=MONGODB_INSERT_ONE, result_type='insert_result'),
    CatalogOperation(name=MONGODB_INSERT_MANY, result_type='insert_many_result'),
    CatalogOperation(name=MONGODB_UPDATE_ONE, result_type='update_result'),
    CatalogOperation(name=MONGODB_UPDATE_MANY, result_type='update_result'),
    CatalogOperation(name=MONGODB_REPLACE_ONE, result_type='update_result'),
    CatalogOperation(name=MONGODB_DELETE_ONE, result_type='delete_result'),
    CatalogOperation(name=MONGODB_DELETE_MANY, result_type='delete_result'),
    CatalogOperation(name=MONGODB_BULK_WRITE, result_type='bulk_write_result'),
)

_TRANSACTION_OPERATIONS = (
    CatalogOperation(name=MONGODB_START_SESSION, result_type='session'),
    CatalogOperation(
        name=MONGODB_WITH_TRANSACTION,
        result_type='transaction_result',
    ),
)

_AGGREGATION_OPERATIONS = (
    CatalogOperation(
        name=MONGODB_AGGREGATE,
        result_type='cursor',
        description='Run an aggregation pipeline.',
    ),
)

_CHANGE_STREAM_OPERATIONS = (
    CatalogOperation(
        name=MONGODB_WATCH,
        result_type='change_stream',
        description='Open a change stream.',
    ),
)

_SEARCH_OPERATIONS = (
    CatalogOperation(
        name=MONGODB_AGGREGATE,
        result_type='cursor',
        description='Run aggregate pipelines that start with $search.',
    ),
)

_VECTOR_SEARCH_OPERATIONS = (
    CatalogOperation(
        name=MONGODB_AGGREGATE,
        result_type='cursor',
        description='Run aggregate pipelines that start with $vectorSearch.',
    ),
)

_READ_OPERATION_NAMES = tuple(operation.name for operation in _READ_OPERATIONS)
_WRITE_OPERATION_NAMES = tuple(operation.name for operation in _WRITE_OPERATIONS)
_TRANSACTION_OPERATION_NAMES = tuple(
    operation.name for operation in _TRANSACTION_OPERATIONS
)

_DB_SYSTEM_FIELD = TelemetryFieldRequirement(name='db.system.name')
_DB_OPERATION_FIELD = TelemetryFieldRequirement(name='db.operation.name')
_DB_NAMESPACE_FIELD = TelemetryFieldRequirement(name='db.namespace.name')
_DB_OUTCOME_FIELD = TelemetryFieldRequirement(name='db.operation.outcome')
_DB_PIPELINE_STAGE_FIELD = TelemetryFieldRequirement(name='db.pipeline.stage.name')
_DB_PIPELINE_STAGE_COUNT_FIELD = TelemetryFieldRequirement(
    name='db.pipeline.stage.count'
)
_DB_SEARCH_OPERATOR_FIELD = TelemetryFieldRequirement(name='db.search.operator')
_DB_VECTOR_SIMILARITY_FIELD = TelemetryFieldRequirement(
    name='db.vector_search.similarity'
)
_DB_CHANGE_OPERATION_TYPE_FIELD = TelemetryFieldRequirement(
    name='db.change.operation_type'
)
_DB_COLLATION_LOCALE_FIELD = TelemetryFieldRequirement(name='db.collation.locale')
_DB_PERSISTENCE_ENGINE_FIELD = TelemetryFieldRequirement(
    name='db.persistence.storage_engine'
)
_DB_PERSISTENCE_PERSISTENT_FIELD = TelemetryFieldRequirement(
    name='db.persistence.persistent'
)
_DB_TOPOLOGY_TYPE_FIELD = TelemetryFieldRequirement(name='db.topology.type')
_DB_TOPOLOGY_SERVER_COUNT_FIELD = TelemetryFieldRequirement(
    name='db.topology.server.count'
)
_DB_TRANSACTION_ID_FIELD = TelemetryFieldRequirement(name='db.transaction.id')
_DB_TRANSACTION_OUTCOME_FIELD = TelemetryFieldRequirement(
    name='db.transaction.outcome'
)


def _mongodb_operation_telemetry(
    *,
    span_name: str,
    metric_name: str,
    event_type: str,
    extra_span_attributes: tuple[TelemetryFieldRequirement, ...] = (),
    extra_metric_labels: tuple[TelemetryFieldRequirement, ...] = (),
    extra_event_payload_keys: tuple[TelemetryFieldRequirement, ...] = (),
    description: str,
) -> CapabilityTelemetry:
    return CapabilityTelemetry(
        spans=(
            TelemetrySpanSpec(
                name=span_name,
                required_attributes=(
                    _DB_SYSTEM_FIELD,
                    _DB_OPERATION_FIELD,
                    _DB_NAMESPACE_FIELD,
                    *extra_span_attributes,
                ),
                description=description,
            ),
        ),
        metrics=(
            TelemetryMetricSpec(
                name=metric_name,
                unit='s',
                required_labels=(
                    _DB_SYSTEM_FIELD,
                    _DB_OPERATION_FIELD,
                    _DB_OUTCOME_FIELD,
                    *extra_metric_labels,
                ),
                description=f'{description} duration metric.',
            ),
        ),
        events=(
            TelemetryEventSpec(
                event_type=event_type,
                required_payload_keys=(
                    _DB_SYSTEM_FIELD,
                    _DB_OPERATION_FIELD,
                    _DB_NAMESPACE_FIELD,
                    _DB_OUTCOME_FIELD,
                    *extra_event_payload_keys,
                ),
                description=f'{description} completion event.',
            ),
        ),
    )


_MONGODB_READ_WRITE_TELEMETRY = _mongodb_operation_telemetry(
    span_name='db.client.operation',
    metric_name='db.client.operation.duration',
    event_type='db.client.operation.completed',
    description='Database client operation span.',
)

_MONGODB_AGGREGATION_TELEMETRY = _mongodb_operation_telemetry(
    span_name='db.client.aggregate',
    metric_name='db.client.aggregate.duration',
    event_type='db.client.aggregate.completed',
    extra_span_attributes=(_DB_PIPELINE_STAGE_COUNT_FIELD,),
    extra_event_payload_keys=(_DB_PIPELINE_STAGE_COUNT_FIELD,),
    description='Aggregation pipeline execution span.',
)

_MONGODB_SEARCH_TELEMETRY = _mongodb_operation_telemetry(
    span_name='db.client.search',
    metric_name='db.client.search.duration',
    event_type='db.client.search.completed',
    extra_span_attributes=(
        _DB_PIPELINE_STAGE_FIELD,
        _DB_SEARCH_OPERATOR_FIELD,
    ),
    extra_metric_labels=(_DB_PIPELINE_STAGE_FIELD,),
    extra_event_payload_keys=(
        _DB_PIPELINE_STAGE_FIELD,
        _DB_SEARCH_OPERATOR_FIELD,
    ),
    description='Search pipeline execution span.',
)

_MONGODB_VECTOR_SEARCH_TELEMETRY = _mongodb_operation_telemetry(
    span_name='db.client.vector_search',
    metric_name='db.client.vector_search.duration',
    event_type='db.client.vector_search.completed',
    extra_span_attributes=(
        _DB_PIPELINE_STAGE_FIELD,
        _DB_VECTOR_SIMILARITY_FIELD,
    ),
    extra_metric_labels=(_DB_VECTOR_SIMILARITY_FIELD,),
    extra_event_payload_keys=(
        _DB_PIPELINE_STAGE_FIELD,
        _DB_VECTOR_SIMILARITY_FIELD,
    ),
    description='Vector search pipeline execution span.',
)

MONGODB_CATALOG = register_catalog(
    CapabilityCatalog(
        interface=MONGODB_INTERFACE,
        description=(
            'CXP standard for providers compatible with the '
            'database/mongodb interface.'
        ),
        capabilities=(
            CatalogCapability(
                name=MONGODB_READ,
                description='Basic read queries.',
                operations=_READ_OPERATIONS,
                telemetry=_MONGODB_READ_WRITE_TELEMETRY,
            ),
            CatalogCapability(
                name=MONGODB_WRITE,
                description='Insert, update, and delete document operations.',
                operations=_WRITE_OPERATIONS,
                telemetry=_MONGODB_READ_WRITE_TELEMETRY,
            ),
            CatalogCapability(
                name=MONGODB_TRANSACTIONS,
                description='Atomic multi-document operations.',
                operations=_TRANSACTION_OPERATIONS,
                telemetry=CapabilityTelemetry(
                    spans=(
                        TelemetrySpanSpec(
                            name='db.client.transaction',
                            required_attributes=(
                                _DB_SYSTEM_FIELD,
                                _DB_TRANSACTION_ID_FIELD,
                            ),
                        ),
                    ),
                    metrics=(
                        TelemetryMetricSpec(
                            name='db.client.transaction.duration',
                            unit='s',
                            required_labels=(
                                _DB_SYSTEM_FIELD,
                                _DB_TRANSACTION_OUTCOME_FIELD,
                            ),
                        ),
                    ),
                    events=(
                        TelemetryEventSpec(
                            event_type='db.client.transaction.finished',
                            required_payload_keys=(
                                _DB_SYSTEM_FIELD,
                                _DB_TRANSACTION_ID_FIELD,
                                _DB_TRANSACTION_OUTCOME_FIELD,
                            ),
                        ),
                    ),
                ),
            ),
            CatalogCapability(
                name=MONGODB_AGGREGATION,
                description='Support for the aggregation framework.',
                operations=_AGGREGATION_OPERATIONS,
                metadata_schema=MongoAggregationMetadata,
                telemetry=_MONGODB_AGGREGATION_TELEMETRY,
            ),
            CatalogCapability(
                name=MONGODB_CHANGE_STREAMS,
                description='Realtime change observability.',
                operations=_CHANGE_STREAM_OPERATIONS,
                telemetry=CapabilityTelemetry(
                    spans=(
                        TelemetrySpanSpec(
                            name='db.client.change_stream.open',
                            required_attributes=(
                                _DB_SYSTEM_FIELD,
                                _DB_OPERATION_FIELD,
                                _DB_NAMESPACE_FIELD,
                            ),
                        ),
                    ),
                    events=(
                        TelemetryEventSpec(
                            event_type='db.client.change.received',
                            required_payload_keys=(
                                _DB_SYSTEM_FIELD,
                                _DB_NAMESPACE_FIELD,
                                _DB_CHANGE_OPERATION_TYPE_FIELD,
                            ),
                        ),
                    ),
                ),
            ),
            CatalogCapability(
                name=MONGODB_SEARCH,
                description='Support for Atlas Search-style textual queries.',
                operations=_SEARCH_OPERATIONS,
                metadata_schema=MongoSearchMetadata,
                telemetry=_MONGODB_SEARCH_TELEMETRY,
            ),
            CatalogCapability(
                name=MONGODB_VECTOR_SEARCH,
                description='Semantic similarity search support.',
                operations=_VECTOR_SEARCH_OPERATIONS,
                metadata_schema=MongoVectorSearchMetadata,
                telemetry=_MONGODB_VECTOR_SEARCH_TELEMETRY,
            ),
            CatalogCapability(
                name=MONGODB_COLLATION,
                description='Collation-aware sorting and comparison.',
                metadata_schema=MongoCollationMetadata,
                telemetry=CapabilityTelemetry(
                    events=(
                        TelemetryEventSpec(
                            event_type='db.client.collation.applied',
                            required_payload_keys=(
                                _DB_SYSTEM_FIELD,
                                _DB_OPERATION_FIELD,
                                _DB_COLLATION_LOCALE_FIELD,
                            ),
                        ),
                    ),
                ),
            ),
            CatalogCapability(
                name=MONGODB_PERSISTENCE,
                description='Data persistence beyond process lifetime.',
                metadata_schema=MongoPersistenceMetadata,
                telemetry=CapabilityTelemetry(
                    events=(
                        TelemetryEventSpec(
                            event_type='db.client.persistence.detected',
                            required_payload_keys=(
                                _DB_SYSTEM_FIELD,
                                _DB_PERSISTENCE_ENGINE_FIELD,
                                _DB_PERSISTENCE_PERSISTENT_FIELD,
                            ),
                        ),
                    ),
                ),
            ),
            CatalogCapability(
                name=MONGODB_TOPOLOGY_DISCOVERY,
                description='Topology and node-state discovery.',
                metadata_schema=MongoTopologyDiscoveryMetadata,
                telemetry=CapabilityTelemetry(
                    events=(
                        TelemetryEventSpec(
                            event_type='db.client.topology.discovered',
                            required_payload_keys=(
                                _DB_SYSTEM_FIELD,
                                _DB_TOPOLOGY_TYPE_FIELD,
                                _DB_TOPOLOGY_SERVER_COUNT_FIELD,
                            ),
                        ),
                        TelemetryEventSpec(
                            event_type='db.client.topology.changed',
                            required_payload_keys=(
                                _DB_SYSTEM_FIELD,
                                _DB_TOPOLOGY_TYPE_FIELD,
                                _DB_TOPOLOGY_SERVER_COUNT_FIELD,
                            ),
                        ),
                    ),
                ),
            ),
        ),
        tiers=(
            ConformanceTier(
                name=MONGODB_CORE_TIER,
                required_capabilities=(
                    MONGODB_READ,
                    MONGODB_WRITE,
                    MONGODB_AGGREGATION,
                ),
                description='Minimum interoperable contract for MongoDB providers.',
            ),
            ConformanceTier(
                name=MONGODB_SEARCH_TIER,
                required_capabilities=(
                    MONGODB_READ,
                    MONGODB_WRITE,
                    MONGODB_AGGREGATION,
                    MONGODB_SEARCH,
                    MONGODB_VECTOR_SEARCH,
                ),
                description='Core support plus textual and vector search.',
            ),
            ConformanceTier(
                name=MONGODB_PLATFORM_TIER,
                required_capabilities=(
                    MONGODB_READ,
                    MONGODB_WRITE,
                    MONGODB_AGGREGATION,
                    MONGODB_TRANSACTIONS,
                    MONGODB_CHANGE_STREAMS,
                    MONGODB_COLLATION,
                    MONGODB_PERSISTENCE,
                    MONGODB_TOPOLOGY_DISCOVERY,
                ),
                description='Platform and runtime operation capabilities.',
            ),
        ),
    )
)

MONGODB_CORE_PROFILE = CapabilityProfile(
    name=MONGODB_CORE_PROFILE_NAME,
    interface=MONGODB_INTERFACE,
    description='Reusable minimum profile for basic MongoDB tests and resources.',
    requirements=(
        CapabilityRequirement(
            capability_name=MONGODB_READ,
            required_operations=_READ_OPERATION_NAMES,
        ),
        CapabilityRequirement(
            capability_name=MONGODB_WRITE,
            required_operations=_WRITE_OPERATION_NAMES,
        ),
        CapabilityRequirement(
            capability_name=MONGODB_AGGREGATION,
            required_operations=(MONGODB_AGGREGATE,),
            required_metadata_keys=('supportedStages',),
        ),
    ),
)

MONGODB_TEXT_SEARCH_PROFILE = CapabilityProfile(
    name=MONGODB_TEXT_SEARCH_PROFILE_NAME,
    interface=MONGODB_INTERFACE,
    description=(
        'Reusable profile for tests and resources that need textual $search '
        'without requiring vector search.'
    ),
    requirements=(
        *MONGODB_CORE_PROFILE.requirements,
        CapabilityRequirement(
            capability_name=MONGODB_SEARCH,
            required_operations=(MONGODB_AGGREGATE,),
            required_metadata_keys=('operators', 'aggregateStage'),
        ),
    ),
)

MONGODB_SEARCH_PROFILE = CapabilityProfile(
    name=MONGODB_SEARCH_PROFILE_NAME,
    interface=MONGODB_INTERFACE,
    description=(
        'Reusable profile for tests and resources with search and vector search.'
    ),
    requirements=(
        *MONGODB_CORE_PROFILE.requirements,
        CapabilityRequirement(
            capability_name=MONGODB_SEARCH,
            required_operations=(MONGODB_AGGREGATE,),
            required_metadata_keys=('operators', 'aggregateStage'),
        ),
        CapabilityRequirement(
            capability_name=MONGODB_VECTOR_SEARCH,
            required_operations=(MONGODB_AGGREGATE,),
            required_metadata_keys=('similarities', 'aggregateStage'),
        ),
    ),
)

MONGODB_PLATFORM_PROFILE = CapabilityProfile(
    name=MONGODB_PLATFORM_PROFILE_NAME,
    interface=MONGODB_INTERFACE,
    description='Reusable profile for MongoDB runtimes with platform surface.',
    requirements=(
        *MONGODB_CORE_PROFILE.requirements,
        CapabilityRequirement(
            capability_name=MONGODB_TRANSACTIONS,
            required_operations=_TRANSACTION_OPERATION_NAMES,
        ),
        CapabilityRequirement(
            capability_name=MONGODB_CHANGE_STREAMS,
            required_operations=(MONGODB_WATCH,),
        ),
        CapabilityRequirement(
            capability_name=MONGODB_COLLATION,
            required_metadata_keys=('backend', 'capabilities'),
        ),
        CapabilityRequirement(
            capability_name=MONGODB_PERSISTENCE,
            required_metadata_keys=('persistent', 'storageEngine'),
        ),
        CapabilityRequirement(
            capability_name=MONGODB_TOPOLOGY_DISCOVERY,
            required_metadata_keys=('topologyType', 'serverCount', 'sdam'),
        ),
    ),
)

MONGODB_AGGREGATE_RICH_PROFILE = CapabilityProfile(
    name=MONGODB_AGGREGATE_RICH_PROFILE_NAME,
    interface=MONGODB_INTERFACE,
    description='Reusable profile for tests that need a richer aggregation subset.',
    requirements=(
        CapabilityRequirement(
            capability_name=MONGODB_AGGREGATION,
            required_operations=(MONGODB_AGGREGATE,),
            required_metadata_keys=(
                'supportedStages',
                'supportedExpressionOperators',
                'supportedGroupAccumulators',
                'supportedWindowAccumulators',
            ),
        ),
    ),
)

MONGODB_MINIMAL_CAPABILITIES = (
    MONGODB_READ,
    MONGODB_WRITE,
    MONGODB_AGGREGATION,
)
MONGODB_FULL_CAPABILITIES = MONGODB_CATALOG.capability_names()

__all__ = (
    'MONGODB_AGGREGATE',
    'MONGODB_AGGREGATE_RICH_PROFILE',
    'MONGODB_AGGREGATE_RICH_PROFILE_NAME',
    'MONGODB_AGGREGATION',
    'MONGODB_BULK_WRITE',
    'MONGODB_CATALOG',
    'MONGODB_CHANGE_STREAMS',
    'MONGODB_COLLATION',
    'MONGODB_CORE_PROFILE',
    'MONGODB_CORE_PROFILE_NAME',
    'MONGODB_CORE_TIER',
    'MONGODB_COUNT_DOCUMENTS',
    'MONGODB_DELETE_MANY',
    'MONGODB_DELETE_ONE',
    'MONGODB_DISTINCT',
    'MONGODB_ESTIMATED_DOCUMENT_COUNT',
    'MONGODB_FIND',
    'MONGODB_FIND_ONE',
    'MONGODB_FULL_CAPABILITIES',
    'MONGODB_INSERT_MANY',
    'MONGODB_INSERT_ONE',
    'MONGODB_INTERFACE',
    'MONGODB_MINIMAL_CAPABILITIES',
    'MONGODB_PERSISTENCE',
    'MONGODB_PLATFORM_PROFILE',
    'MONGODB_PLATFORM_PROFILE_NAME',
    'MONGODB_PLATFORM_TIER',
    'MONGODB_READ',
    'MONGODB_REPLACE_ONE',
    'MONGODB_SEARCH',
    'MONGODB_TEXT_SEARCH_PROFILE',
    'MONGODB_TEXT_SEARCH_PROFILE_NAME',
    'MONGODB_SEARCH_PROFILE',
    'MONGODB_SEARCH_PROFILE_NAME',
    'MONGODB_SEARCH_TIER',
    'MONGODB_START_SESSION',
    'MONGODB_TOPOLOGY_DISCOVERY',
    'MONGODB_TRANSACTIONS',
    'MONGODB_UPDATE_MANY',
    'MONGODB_UPDATE_ONE',
    'MONGODB_VECTOR_SEARCH',
    'MONGODB_WATCH',
    'MONGODB_WITH_TRANSACTION',
    'MONGODB_WRITE',
)
