from __future__ import annotations

import asyncio

import msgspec
from pytest import raises

from cxp import (
    PLAN_RUN_EXECUTION_CATALOG,
    MONGODB_CATALOG,
    MONGODB_CORE_PROFILE,
    SUPPORTED_PROTOCOL_VERSIONS,
    Capability,
    CapabilityCatalog,
    CapabilityDescriptor,
    CapabilityMatrix,
    CapabilityOperationBinding,
    CapabilityProfileDefinitionValidationResult,
    CapabilityProfileValidationResult,
    CapabilityRequirement,
    CatalogCapability,
    CatalogOperation,
    CatalogRegistry,
    ComponentCapabilitySnapshot,
    ComponentIdentity,
    ConformanceTier,
    HandshakeResponse,
    TelemetryBuffer,
    TelemetryContext,
    TelemetryEvent,
    TelemetryMetric,
    TelemetrySnapshot,
    TelemetrySpan,
    TelemetryValidationResult,
)
from cxp.catalogs.base import (
    CapabilityTelemetry,
    TelemetryEventSpec,
    TelemetryFieldRequirement,
    TelemetryMetricSpec,
    TelemetrySpanSpec,
    _catalog_satisfies_interface,
    _merge_field_requirements,
)
from cxp.descriptors import DescriptorValidationResult
from cxp.descriptors import UnknownCapabilityOperations
from cxp.integration import (
    _supported_protocol_versions,
    _validate_component_snapshot,
    _validate_handshake_response_against_catalog,
    _validate_telemetry_snapshot,
    stream_provider_telemetry,
    stream_provider_telemetry_async,
)
from cxp.telemetry import TelemetryBufferOverflow


class ExampleMetadata(msgspec.Struct, frozen=True):
    mode: str


def test_capability_helpers_cover_conversion_and_lookup_paths() -> None:
    metadata = ExampleMetadata(mode="strict")
    capability = Capability(name="planning", metadata=metadata)

    assert capability.get_metadata(ExampleMetadata) is metadata

    converted = Capability(
        name="planning",
        metadata={"mode": "loose"},
    ).get_metadata(ExampleMetadata)
    assert converted == ExampleMetadata(mode="loose")

    matrix = CapabilityMatrix.from_names(("run", "planning"))

    assert matrix.has_capability("run") is True
    assert matrix.has_capability("missing") is False
    assert matrix.get_capability("planning") == Capability(name="planning")
    assert matrix.get_capability("missing") is None


def test_descriptor_helpers_cover_lookup_and_message_edges() -> None:
    descriptor = CapabilityDescriptor(
        name="planning",
        level="accepted_noop",
        operations=(CapabilityOperationBinding(operation_name="plan.analyze"),),
    )
    snapshot = ComponentCapabilitySnapshot(
        component_name="pytest",
        capabilities=(
            descriptor,
            CapabilityDescriptor(name="run", level="unsupported"),
        ),
    )
    validation = DescriptorValidationResult(
        unknown_capabilities=("unknown",),
        unknown_operations=(),
        invalid_metadata=(),
        interface_mismatch="database/mongodb",
        expected_interface="execution/plan-run",
    )

    assert descriptor.get_operation("missing") is None
    assert descriptor.is_negotiable() is False
    assert snapshot.get_capability("planning") is descriptor
    assert snapshot.get_capability("missing") is None
    assert snapshot.offered_capabilities() == (descriptor,)
    assert validation.messages() == (
        "Unknown capabilities: unknown",
        "Interface mismatch: expected 'execution/plan-run' but received "
        "'database/mongodb'",
    )


def test_validation_result_messages_cover_all_fields() -> None:
    profile_definition = CapabilityProfileDefinitionValidationResult(
        unknown_capabilities=("unknown_capability",),
        unknown_operations=(
            UnknownCapabilityOperations(
                capability_name="run",
                operation_names=("unknown.operation",),
            ),
        ),
        unknown_metadata_keys=("run.mode",),
        interface_mismatch="database/mongodb",
        expected_interface="execution/plan-run",
    )
    telemetry_validation = TelemetryValidationResult(
        unknown_capabilities=("unknown_capability",),
        unknown_spans=("unknown.span",),
        unknown_metrics=("unknown.metric",),
        unknown_events=("unknown.event",),
        missing_span_attributes=("span.attr",),
        missing_metric_labels=("metric.label",),
        missing_event_payload_keys=("event.payload",),
        invalid_metric_units=("metric: expected 's', got 'ms'",),
        invalid_event_severities=("event: expected 'error', got 'warning'",),
    )
    profile_validation = CapabilityProfileValidationResult(
        unknown_profile_capabilities=("unknown_capability",),
        missing_capabilities=("missing_capability",),
        missing_operations=(
            UnknownCapabilityOperations(
                capability_name="run",
                operation_names=("run",),
            ),
        ),
        missing_metadata_keys=("run.mode",),
        invalid_metadata=("run",),
        interface_mismatch="database/mongodb",
        expected_interface="execution/plan-run",
    )

    assert profile_definition.is_valid() is False
    assert CapabilityProfileDefinitionValidationResult().messages() == ()
    assert profile_definition.messages() == (
        "Unknown profile capabilities: unknown_capability",
        "Unknown profile operations for capability 'run': unknown.operation",
        "Unknown profile metadata keys: run.mode",
        "Interface mismatch: 'database/mongodb' != 'execution/plan-run'",
    )
    assert telemetry_validation.is_valid() is False
    assert TelemetryValidationResult().messages() == ()
    assert telemetry_validation.messages() == (
        "Unknown capabilities for telemetry validation: unknown_capability",
        "Unknown telemetry spans: unknown.span",
        "Unknown telemetry metrics: unknown.metric",
        "Unknown telemetry events: unknown.event",
        "Missing span attributes: span.attr",
        "Missing metric labels: metric.label",
        "Missing event payload keys: event.payload",
        "Invalid metric units: metric: expected 's', got 'ms'",
        "Invalid event severities: event: expected 'error', got 'warning'",
    )
    assert profile_validation.is_valid() is False
    assert CapabilityProfileValidationResult().messages() == ()
    assert profile_validation.messages() == (
        "Unknown profile capabilities: unknown_capability",
        "Missing capabilities: missing_capability",
        "Missing operations for capability 'run': run",
        "Missing metadata keys: run.mode",
        "Invalid metadata for capabilities: run",
        "Interface mismatch: 'database/mongodb' != 'execution/plan-run'",
    )


def test_catalog_helpers_cover_missing_capabilities_and_abstract_guards() -> None:
    catalog_capability = CatalogCapability(
        name="planning",
        operations=(CatalogOperation(name="plan.analyze"),),
        metadata_schema=ExampleMetadata,
    )
    catalog = CapabilityCatalog(
        interface="execution/custom",
        capabilities=(catalog_capability,),
        tiers=(ConformanceTier(name="core", required_capabilities=("planning",)),),
    )
    abstract_catalog = CapabilityCatalog(interface="application/http", abstract=True)

    assert catalog_capability.get_operation("missing") is None
    assert CatalogCapability(name="run").metadata_keys() == ()
    assert CatalogCapability(name="run").validate_metadata(Capability(name="run")) is True
    assert catalog.capability_operation_names("missing") == ()
    assert catalog.has_operation("missing", "plan.analyze") is False
    assert catalog.get_operation("missing", "plan.analyze") is None
    assert catalog.get_capability_telemetry("missing") is None
    assert catalog.telemetry_span_names("missing") == ()
    assert catalog.telemetry_metric_names("missing") == ()
    assert catalog.telemetry_event_types("missing") == ()

    with raises(ValueError, match="Abstract catalog"):
        abstract_catalog.validate_capability_names(())


def test_catalog_profile_validation_edge_paths() -> None:
    empty_mongodb_catalog = CapabilityCatalog(interface="database/mongodb")
    wrong_identity_snapshot = ComponentCapabilitySnapshot(
        component_name="mongo",
        identity=ComponentIdentity(
            interface="execution/plan-run",
            provider="pytest",
            version="1.0.0",
        ),
        capabilities=(),
    )
    missing_metadata_snapshot = ComponentCapabilitySnapshot(
        component_name="mongo",
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
                metadata={},
            ),
        ),
    )

    unknown_profile = empty_mongodb_catalog.validate_component_snapshot_against_profile(
        ComponentCapabilitySnapshot(component_name="mongo", capabilities=()),
        MONGODB_CORE_PROFILE,
    )
    assert unknown_profile.unknown_profile_capabilities == (
        "read",
        "write",
        "aggregation",
    )

    identity_mismatch = MONGODB_CATALOG.validate_component_snapshot_against_profile(
        wrong_identity_snapshot,
        MONGODB_CORE_PROFILE,
    )
    assert identity_mismatch.interface_mismatch == "execution/plan-run"

    profile_interface_mismatch = (
        PLAN_RUN_EXECUTION_CATALOG.validate_component_snapshot_against_profile(
            ComponentCapabilitySnapshot(component_name="pytest", capabilities=()),
            MONGODB_CORE_PROFILE,
        )
    )
    assert profile_interface_mismatch.interface_mismatch == "database/mongodb"

    missing_metadata = MONGODB_CATALOG.validate_component_snapshot_against_profile(
        missing_metadata_snapshot,
        MONGODB_CORE_PROFILE,
    )
    assert missing_metadata.missing_metadata_keys == ("aggregation.supportedStages",)
    assert missing_metadata.invalid_metadata == ("aggregation",)


def test_catalog_profile_definition_and_component_compliance_edges() -> None:
    empty_mongodb_catalog = CapabilityCatalog(interface="database/mongodb")
    invalid_metadata_catalog = CapabilityCatalog(
        interface="execution/plan-run",
        capabilities=(
            CatalogCapability(
                name="planning",
                metadata_schema=ExampleMetadata,
            ),
        ),
    )
    invalid_snapshot = ComponentCapabilitySnapshot(
        component_name="pytest",
        capabilities=(
            CapabilityDescriptor(
                name="planning",
                level="supported",
                metadata={"mode": 3},
            ),
        ),
    )

    definition_unknown = empty_mongodb_catalog.validate_profile_definition(
        MONGODB_CORE_PROFILE,
    )
    assert definition_unknown.unknown_capabilities == ("read", "write", "aggregation")

    definition_interface_mismatch = PLAN_RUN_EXECUTION_CATALOG.validate_profile_definition(
        MONGODB_CORE_PROFILE,
    )
    assert definition_interface_mismatch.interface_mismatch == "database/mongodb"

    descriptor_validation = PLAN_RUN_EXECUTION_CATALOG.validate_capability_descriptors(
        (CapabilityDescriptor(name="unknown", level="supported"),),
    )
    assert descriptor_validation.unknown_capabilities == ("unknown",)

    matrix = CapabilityMatrix(
        capabilities=(Capability(name="planning", metadata={"mode": 3}),),
    )
    assert (
        invalid_metadata_catalog.validate_capability_matrix(
            matrix,
            validate_metadata=False,
        ).invalid_metadata
        == ()
    )
    assert (
        invalid_metadata_catalog.is_component_snapshot_compliant(
            invalid_snapshot,
            validate_metadata=False,
        )
        is True
    )


def test_execution_engine_telemetry_validation_covers_strict_signal_paths() -> None:
    snapshot = TelemetrySnapshot(
        provider_id="pytest-engine",
        spans=(
            TelemetrySpan(
                trace_id="trace-1",
                span_id="span-1",
                parent_span_id=None,
                name="unknown.span",
                start_time=1.0,
                end_time=1.1,
            ),
            TelemetrySpan(
                trace_id="trace-1",
                span_id="span-2",
                parent_span_id=None,
                name="engine.execution.status.read",
                start_time=1.1,
                end_time=1.2,
            ),
        ),
        metrics=(
            TelemetryMetric(name="unknown.metric", value=1),
            TelemetryMetric(name="engine.execution.active_runs", value=1),
        ),
        events=(
            TelemetryEvent(event_type="unknown.event"),
            TelemetryEvent(
                event_type="engine.input.validation.failed",
                severity="warning",
                payload={"engine.name": "pytest"},
            ),
        ),
    )

    validation = PLAN_RUN_EXECUTION_CATALOG.validate_telemetry_snapshot(
        snapshot,
        ("input_validation", "execution_status"),
        reject_unknown_signals=True,
    )

    assert validation.unknown_spans == ("unknown.span",)
    assert validation.unknown_metrics == ("unknown.metric",)
    assert validation.unknown_events == ("unknown.event",)
    assert validation.missing_span_attributes == (
        "engine.execution.status.read.engine.name",
    )
    assert validation.missing_metric_labels == (
        "engine.execution.active_runs.engine.name",
    )
    assert validation.missing_event_payload_keys == (
        "engine.input.validation.failed.error.code",
    )
    assert validation.invalid_event_severities == (
        "engine.input.validation.failed: expected 'error', got 'warning'",
    )


def test_execution_engine_telemetry_validation_ignores_unknown_metric_and_event_by_default() -> None:
    snapshot = TelemetrySnapshot(
        provider_id="pytest-engine",
        metrics=(TelemetryMetric(name="unknown.metric", value=1),),
        events=(TelemetryEvent(event_type="unknown.event"),),
    )

    validation = PLAN_RUN_EXECUTION_CATALOG.validate_telemetry_snapshot(
        snapshot,
        ("run",),
    )

    assert validation.unknown_metrics == ()
    assert validation.unknown_events == ()


def test_registry_and_private_catalog_helpers_cover_remaining_branches() -> None:
    registry = CatalogRegistry()
    catalog = CapabilityCatalog(interface="demo/interface")
    cycle_catalogs = {
        "demo/a": CapabilityCatalog(
            interface="demo/a",
            satisfies_interfaces=("demo/b",),
        ),
        "demo/b": CapabilityCatalog(
            interface="demo/b",
            satisfies_interfaces=("demo/a",),
        ),
    }

    assert registry.register(catalog) is catalog
    assert registry.get("demo/interface") is catalog
    assert registry.interfaces() == ("demo/interface",)

    with raises(ValueError, match="cannot satisfy itself"):
        registry.register(
            CapabilityCatalog(
                interface="demo/self",
                satisfies_interfaces=("demo/self",),
            )
        )

    assert _catalog_satisfies_interface(
        offered_interface="demo/missing",
        required_interface="demo/interface",
        catalogs={"demo/interface": catalog},
    ) is False
    assert _catalog_satisfies_interface(
        offered_interface="demo/a",
        required_interface="demo/other",
        catalogs=cycle_catalogs,
        visited={"demo/a"},
    ) is False

    merged = _merge_field_requirements(
        (TelemetryFieldRequirement(name="engine.name"),),
        (
            TelemetryFieldRequirement(
                name="engine.name",
                description="Primary engine name",
            ),
            TelemetryFieldRequirement(name="run.mode"),
        ),
    )
    assert merged == (
        TelemetryFieldRequirement(
            name="engine.name",
            description="Primary engine name",
        ),
        TelemetryFieldRequirement(name="run.mode"),
    )


def test_integration_helpers_cover_fallback_and_error_paths(
    mongo_request_factory,
) -> None:
    class NoTelemetryMethods:
        pass

    class NoneSyncTelemetryProvider:
        def cxp_telemetry_provider_id(self) -> str:
            return "example-mongodb"

        def cxp_telemetry_snapshot(self) -> TelemetrySnapshot | None:
            return None

    class NoneAsyncTelemetryProvider:
        def cxp_telemetry_provider_id(self) -> str:
            return "example-mongodb"

        async def cxp_telemetry_snapshot(self) -> TelemetrySnapshot | None:
            return None

    class AwaitableAsyncStreamProvider:
        def cxp_telemetry_provider_id(self) -> str:
            return "example-mongodb"

        async def cxp_telemetry_stream(self):
            async def _stream():
                yield TelemetrySnapshot(provider_id="example-mongodb")

            return _stream()

    class OneSyncTelemetryProvider:
        def cxp_telemetry_provider_id(self) -> str:
            return "example-mongodb"

        def cxp_telemetry_snapshot(self) -> TelemetrySnapshot | None:
            return TelemetrySnapshot(provider_id="example-mongodb")

    class OneAsyncTelemetryProvider:
        def cxp_telemetry_provider_id(self) -> str:
            return "example-mongodb"

        async def cxp_telemetry_snapshot(self) -> TelemetrySnapshot | None:
            return TelemetrySnapshot(provider_id="example-mongodb")

    class SyncStreamProviderWithNone:
        def cxp_telemetry_provider_id(self) -> str:
            return "example-mongodb"

        def cxp_telemetry_stream(self):
            yield None
            yield TelemetrySnapshot(provider_id="example-mongodb")

    class AsyncStreamProviderWithNone:
        def cxp_telemetry_provider_id(self) -> str:
            return "example-mongodb"

        async def cxp_telemetry_stream(self):
            yield None
            yield TelemetrySnapshot(provider_id="example-mongodb")

    class NoSupportedProtocolVersions:
        pass

    class EmptySupportedProtocolVersions:
        def cxp_supported_protocol_versions(self) -> tuple[int, ...]:
            return ()

    response = HandshakeResponse(
        provider_identity=ComponentIdentity(
            interface="database/mongodb",
            provider="example-mongodb",
            version="3.0.0",
        ),
        status="rejected",
        offered_capabilities=CapabilityMatrix.from_names(("read",)),
        reason="already rejected",
        protocol_version=1,
    )
    matching_identity = ComponentIdentity(
        interface="execution/plan-run",
        provider="pytest",
        version="1.0.0",
    )
    matching_snapshot = ComponentCapabilitySnapshot(
        component_name="pytest",
        identity=matching_identity,
        capabilities=(),
    )

    with raises(TypeError, match="TelemetryProvider"):
        tuple(stream_provider_telemetry(NoTelemetryMethods()))

    assert tuple(stream_provider_telemetry(NoneSyncTelemetryProvider())) == ()

    async def _consume_none_async() -> tuple[TelemetrySnapshot, ...]:
        return tuple(
            [
                snapshot
                async for snapshot in stream_provider_telemetry_async(
                    NoneAsyncTelemetryProvider(),
                )
            ]
        )

    async def _consume_awaitable_stream() -> tuple[TelemetrySnapshot, ...]:
        return tuple(
            [
                snapshot
                async for snapshot in stream_provider_telemetry_async(
                    AwaitableAsyncStreamProvider(),
                )
            ]
        )

    async def _consume_one_async_snapshot() -> tuple[TelemetrySnapshot, ...]:
        return tuple(
            [
                snapshot
                async for snapshot in stream_provider_telemetry_async(
                    OneAsyncTelemetryProvider(),
                )
            ]
        )

    async def _consume_missing_async_provider() -> tuple[TelemetrySnapshot, ...]:
        return tuple(
            [
                snapshot
                async for snapshot in stream_provider_telemetry_async(
                    NoTelemetryMethods(),
                )
            ]
        )

    async def _consume_stream_with_none_async() -> tuple[TelemetrySnapshot, ...]:
        return tuple(
            [
                snapshot
                async for snapshot in stream_provider_telemetry_async(
                    AsyncStreamProviderWithNone(),
                )
            ]
        )

    with raises(TypeError, match="AsyncTelemetryProvider"):
        asyncio.run(_consume_missing_async_provider())

    assert asyncio.run(_consume_none_async()) == ()
    assert tuple(stream_provider_telemetry(OneSyncTelemetryProvider())) == (
        TelemetrySnapshot(provider_id="example-mongodb"),
    )
    assert tuple(stream_provider_telemetry(SyncStreamProviderWithNone())) == (
        TelemetrySnapshot(provider_id="example-mongodb"),
    )
    awaitable_snapshots = asyncio.run(_consume_awaitable_stream())
    assert len(awaitable_snapshots) == 1
    assert asyncio.run(_consume_one_async_snapshot()) == (
        TelemetrySnapshot(provider_id="example-mongodb"),
    )
    assert asyncio.run(_consume_stream_with_none_async()) == (
        TelemetrySnapshot(provider_id="example-mongodb"),
    )
    assert _supported_protocol_versions(NoSupportedProtocolVersions()) == (
        SUPPORTED_PROTOCOL_VERSIONS
    )
    assert _supported_protocol_versions(EmptySupportedProtocolVersions()) == (
        SUPPORTED_PROTOCOL_VERSIONS
    )
    assert _validate_telemetry_snapshot(NoneSyncTelemetryProvider(), None) is None
    assert _validate_component_snapshot(matching_identity, matching_snapshot) is (
        matching_snapshot
    )
    assert (
        _validate_handshake_response_against_catalog(
            response,
            MONGODB_CATALOG,
            required_tier=None,
            validate_metadata=True,
        )
        is response
    )
    assert mongo_request_factory(required_capabilities=("read",)).protocol_version == 1


def test_telemetry_buffer_covers_capacity_and_drop_paths() -> None:
    with raises(ValueError, match="greater than zero"):
        TelemetryBuffer(provider_id="example-mongodb", max_items=0)

    empty_buffer = TelemetryBuffer(provider_id="example-mongodb")
    empty_buffer._drop_oldest_item()

    event_buffer = TelemetryBuffer(
        provider_id="example-mongodb",
        max_items=1,
        overflow_policy="drop_oldest",
    )
    event_buffer.record_event(TelemetryEvent(event_type="command.started"))
    event_buffer.record_metric("ops", 1)
    event_snapshot = event_buffer.flush()
    assert event_snapshot.events == ()
    assert len(event_snapshot.metrics) == 1

    metric_buffer = TelemetryBuffer(
        provider_id="example-mongodb",
        max_items=1,
        overflow_policy="drop_oldest",
    )
    metric_buffer.record_metric("ops", 1)
    metric_buffer.record_event(TelemetryEvent(event_type="command.started"))
    metric_snapshot = metric_buffer.flush()
    assert metric_snapshot.metrics == ()
    assert len(metric_snapshot.events) == 1

    span_buffer = TelemetryBuffer(
        provider_id="example-mongodb",
        max_items=1,
        overflow_policy="drop_oldest",
    )
    span_buffer.record_span(
        TelemetryContext("trace-1").create_span(
            "mongo.find",
            start_time=1.0,
            end_time=1.1,
        )
    )
    span_buffer.record_event(TelemetryEvent(event_type="command.finished"))
    span_snapshot = span_buffer.flush()
    assert span_snapshot.spans == ()
    assert len(span_snapshot.events) == 1

    raise_buffer = TelemetryBuffer(
        provider_id="example-mongodb",
        max_items=1,
        overflow_policy="raise",
    )
    raise_buffer.record_metric("ops", 1)
    with raises(TelemetryBufferOverflow, match="capacity exceeded"):
        raise_buffer.record_span(
            TelemetryContext("trace-2").create_span(
                "mongo.aggregate",
                start_time=1.0,
                end_time=1.2,
            )
        )
