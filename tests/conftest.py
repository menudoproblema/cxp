from __future__ import annotations

from collections.abc import Iterator

import pytest

from cxp import (
    SUPPORTED_PROTOCOL_VERSIONS,
    Capability,
    CapabilityDescriptor,
    CapabilityMatrix,
    ComponentCapabilitySnapshot,
    ComponentIdentity,
    TelemetryMetric,
    TelemetrySnapshot,
)


class _SyncMongoProvider:
    def __init__(
        self,
        capabilities: tuple[str, ...],
        *,
        supported_protocol_versions: tuple[int, ...] = SUPPORTED_PROTOCOL_VERSIONS,
    ) -> None:
        self._capabilities = capabilities
        self._supported_protocol_versions = supported_protocol_versions

    def cxp_identity(self) -> ComponentIdentity:
        return ComponentIdentity(
            interface="database/mongodb",
            provider="example-mongodb",
            version="3.0.0",
        )

    def cxp_capabilities(self) -> CapabilityMatrix:
        return CapabilityMatrix(
            capabilities=tuple(Capability(name=name) for name in self._capabilities),
        )

    def cxp_supported_protocol_versions(self) -> tuple[int, ...]:
        return self._supported_protocol_versions


class _AsyncMongoProvider:
    def __init__(
        self,
        capabilities: tuple[str, ...],
        *,
        supported_protocol_versions: tuple[int, ...] = SUPPORTED_PROTOCOL_VERSIONS,
    ) -> None:
        self._capabilities = capabilities
        self._supported_protocol_versions = supported_protocol_versions

    async def cxp_identity(self) -> ComponentIdentity:
        return ComponentIdentity(
            interface="database/mongodb",
            provider="example-mongodb",
            version="3.0.0",
        )

    async def cxp_capabilities(self) -> CapabilityMatrix:
        return CapabilityMatrix(
            capabilities=tuple(Capability(name=name) for name in self._capabilities),
        )

    def cxp_supported_protocol_versions(self) -> tuple[int, ...]:
        return self._supported_protocol_versions


class _SyncTelemetryProvider:
    def __init__(self, snapshot: TelemetrySnapshot | None) -> None:
        self._snapshot = snapshot

    def cxp_telemetry_provider_id(self) -> str:
        return "example-mongodb"

    def cxp_telemetry_snapshot(self) -> TelemetrySnapshot | None:
        return self._snapshot


class _AsyncTelemetryProvider:
    def __init__(self, snapshot: TelemetrySnapshot | None) -> None:
        self._snapshot = snapshot

    def cxp_telemetry_provider_id(self) -> str:
        return "example-mongodb"

    async def cxp_telemetry_snapshot(self) -> TelemetrySnapshot | None:
        return self._snapshot


class _SyncTelemetryStreamProvider:
    def cxp_telemetry_provider_id(self) -> str:
        return "example-mongodb"

    def cxp_telemetry_stream(self) -> Iterator[TelemetrySnapshot]:
        yield TelemetrySnapshot(provider_id="example-mongodb")
        yield TelemetrySnapshot(
            provider_id="example-mongodb",
            metrics=(TelemetryMetric(name="ops", value=2),),
        )


class _AsyncTelemetryStreamProvider:
    def cxp_telemetry_provider_id(self) -> str:
        return "example-mongodb"

    async def cxp_telemetry_stream(self):
        yield TelemetrySnapshot(provider_id="example-mongodb")
        yield TelemetrySnapshot(provider_id="example-mongodb", status="degraded")


class _SyncSnapshotProvider:
    def __init__(self, snapshot: ComponentCapabilitySnapshot) -> None:
        self._snapshot = snapshot

    def cxp_identity(self) -> ComponentIdentity:
        return ComponentIdentity(
            interface="execution/engine",
            provider="pytest",
            version="1.0.0",
        )

    def cxp_capability_snapshot(self) -> ComponentCapabilitySnapshot:
        return self._snapshot


class _AsyncSnapshotProvider:
    def __init__(self, snapshot: ComponentCapabilitySnapshot) -> None:
        self._snapshot = snapshot

    async def cxp_identity(self) -> ComponentIdentity:
        return ComponentIdentity(
            interface="execution/engine",
            provider="gherkin",
            version="1.0.0",
        )

    async def cxp_capability_snapshot(self) -> ComponentCapabilitySnapshot:
        return self._snapshot


@pytest.fixture
def mongo_request_factory():
    from cxp import HandshakeRequest

    def _build(
        *,
        interface: str = "database/mongodb",
        required_capabilities: tuple[str, ...] = (),
        optional_capabilities: tuple[str, ...] = (),
        protocol_version: int = 1,
    ) -> HandshakeRequest:
        return HandshakeRequest(
            client_identity=ComponentIdentity(
                interface=interface,
                provider="cosecha",
                version="1.0.0",
            ),
            required_capabilities=required_capabilities,
            optional_capabilities=optional_capabilities,
            protocol_version=protocol_version,
        )

    return _build


@pytest.fixture
def sync_mongo_provider_factory():
    return _SyncMongoProvider


@pytest.fixture
def async_mongo_provider_factory():
    return _AsyncMongoProvider


@pytest.fixture
def sync_telemetry_provider_factory():
    return _SyncTelemetryProvider


@pytest.fixture
def async_telemetry_provider_factory():
    return _AsyncTelemetryProvider


@pytest.fixture
def sync_telemetry_stream_provider():
    return _SyncTelemetryStreamProvider()


@pytest.fixture
def async_telemetry_stream_provider():
    return _AsyncTelemetryStreamProvider()


@pytest.fixture
def sync_snapshot_provider_factory():
    return _SyncSnapshotProvider


@pytest.fixture
def async_snapshot_provider_factory():
    return _AsyncSnapshotProvider


@pytest.fixture
def supported_run_descriptor_snapshot():
    return ComponentCapabilitySnapshot(
        component_name="pytest",
        capabilities=(CapabilityDescriptor(name="run", level="supported"),),
    )
