from __future__ import annotations

from collections.abc import AsyncIterator, Iterator
from inspect import isawaitable
from typing import cast

from cxp.capabilities import CapabilityMatrix
from cxp.catalogs.base import (
    CapabilityCatalog,
    catalog_satisfies_interface,
    get_catalog,
)
from cxp.compliance import CatalogComplianceReport, NegotiatedCatalogDecision
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
    "evaluate_capability_matrix_against_catalog",
    "evaluate_handshake_response_against_catalog",
    "negotiate_with_async_provider",
    "negotiate_with_async_provider_catalog",
    "negotiate_with_async_provider_catalog_report",
    "negotiate_with_provider",
    "negotiate_with_provider_catalog",
    "negotiate_with_provider_catalog_report",
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


def negotiate_with_provider_catalog_report(
    request: HandshakeRequest,
    provider: CapabilityProvider,
    catalog: CapabilityCatalog,
    *,
    required_tier: str | None = None,
    validate_metadata: bool = True,
) -> NegotiatedCatalogDecision:
    response = negotiate_with_provider(request, provider)
    compliance = evaluate_handshake_response_against_catalog(
        response,
        catalog,
        required_tier=required_tier,
        validate_metadata=validate_metadata,
    )
    return NegotiatedCatalogDecision(response=response, compliance=compliance)


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


async def negotiate_with_async_provider_catalog_report(
    request: HandshakeRequest,
    provider: AsyncCapabilityProvider,
    catalog: CapabilityCatalog,
    *,
    required_tier: str | None = None,
    validate_metadata: bool = True,
) -> NegotiatedCatalogDecision:
    response = await negotiate_with_async_provider(request, provider)
    compliance = evaluate_handshake_response_against_catalog(
        response,
        catalog,
        required_tier=required_tier,
        validate_metadata=validate_metadata,
    )
    return NegotiatedCatalogDecision(response=response, compliance=compliance)


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
    provider: (
        TelemetryProvider
        | AsyncTelemetryProvider
        | TelemetryStreamProvider
        | AsyncTelemetryStreamProvider
    ),
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

    report = evaluate_handshake_response_against_catalog(
        response,
        catalog,
        required_tier=required_tier,
        validate_metadata=validate_metadata,
    )
    if report.compliant:
        return response

    reasons = [response.reason] if response.reason is not None else []
    reasons.extend(report.messages)
    return HandshakeResponse(
        provider_identity=response.provider_identity,
        status="rejected",
        offered_capabilities=CapabilityMatrix(),
        reason="; ".join(reasons) if reasons else None,
        missing_required_capabilities=response.missing_required_capabilities,
        missing_optional_capabilities=response.missing_optional_capabilities,
        protocol_version=response.protocol_version,
    )


def evaluate_capability_matrix_against_catalog(
    offered_interface: str,
    capability_matrix: CapabilityMatrix,
    catalog: CapabilityCatalog,
    *,
    required_tier: str | None = None,
    validate_metadata: bool = True,
) -> CatalogComplianceReport:
    catalog_interface = catalog.interface
    interfaces_are_compatible = (
        offered_interface == catalog_interface
        or catalog_satisfies_interface(offered_interface, catalog_interface)
    )
    if not interfaces_are_compatible:
        reason = (
            "Interface mismatch: provider exposes "
            f"{offered_interface!r} but catalog requires {catalog_interface!r}"
        )
        return CatalogComplianceReport(
            compliant=False,
            catalog_interface=catalog_interface,
            offered_interface=offered_interface,
            required_tier=required_tier,
            reason=reason,
            messages=(reason,),
            validation=None,
        )

    validation_catalog = catalog
    if catalog.abstract:
        offered_catalog = get_catalog(offered_interface)
        if offered_catalog is not None and not offered_catalog.abstract:
            validation_catalog = offered_catalog

    if validation_catalog.abstract:
        reason = (
            "Abstract catalog "
            f"{catalog_interface!r} cannot validate capability matrices for "
            f"provider interface {offered_interface!r} without a registered "
            "concrete catalog"
        )
        return CatalogComplianceReport(
            compliant=False,
            catalog_interface=catalog_interface,
            offered_interface=offered_interface,
            required_tier=required_tier,
            reason=reason,
            messages=(reason,),
            validation=None,
        )

    validation = validation_catalog.validate_capability_matrix(
        capability_matrix,
        required_tier=required_tier,
        validate_metadata=validate_metadata,
    )
    messages = validation.messages()
    return CatalogComplianceReport(
        compliant=validation.is_valid(),
        catalog_interface=catalog_interface,
        offered_interface=offered_interface,
        required_tier=required_tier,
        reason="; ".join(messages) if messages else None,
        messages=messages,
        validation=validation,
    )


def evaluate_handshake_response_against_catalog(
    response: HandshakeResponse,
    catalog: CapabilityCatalog,
    *,
    required_tier: str | None = None,
    validate_metadata: bool = True,
) -> CatalogComplianceReport:
    if response.status == "rejected":
        messages = (response.reason,) if response.reason is not None else ()
        return CatalogComplianceReport(
            compliant=False,
            catalog_interface=catalog.interface,
            offered_interface=response.provider_identity.interface,
            required_tier=required_tier,
            reason=response.reason,
            messages=messages,
            validation=None,
        )

    return evaluate_capability_matrix_against_catalog(
        response.provider_identity.interface,
        response.offered_capabilities,
        catalog,
        required_tier=required_tier,
        validate_metadata=validate_metadata,
    )
