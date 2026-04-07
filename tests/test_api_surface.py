import msgspec
from pytest import raises

import cxp.contracts
import cxp.integration
from cxp import (
    CURRENT_PROTOCOL_VERSION,
    SUPPORTED_PROTOCOL_VERSIONS,
    Capability,
    CapabilityCatalog,
    CapabilityDescriptor,
    CapabilityMatrix,
    CapabilityMatrixValidationResult,
    CapabilitySnapshotProvider,
    CatalogCapability,
    ComponentCapabilitySnapshot,
    ComponentDependencyRule,
    ConformanceTier,
    TelemetryBuffer,
    TelemetryBufferOverflow,
    TelemetryContext,
    TelemetrySnapshot,
    TelemetrySpan,
    collect_provider_capability_snapshot,
    get_catalog,
    is_protocol_version_supported,
    negotiate_protocol_version,
    register_catalog,
)
from cxp.catalogs.interfaces.browser.playwright import PLAYWRIGHT_BROWSER_CATALOG
from cxp.catalogs.interfaces.database.mongodb import MONGODB_CATALOG
from cxp.catalogs.results import ActionResult


def test_current_protocol_version_is_supported() -> None:
    assert is_protocol_version_supported(CURRENT_PROTOCOL_VERSION)
    assert CURRENT_PROTOCOL_VERSION in SUPPORTED_PROTOCOL_VERSIONS


def test_default_supported_protocol_versions_are_not_nested() -> None:
    assert is_protocol_version_supported(1) is True
    assert negotiate_protocol_version(1) == 1


def test_negotiate_protocol_version_returns_none_for_unknown_version() -> None:
    assert negotiate_protocol_version(999) is None


def test_negotiate_protocol_version_returns_requested_version_when_supported() -> None:
    assert (
        negotiate_protocol_version(CURRENT_PROTOCOL_VERSION) == CURRENT_PROTOCOL_VERSION
    )


def test_telemetry_snapshot_heartbeat_marks_snapshot() -> None:
    snapshot = TelemetrySnapshot.heartbeat(provider_id="example-mongodb")

    assert snapshot.provider_id == "example-mongodb"
    assert snapshot.is_heartbeat is True
    assert snapshot.status == "healthy"


def test_telemetry_context_propagates_trace_id() -> None:
    context = TelemetryContext(trace_id="trace-123")
    event = context.create_event("command_started")

    assert event.trace_id == "trace-123"
    assert event.event_type == "command_started"


def test_telemetry_context_creates_spans_with_trace_id() -> None:
    context = TelemetryContext(trace_id="trace-123")
    span = context.create_span(
        "mongo.command",
        start_time=1.0,
        end_time=1.25,
        attributes={"command": "find"},
    )

    assert isinstance(span, TelemetrySpan)
    assert span.trace_id == "trace-123"
    assert span.duration == 0.25


def test_telemetry_context_injects_contextual_ids_into_event_payload() -> None:
    context = TelemetryContext(
        trace_id="trace-123",
        request_id="req-1",
        session_id="sess-1",
        operation_id="op-1",
        parent_operation_id="op-root",
    )
    event = context.create_event("command_started")

    assert event.trace_id == "trace-123"
    assert event.payload == {
        "cxp.request.id": "req-1",
        "cxp.session.id": "sess-1",
        "cxp.operation.id": "op-1",
        "cxp.parent.operation.id": "op-root",
    }


def test_telemetry_context_injects_contextual_ids_into_span_attributes() -> None:
    context = TelemetryContext(
        trace_id="trace-123",
        request_id="req-1",
        session_id="sess-1",
        operation_id="op-1",
    )
    span = context.create_span(
        "mongo.command",
        start_time=1.0,
        end_time=1.25,
    )

    assert span.trace_id == "trace-123"
    assert span.attributes == {
        "cxp.request.id": "req-1",
        "cxp.session.id": "sess-1",
        "cxp.operation.id": "op-1",
    }


def test_telemetry_context_create_metric_injects_contextual_ids_into_labels() -> None:
    context = TelemetryContext(
        trace_id="trace-123",
        request_id="req-1",
        session_id="sess-1",
        operation_id="op-1",
    )
    metric = context.create_metric("ops", 2, unit="1")

    assert metric.name == "ops"
    assert metric.value == 2
    assert metric.unit == "1"
    assert metric.labels == {
        "cxp.request.id": "req-1",
        "cxp.session.id": "sess-1",
        "cxp.operation.id": "op-1",
    }


def test_telemetry_context_explicit_values_override_context_values() -> None:
    context = TelemetryContext(
        trace_id="trace-123",
        request_id="req-1",
        session_id="sess-1",
        operation_id="op-1",
    )
    event = context.create_event(
        "command_started",
        payload={"cxp.operation.id": "op-2", "custom": "value"},
    )
    span = context.create_span(
        "mongo.command",
        start_time=1.0,
        end_time=1.25,
        attributes={"cxp.request.id": "req-2"},
    )
    metric = context.create_metric(
        "ops",
        2,
        labels={"cxp.session.id": "sess-2"},
    )

    assert event.payload["cxp.operation.id"] == "op-2"
    assert event.payload["custom"] == "value"
    assert span.attributes["cxp.request.id"] == "req-2"
    assert metric.labels["cxp.session.id"] == "sess-2"


def test_telemetry_context_generates_consistent_trace_id_when_missing() -> None:
    context = TelemetryContext()
    event = context.create_event("command_started")
    span = context.create_span(
        "mongo.command",
        start_time=1.0,
        end_time=1.25,
    )

    assert event.trace_id is not None
    assert span.trace_id == event.trace_id


def test_telemetry_buffer_flushes_and_clears_state() -> None:
    buffer = TelemetryBuffer(provider_id="example-mongodb")
    buffer.record_metric("ops", 2)
    buffer.record_event(
        TelemetryContext(trace_id="trace-1").create_event("command_succeeded")
    )
    buffer.record_span(
        TelemetryContext(trace_id="trace-1").create_span(
            "mongo.command",
            start_time=1.0,
            end_time=1.5,
        )
    )

    snapshot = buffer.flush(status="healthy", is_heartbeat=True)

    assert snapshot.provider_id == "example-mongodb"
    assert snapshot.is_heartbeat is True
    assert len(snapshot.metrics) == 1
    assert len(snapshot.events) == 1
    assert len(snapshot.spans) == 1

    empty_snapshot = buffer.flush()
    assert empty_snapshot.metrics == ()
    assert empty_snapshot.events == ()
    assert empty_snapshot.spans == ()


def test_telemetry_buffer_can_enforce_capacity_limit() -> None:
    buffer = TelemetryBuffer(provider_id="example-mongodb", max_items=1)
    buffer.record_metric("ops", 1)

    try:
        buffer.record_event(
            TelemetryContext(trace_id="trace-1").create_event("command_started")
        )
    except TelemetryBufferOverflow as error:
        assert "capacity exceeded" in str(error)
    else:
        raise AssertionError("expected buffer capacity limit to fail")


def test_telemetry_buffer_can_drop_new_items_when_full() -> None:
    buffer = TelemetryBuffer(
        provider_id="example-mongodb",
        max_items=1,
        overflow_policy="drop_newest",
    )
    buffer.record_metric("ops", 1)
    buffer.record_event(
        TelemetryContext(trace_id="trace-1").create_event("command_started")
    )

    snapshot = buffer.flush()

    assert len(snapshot.metrics) == 1
    assert len(snapshot.events) == 0
    assert snapshot.dropped_items == 1


def test_mongodb_telemetry_requires_universal_and_domain_resource_identity() -> None:
    capability = MONGODB_CATALOG.get_capability("read")
    assert capability is not None
    telemetry = capability.telemetry
    assert telemetry is not None

    span = telemetry.spans[0]
    required_names = {field.name for field in span.required_attributes}

    assert "cxp.resource.name" in required_names
    assert "cxp.resource.kind" in required_names
    assert "db.system.name" in required_names


def test_playwright_telemetry_requires_universal_and_domain_resource_identity() -> None:
    capability = PLAYWRIGHT_BROWSER_CATALOG.get_capability("dom_interaction")
    assert capability is not None
    telemetry = capability.telemetry
    assert telemetry is not None

    span = telemetry.spans[0]
    required_names = {field.name for field in span.required_attributes}

    assert "cxp.resource.name" in required_names
    assert "cxp.resource.kind" in required_names
    assert "browser.engine" in required_names


def test_atomic_catalog_operations_return_action_result_schema() -> None:
    cache_catalog = get_catalog("cache/key-value")
    runtime_catalog = get_catalog("runtime/environment")

    assert cache_catalog is not None
    assert runtime_catalog is not None

    cache_set = cache_catalog.get_capability("read_write").get_operation("cache.set")
    runtime_reload = runtime_catalog.get_capability("lifecycle").get_operation(
        "runtime.reload"
    )
    browser_click = PLAYWRIGHT_BROWSER_CATALOG.get_capability(
        "dom_interaction"
    ).get_operation("element.click")

    assert cache_set.result_type == "action.result"
    assert cache_set.result_schema is ActionResult
    assert runtime_reload.result_type == "action.result"
    assert runtime_reload.result_schema is ActionResult
    assert browser_click.result_type == "action.result"
    assert browser_click.result_schema is ActionResult


def test_telemetry_buffer_can_drop_oldest_items_when_full() -> None:
    buffer = TelemetryBuffer(
        provider_id="example-mongodb",
        max_items=1,
        overflow_policy="drop_oldest",
    )
    buffer.record_metric("ops", 1)
    buffer.record_event(
        TelemetryContext(trace_id="trace-1").create_event("command_started")
    )

    snapshot = buffer.flush()

    assert len(snapshot.metrics) == 0
    assert len(snapshot.events) == 1
    assert snapshot.dropped_items == 1


def test_descriptor_types_are_exported_in_public_api() -> None:
    descriptor = CapabilityDescriptor(name="planning", level="supported")
    snapshot = ComponentCapabilitySnapshot(
        component_name="pytest",
        capabilities=(descriptor,),
    )
    rule = ComponentDependencyRule(
        source_component="gherkin",
        target_component="pytest",
        dependency_kind="knowledge",
        projection_policy="diagnostic_only",
    )

    assert snapshot.capabilities == (descriptor,)
    assert rule.target_component == "pytest"
    assert collect_provider_capability_snapshot is not None
    assert CapabilitySnapshotProvider is not None
    assert CapabilityMatrixValidationResult is not None


def test_public_module_layout_exposes_contracts_and_integration_layers() -> None:
    from cxp.catalogs.interfaces.execution.plan_run import (
        PLAN_RUN_EXECUTION_CATALOG as plan_run_execution_catalog,
    )

    assert cxp.contracts.CapabilityProvider is not None
    assert cxp.integration.negotiate_with_provider is not None
    assert plan_run_execution_catalog.interface == "execution/plan-run"


def test_catalog_registry_rejects_conflicting_duplicate_registration() -> None:
    from cxp.catalogs import CatalogRegistry

    registry = CatalogRegistry()
    registry.register(
        CapabilityCatalog(
            interface="transport/http",
            capabilities=(CatalogCapability(name="request"),),
            tiers=(ConformanceTier(name="core", required_capabilities=("request",)),),
        )
    )

    try:
        registry.register(
            CapabilityCatalog(
                interface="transport/http",
                capabilities=(CatalogCapability(name="streaming"),),
            )
        )
    except ValueError as error:
        assert "already registered" in str(error)
    else:
        raise AssertionError("expected duplicate registration to fail")


def test_catalog_registry_treats_equal_registration_as_idempotent() -> None:
    from cxp.catalogs import CatalogRegistry

    catalog = CapabilityCatalog(
        interface="transport/http",
        capabilities=(CatalogCapability(name="request"),),
    )
    registry = CatalogRegistry()

    first = registry.register(catalog)
    second = registry.register(catalog)

    assert first is second


def test_catalog_registry_can_replace_when_explicitly_requested() -> None:
    from cxp.catalogs import CatalogRegistry

    registry = CatalogRegistry()
    registry.register(
        CapabilityCatalog(
            interface="transport/http",
            capabilities=(CatalogCapability(name="request"),),
        )
    )
    replaced = registry.register(
        CapabilityCatalog(
            interface="transport/http",
            capabilities=(CatalogCapability(name="streaming"),),
        ),
        replace=True,
    )

    assert replaced.has_capability("streaming") is True


def test_top_level_register_catalog_supports_replace() -> None:
    interface = "tests/top-level-register-catalog"
    initial = CapabilityCatalog(
        interface=interface,
        capabilities=(CatalogCapability(name="request"),),
    )
    replacement = CapabilityCatalog(
        interface=interface,
        capabilities=(CatalogCapability(name="streaming"),),
    )

    register_catalog(initial)
    assert get_catalog(interface) is initial

    with raises(ValueError, match="already registered"):
        register_catalog(replacement)

    replaced = register_catalog(replacement, replace=True)

    assert replaced is replacement
    assert get_catalog(interface) is replacement


def test_catalog_validation_result_reports_invalid_metadata_messages() -> None:
    class PlanningMetadata(msgspec.Struct, frozen=True):
        mode: str

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

    validation = catalog.validate_capability_matrix(matrix)

    assert validation.is_valid() is False
    assert validation.messages() == ("Invalid metadata for capabilities: planning",)
