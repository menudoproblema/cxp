import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from cxp import (
    MONGODB_CATALOG,
    MONGODB_SEARCH_PROFILE,
    CapabilityDescriptor,
    CapabilityOperationBinding,
    ComponentCapabilitySnapshot,
    MongoAggregationMetadata,
    MongoSearchMetadata,
    MongoVectorSearchMetadata,
    TelemetryEvent,
    TelemetryMetric,
    TelemetrySnapshot,
    TelemetrySpan,
)

snapshot = ComponentCapabilitySnapshot(
    component_name="local-mongodb",
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
            metadata=MongoAggregationMetadata(
                supportedStages=("$match", "$project", "$search", "$vectorSearch"),
                supportedExpressionOperators=("$eq", "$and"),
            ),
        ),
        CapabilityDescriptor(
            name="search",
            level="supported",
            operations=(CapabilityOperationBinding("aggregate"),),
            metadata=MongoSearchMetadata(
                operators=("text", "phrase", "compound"),
            ),
        ),
        CapabilityDescriptor(
            name="vector_search",
            level="supported",
            operations=(CapabilityOperationBinding("aggregate"),),
            metadata=MongoVectorSearchMetadata(
                similarities=("cosine",),
            ),
        ),
    ),
)

profile_validation = MONGODB_CATALOG.validate_component_snapshot_against_profile(
    snapshot,
    MONGODB_SEARCH_PROFILE,
)

telemetry = TelemetrySnapshot(
    provider_id="local-mongodb",
    spans=(
        TelemetrySpan(
            trace_id="trace-search",
            span_id="span-search",
            parent_span_id=None,
            name="db.client.search",
            start_time=1.0,
            end_time=1.2,
            attributes={
                "db.system.name": "mongodb",
                "db.operation.name": "aggregate",
                "db.namespace.name": "docs.articles",
                "db.pipeline.stage.name": "$search",
                "db.search.operator": "compound",
            },
        ),
    ),
    metrics=(
        TelemetryMetric(
            name="db.client.search.duration",
            value=0.2,
            unit="s",
            labels={
                "db.system.name": "mongodb",
                "db.operation.name": "aggregate",
                "db.operation.outcome": "success",
                "db.pipeline.stage.name": "$search",
            },
        ),
    ),
    events=(
        TelemetryEvent(
            event_type="db.client.search.completed",
            payload={
                "db.system.name": "mongodb",
                "db.operation.name": "aggregate",
                "db.namespace.name": "docs.articles",
                "db.operation.outcome": "success",
                "db.pipeline.stage.name": "$search",
                "db.search.operator": "compound",
            },
        ),
    ),
)

telemetry_ok = MONGODB_CATALOG.is_telemetry_snapshot_compliant(
    telemetry,
    ("search",),
)

print("search profile valid:", profile_validation.is_valid())
print("telemetry valid:", telemetry_ok)
