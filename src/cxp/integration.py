from __future__ import annotations

from collections.abc import AsyncIterator, Iterator
from inspect import isawaitable
from typing import cast

from cxp.capabilities import CapabilityMatrix
from cxp.catalogs.base import CapabilityCatalog
from cxp.contracts import (
    AsyncCapabilityProvider,
    AsyncCapabilitySnapshotProvider,
    AsyncTelemetryProvider,
    AsyncTelemetryStreamProvider,
    CapabilityProvider,
    CapabilitySnapshotProvider,
    TelemetryProvider,
    TelemetryStreamProvider,
)
from cxp.descriptors import ComponentCapabilitySnapshot
from cxp.handshake import (
    SUPPORTED_PROTOCOL_VERSIONS,
    HandshakeRequest,
    HandshakeResponse,
    ProtocolVersion,
    negotiate_capabilities,
)
from cxp.telemetry import TelemetrySnapshot
from cxp.types import ComponentIdentity

__all__ = (
    "collect_provider_capability_snapshot",
    "collect_provider_capability_snapshot_async",
    "collect_provider_telemetry",
    "collect_provider_telemetry_async",
    "negotiate_with_async_provider",
    "negotiate_with_async_provider_catalog",
    "negotiate_with_provider",
    "negotiate_with_provider_catalog",
    "stream_provider_telemetry",
    "stream_provider_telemetry_async",
)


def negotiate_with_provider_catalog(
    request: HandshakeRequest,
    provider: CapabilityProvider,
    catalog: CapabilityCatalog,
    *,
    required_tier: str | None = None,
    validate_metadata: bool = True,
) -> HandshakeResponse:
    response = negotiate_with_provider(request, provider)
    return _validate_handshake_response_against_catalog(
        response,
        catalog,
        required_tier=required_tier,
        validate_metadata=validate_metadata,
    )


def negotiate_with_provider(
    request: HandshakeRequest,
    provider: CapabilityProvider,
) -> HandshakeResponse:
    return negotiate_capabilities(
        request,
        provider.cxp_identity(),
        provider.cxp_capabilities(),
        supported_protocol_versions=_supported_protocol_versions(provider),
    )


async def negotiate_with_async_provider(
    request: HandshakeRequest,
    provider: AsyncCapabilityProvider,
) -> HandshakeResponse:
    provider_identity = await provider.cxp_identity()
    available_capabilities = await provider.cxp_capabilities()
    return negotiate_capabilities(
        request,
        provider_identity,
        available_capabilities,
        supported_protocol_versions=_supported_protocol_versions(provider),
    )


async def negotiate_with_async_provider_catalog(
    request: HandshakeRequest,
    provider: AsyncCapabilityProvider,
    catalog: CapabilityCatalog,
    *,
    required_tier: str | None = None,
    validate_metadata: bool = True,
) -> HandshakeResponse:
    response = await negotiate_with_async_provider(request, provider)
    return _validate_handshake_response_against_catalog(
        response,
        catalog,
        required_tier=required_tier,
        validate_metadata=validate_metadata,
    )


def collect_provider_capability_snapshot(
    provider: CapabilitySnapshotProvider,
) -> ComponentCapabilitySnapshot:
    provider_identity = provider.cxp_identity()
    snapshot = provider.cxp_capability_snapshot()
    return _validate_component_snapshot(provider_identity, snapshot)


async def collect_provider_capability_snapshot_async(
    provider: AsyncCapabilitySnapshotProvider,
) -> ComponentCapabilitySnapshot:
    provider_identity = await provider.cxp_identity()
    snapshot = await provider.cxp_capability_snapshot()
    return _validate_component_snapshot(provider_identity, snapshot)


def collect_provider_telemetry(
    provider: TelemetryProvider,
) -> TelemetrySnapshot | None:
    snapshot = provider.cxp_telemetry_snapshot()
    return _validate_telemetry_snapshot(provider, snapshot)


async def collect_provider_telemetry_async(
    provider: AsyncTelemetryProvider,
) -> TelemetrySnapshot | None:
    snapshot = await provider.cxp_telemetry_snapshot()
    return _validate_telemetry_snapshot(provider, snapshot)


def stream_provider_telemetry(
    provider: TelemetryStreamProvider | TelemetryProvider,
) -> Iterator[TelemetrySnapshot]:
    get_stream = getattr(provider, "cxp_telemetry_stream", None)
    if get_stream is None:
        if not isinstance(provider, TelemetryProvider):
            msg = (
                "Provider must implement TelemetryProvider when no stream is available"
            )
            raise TypeError(msg)
        snapshot = collect_provider_telemetry(provider)
        if snapshot is None:
            return
        yield snapshot
        return

    for snapshot in get_stream():
        validated = _validate_telemetry_snapshot(provider, snapshot)
        if validated is not None:
            yield validated


async def stream_provider_telemetry_async(
    provider: AsyncTelemetryStreamProvider | AsyncTelemetryProvider,
) -> AsyncIterator[TelemetrySnapshot]:
    get_stream = getattr(provider, "cxp_telemetry_stream", None)
    if get_stream is None:
        if not isinstance(provider, AsyncTelemetryProvider):
            msg = (
                "Provider must implement AsyncTelemetryProvider when no "
                "stream is available"
            )
            raise TypeError(msg)
        snapshot = await collect_provider_telemetry_async(provider)
        if snapshot is not None:
            yield snapshot
        return

    stream = get_stream()
    if isawaitable(stream):
        stream = await stream
    stream = cast(AsyncIterator[TelemetrySnapshot], stream)

    async for snapshot in stream:
        validated = _validate_telemetry_snapshot(provider, snapshot)
        if validated is not None:
            yield validated


def _supported_protocol_versions(
    provider: object,
) -> tuple[ProtocolVersion, ...]:
    get_supported_protocol_versions = getattr(
        provider,
        "cxp_supported_protocol_versions",
        None,
    )
    if get_supported_protocol_versions is None:
        return SUPPORTED_PROTOCOL_VERSIONS

    supported_protocol_versions = get_supported_protocol_versions()
    if not supported_protocol_versions:
        return SUPPORTED_PROTOCOL_VERSIONS

    return tuple(supported_protocol_versions)


def _validate_telemetry_snapshot(
    provider: TelemetryProvider | AsyncTelemetryProvider,
    snapshot: TelemetrySnapshot | None,
) -> TelemetrySnapshot | None:
    if snapshot is None:
        return None

    expected_provider_id = provider.cxp_telemetry_provider_id()
    if snapshot.provider_id != expected_provider_id:
        msg = (
            "Telemetry snapshot provider_id does not match the telemetry "
            f"provider identity: {snapshot.provider_id!r} != "
            f"{expected_provider_id!r}"
        )
        raise ValueError(msg)

    return snapshot


def _validate_component_snapshot(
    provider_identity: ComponentIdentity,
    snapshot: ComponentCapabilitySnapshot,
) -> ComponentCapabilitySnapshot:
    if snapshot.identity is None:
        return ComponentCapabilitySnapshot(
            component_name=snapshot.component_name,
            capabilities=snapshot.capabilities,
            component_kind=snapshot.component_kind,
            identity=provider_identity,
        )

    if snapshot.identity != provider_identity:
        msg = (
            "Capability snapshot identity does not match provider identity: "
            f"{snapshot.identity!r} != {provider_identity!r}"
        )
        raise ValueError(msg)

    return snapshot


def _validate_handshake_response_against_catalog(
    response: HandshakeResponse,
    catalog: CapabilityCatalog,
    *,
    required_tier: str | None,
    validate_metadata: bool,
) -> HandshakeResponse:
    if response.status == "rejected":
        return response

    validation = catalog.validate_capability_matrix(
        response.offered_capabilities,
        required_tier=required_tier,
        validate_metadata=validate_metadata,
    )
    if validation.is_valid():
        return response

    reasons = [response.reason] if response.reason is not None else []
    reasons.extend(validation.messages())
    return HandshakeResponse(
        provider_identity=response.provider_identity,
        status="rejected",
        offered_capabilities=CapabilityMatrix(),
        reason="; ".join(reasons) if reasons else None,
        missing_required_capabilities=response.missing_required_capabilities,
        missing_optional_capabilities=response.missing_optional_capabilities,
        protocol_version=response.protocol_version,
    )
