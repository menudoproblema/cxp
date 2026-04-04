from __future__ import annotations

from collections.abc import AsyncIterator, Iterator
from typing import Protocol, runtime_checkable

from cxp.capabilities import CapabilityMatrix
from cxp.descriptors import ComponentCapabilitySnapshot
from cxp.handshake import ProtocolVersion
from cxp.telemetry import TelemetrySnapshot
from cxp.types import ComponentIdentity

__all__ = (
    "AsyncCapabilityProvider",
    "AsyncCapabilitySnapshotProvider",
    "AsyncTelemetryProvider",
    "AsyncTelemetryStreamProvider",
    "CapabilityProvider",
    "CapabilitySnapshotProvider",
    "ProtocolVersionProvider",
    "TelemetryProvider",
    "TelemetryStreamProvider",
)


@runtime_checkable
class CapabilityProvider(Protocol):
    def cxp_identity(self) -> ComponentIdentity: ...

    def cxp_capabilities(self) -> CapabilityMatrix: ...


@runtime_checkable
class CapabilitySnapshotProvider(Protocol):
    def cxp_identity(self) -> ComponentIdentity: ...

    def cxp_capability_snapshot(self) -> ComponentCapabilitySnapshot: ...


@runtime_checkable
class TelemetryProvider(Protocol):
    def cxp_telemetry_provider_id(self) -> str: ...

    def cxp_telemetry_snapshot(self) -> TelemetrySnapshot | None: ...


@runtime_checkable
class AsyncCapabilityProvider(Protocol):
    async def cxp_identity(self) -> ComponentIdentity: ...

    async def cxp_capabilities(self) -> CapabilityMatrix: ...


@runtime_checkable
class AsyncCapabilitySnapshotProvider(Protocol):
    async def cxp_identity(self) -> ComponentIdentity: ...

    async def cxp_capability_snapshot(self) -> ComponentCapabilitySnapshot: ...


@runtime_checkable
class AsyncTelemetryProvider(Protocol):
    def cxp_telemetry_provider_id(self) -> str: ...

    async def cxp_telemetry_snapshot(self) -> TelemetrySnapshot | None: ...


@runtime_checkable
class TelemetryStreamProvider(Protocol):
    def cxp_telemetry_provider_id(self) -> str: ...

    def cxp_telemetry_stream(self) -> Iterator[TelemetrySnapshot]: ...


@runtime_checkable
class AsyncTelemetryStreamProvider(Protocol):
    def cxp_telemetry_provider_id(self) -> str: ...

    async def cxp_telemetry_stream(self) -> AsyncIterator[TelemetrySnapshot]: ...


@runtime_checkable
class ProtocolVersionProvider(Protocol):
    def cxp_supported_protocol_versions(self) -> tuple[ProtocolVersion, ...]: ...
