from pytest import raises

from cxp import (
    PLAN_RUN_EXECUTION_CATALOG,
    MONGODB_CATALOG,
    CapabilityCatalog,
    CapabilityTelemetry,
    CatalogCapability,
    CatalogRegistry,
    TelemetryEvent,
    TelemetryEventSpec,
    TelemetryFieldRequirement,
    TelemetryMetric,
    TelemetryMetricSpec,
    TelemetrySnapshot,
    TelemetrySpan,
    TelemetrySpanSpec,
)


def test_execution_engine_catalog_exposes_capability_telemetry() -> None:
    assert PLAN_RUN_EXECUTION_CATALOG.telemetry_span_names("run") == (
        "engine.run.execute",
    )
    assert PLAN_RUN_EXECUTION_CATALOG.telemetry_metric_names("planning") == (
        "engine.plan.duration",
    )
    assert PLAN_RUN_EXECUTION_CATALOG.telemetry_event_types(
        "execution_status"
    ) == (
        "engine.execution.status.updated",
    )


def test_mongodb_catalog_exposes_capability_specific_telemetry_names() -> None:
    assert MONGODB_CATALOG.telemetry_span_names("aggregation") == (
        "db.client.aggregate",
    )
    assert MONGODB_CATALOG.telemetry_metric_names("search") == (
        "db.client.search.duration",
    )
    assert MONGODB_CATALOG.telemetry_event_types("vector_search") == (
        "db.client.vector_search.completed",
    )


def test_execution_engine_catalog_validates_telemetry_snapshot() -> None:
    snapshot = TelemetrySnapshot(
        provider_id="pytest-engine",
        spans=(
            TelemetrySpan(
                trace_id="trace-1",
                span_id="span-run",
                parent_span_id=None,
                name="engine.run.execute",
                start_time=1.0,
                end_time=2.0,
                attributes={
                    "engine.name": "pytest",
                    "run.mode": "live",
                },
            ),
            TelemetrySpan(
                trace_id="trace-1",
                span_id="span-plan",
                parent_span_id=None,
                name="engine.plan.analyze",
                start_time=2.0,
                end_time=2.2,
                attributes={"engine.name": "pytest"},
            ),
        ),
        metrics=(
            TelemetryMetric(
                name="engine.run.duration",
                value=1.0,
                unit="s",
                labels={
                    "engine.name": "pytest",
                    "run.outcome": "passed",
                },
            ),
        ),
        events=(
            TelemetryEvent(
                event_type="engine.run.finished",
                payload={
                    "engine.name": "pytest",
                    "run.outcome": "passed",
                },
            ),
        ),
    )

    assert PLAN_RUN_EXECUTION_CATALOG.is_telemetry_snapshot_compliant(
        snapshot,
        ("run", "planning"),
    )


def test_execution_engine_catalog_reports_invalid_metric_unit() -> None:
    snapshot = TelemetrySnapshot(
        provider_id="pytest-engine",
        metrics=(
            TelemetryMetric(
                name="engine.run.duration",
                value=1000,
                unit="ms",
                labels={
                    "engine.name": "pytest",
                    "run.outcome": "passed",
                },
            ),
        ),
    )

    validation = PLAN_RUN_EXECUTION_CATALOG.validate_telemetry_snapshot(
        snapshot,
        ("run",),
    )

    assert validation.is_valid() is False
    assert validation.invalid_metric_units == (
        "engine.run.duration: expected 's', got 'ms'",
    )


def test_telemetry_subset_validation_ignores_extra_signals_by_default() -> None:
    snapshot = TelemetrySnapshot(
        provider_id="pytest-engine",
        spans=(
            TelemetrySpan(
                trace_id="trace-1",
                span_id="span-run",
                parent_span_id=None,
                name="engine.run.execute",
                start_time=1.0,
                end_time=2.0,
                attributes={
                    "engine.name": "pytest",
                    "run.mode": "live",
                },
            ),
            TelemetrySpan(
                trace_id="trace-1",
                span_id="span-live",
                parent_span_id=None,
                name="engine.execution.subscribe",
                start_time=2.0,
                end_time=2.1,
                attributes={"engine.name": "pytest"},
            ),
        ),
    )

    assert PLAN_RUN_EXECUTION_CATALOG.is_telemetry_snapshot_compliant(
        snapshot,
        ("run",),
    )


def test_telemetry_subset_validation_can_reject_extra_signals_when_strict() -> None:
    snapshot = TelemetrySnapshot(
        provider_id="pytest-engine",
        events=(
            TelemetryEvent(
                event_type="engine.execution.status.updated",
                payload={
                    "engine.name": "pytest",
                    "execution.status": "running",
                },
            ),
        ),
    )

    validation = PLAN_RUN_EXECUTION_CATALOG.validate_telemetry_snapshot(
        snapshot,
        ("run",),
        reject_unknown_signals=True,
    )

    assert validation.is_valid() is False
    assert validation.unknown_events == ("engine.execution.status.updated",)


def test_mongodb_catalog_validates_shared_operation_telemetry() -> None:
    snapshot = TelemetrySnapshot(
        provider_id="example-mongodb",
        spans=(
            TelemetrySpan(
                trace_id="trace-1",
                span_id="span-1",
                parent_span_id=None,
                name="db.client.operation",
                start_time=1.0,
                end_time=1.5,
                attributes={
                    "db.system.name": "mongodb",
                    "db.operation.name": "find",
                    "db.namespace.name": "users.accounts",
                },
            ),
        ),
        metrics=(
            TelemetryMetric(
                name="db.client.operation.duration",
                value=0.5,
                unit="s",
                labels={
                    "db.system.name": "mongodb",
                    "db.operation.name": "find",
                    "db.operation.outcome": "success",
                },
            ),
        ),
        events=(
            TelemetryEvent(
                event_type="db.client.operation.completed",
                payload={
                    "db.system.name": "mongodb",
                    "db.operation.name": "find",
                    "db.namespace.name": "users.accounts",
                    "db.operation.outcome": "success",
                },
            ),
        ),
    )

    assert MONGODB_CATALOG.is_telemetry_snapshot_compliant(
        snapshot,
        ("read", "write"),
    )


def test_mongodb_catalog_reports_missing_required_event_payload_keys() -> None:
    snapshot = TelemetrySnapshot(
        provider_id="example-mongodb",
        events=(
            TelemetryEvent(
                event_type="db.client.topology.discovered",
                payload={
                    "db.system.name": "mongodb",
                    "db.topology.type": "replica_set",
                },
            ),
        ),
    )

    validation = MONGODB_CATALOG.validate_telemetry_snapshot(
        snapshot,
        ("topology_discovery",),
    )

    assert validation.is_valid() is False
    assert validation.missing_event_payload_keys == (
        "db.client.topology.discovered.db.topology.server.count",
    )


def test_mongodb_catalog_validates_aggregation_search_and_vector_telemetry() -> None:
    snapshot = TelemetrySnapshot(
        provider_id="example-mongodb",
        spans=(
            TelemetrySpan(
                trace_id="trace-agg",
                span_id="span-agg",
                parent_span_id=None,
                name="db.client.aggregate",
                start_time=1.0,
                end_time=1.4,
                attributes={
                    "db.system.name": "mongodb",
                    "db.operation.name": "aggregate",
                    "db.namespace.name": "users.accounts",
                    "db.pipeline.stage.count": 3,
                },
            ),
            TelemetrySpan(
                trace_id="trace-search",
                span_id="span-search",
                parent_span_id=None,
                name="db.client.search",
                start_time=2.0,
                end_time=2.2,
                attributes={
                    "db.system.name": "mongodb",
                    "db.operation.name": "aggregate",
                    "db.namespace.name": "users.accounts",
                    "db.pipeline.stage.name": "$search",
                    "db.search.operator": "compound",
                },
            ),
            TelemetrySpan(
                trace_id="trace-vector",
                span_id="span-vector",
                parent_span_id=None,
                name="db.client.vector_search",
                start_time=3.0,
                end_time=3.3,
                attributes={
                    "db.system.name": "mongodb",
                    "db.operation.name": "aggregate",
                    "db.namespace.name": "users.accounts",
                    "db.pipeline.stage.name": "$vectorSearch",
                    "db.vector_search.similarity": "cosine",
                },
            ),
        ),
        metrics=(
            TelemetryMetric(
                name="db.client.aggregate.duration",
                value=0.4,
                unit="s",
                labels={
                    "db.system.name": "mongodb",
                    "db.operation.name": "aggregate",
                    "db.operation.outcome": "success",
                },
            ),
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
            TelemetryMetric(
                name="db.client.vector_search.duration",
                value=0.3,
                unit="s",
                labels={
                    "db.system.name": "mongodb",
                    "db.operation.name": "aggregate",
                    "db.operation.outcome": "success",
                    "db.vector_search.similarity": "cosine",
                },
            ),
        ),
        events=(
            TelemetryEvent(
                event_type="db.client.aggregate.completed",
                payload={
                    "db.system.name": "mongodb",
                    "db.operation.name": "aggregate",
                    "db.namespace.name": "users.accounts",
                    "db.operation.outcome": "success",
                    "db.pipeline.stage.count": 3,
                },
            ),
            TelemetryEvent(
                event_type="db.client.search.completed",
                payload={
                    "db.system.name": "mongodb",
                    "db.operation.name": "aggregate",
                    "db.namespace.name": "users.accounts",
                    "db.operation.outcome": "success",
                    "db.pipeline.stage.name": "$search",
                    "db.search.operator": "compound",
                },
            ),
            TelemetryEvent(
                event_type="db.client.vector_search.completed",
                payload={
                    "db.system.name": "mongodb",
                    "db.operation.name": "aggregate",
                    "db.namespace.name": "users.accounts",
                    "db.operation.outcome": "success",
                    "db.pipeline.stage.name": "$vectorSearch",
                    "db.vector_search.similarity": "cosine",
                },
            ),
        ),
    )

    assert MONGODB_CATALOG.is_telemetry_snapshot_compliant(
        snapshot,
        ("aggregation", "search", "vector_search"),
    )


def test_mongodb_catalog_requires_stage_specific_search_metadata() -> None:
    snapshot = TelemetrySnapshot(
        provider_id="example-mongodb",
        events=(
            TelemetryEvent(
                event_type="db.client.search.completed",
                payload={
                    "db.system.name": "mongodb",
                    "db.operation.name": "aggregate",
                    "db.namespace.name": "users.accounts",
                    "db.operation.outcome": "success",
                    "db.pipeline.stage.name": "$search",
                },
            ),
        ),
    )

    validation = MONGODB_CATALOG.validate_telemetry_snapshot(
        snapshot,
        ("search",),
    )

    assert validation.is_valid() is False
    assert validation.missing_event_payload_keys == (
        "db.client.search.completed.db.search.operator",
    )


def test_catalog_registry_rejects_conflicting_shared_metric_definitions() -> None:
    registry = CatalogRegistry()

    with raises(ValueError, match="Conflicting telemetry metric definition"):
        registry.register(
            CapabilityCatalog(
                interface="execution/conflict-metric",
                capabilities=(
                    CatalogCapability(
                        name="run",
                        telemetry=CapabilityTelemetry(
                            metrics=(
                                TelemetryMetricSpec(
                                    name="engine.run.duration",
                                    unit="s",
                                    required_labels=(
                                        TelemetryFieldRequirement(name="engine.name"),
                                    ),
                                ),
                            ),
                        ),
                    ),
                    CatalogCapability(
                        name="planning",
                        telemetry=CapabilityTelemetry(
                            metrics=(
                                TelemetryMetricSpec(
                                    name="engine.run.duration",
                                    unit="ms",
                                    required_labels=(
                                        TelemetryFieldRequirement(name="engine.name"),
                                    ),
                                ),
                            ),
                        ),
                    ),
                ),
            )
        )


def test_catalog_registry_rejects_conflicting_shared_event_definitions() -> None:
    registry = CatalogRegistry()

    with raises(ValueError, match="Conflicting telemetry event definition"):
        registry.register(
            CapabilityCatalog(
                interface="execution/conflict-event",
                capabilities=(
                    CatalogCapability(
                        name="run",
                        telemetry=CapabilityTelemetry(
                            events=(
                                TelemetryEventSpec(
                                    event_type="engine.run.finished",
                                    severity="info",
                                    required_payload_keys=(
                                        TelemetryFieldRequirement(name="run.outcome"),
                                    ),
                                ),
                            ),
                        ),
                    ),
                    CatalogCapability(
                        name="planning",
                        telemetry=CapabilityTelemetry(
                            events=(
                                TelemetryEventSpec(
                                    event_type="engine.run.finished",
                                    severity="error",
                                    required_payload_keys=(
                                        TelemetryFieldRequirement(name="run.outcome"),
                                    ),
                                ),
                            ),
                        ),
                    ),
                ),
            )
        )


def test_catalog_registry_rejects_conflicting_shared_span_definitions() -> None:
    registry = CatalogRegistry()

    with raises(ValueError, match="Conflicting telemetry span definition"):
        registry.register(
            CapabilityCatalog(
                interface="execution/conflict-span",
                capabilities=(
                    CatalogCapability(
                        name="run",
                        telemetry=CapabilityTelemetry(
                            spans=(
                                TelemetrySpanSpec(
                                    name="engine.run.execute",
                                    required_attributes=(
                                        TelemetryFieldRequirement(name="engine.name"),
                                    ),
                                ),
                            ),
                        ),
                    ),
                    CatalogCapability(
                        name="planning",
                        telemetry=CapabilityTelemetry(
                            spans=(
                                TelemetrySpanSpec(
                                    name="engine.run.execute",
                                    required_attributes=(
                                        TelemetryFieldRequirement(name="engine.name"),
                                        TelemetryFieldRequirement(name="run.mode"),
                                    ),
                                ),
                            ),
                        ),
                    ),
                ),
            )
        )
