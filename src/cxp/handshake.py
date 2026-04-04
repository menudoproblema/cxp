from __future__ import annotations

from typing import Literal

import msgspec

from cxp.capabilities import CapabilityMatrix
from cxp.types import ComponentIdentity

type HandshakeStatus = Literal["accepted", "degraded", "rejected"]
type ProtocolVersion = int

CURRENT_PROTOCOL_VERSION: ProtocolVersion = 1
SUPPORTED_PROTOCOL_VERSIONS: tuple[ProtocolVersion, ...] = (
    CURRENT_PROTOCOL_VERSION,
)

class HandshakeRequest(msgspec.Struct, frozen=True):
    client_identity: ComponentIdentity
    required_capabilities: tuple[str, ...] = ()
    optional_capabilities: tuple[str, ...] = ()
    protocol_version: ProtocolVersion = CURRENT_PROTOCOL_VERSION

class HandshakeResponse(msgspec.Struct, frozen=True):
    provider_identity: ComponentIdentity
    status: HandshakeStatus
    offered_capabilities: CapabilityMatrix
    reason: str | None = None
    missing_required_capabilities: tuple[str, ...] = ()
    missing_optional_capabilities: tuple[str, ...] = ()
    protocol_version: ProtocolVersion = CURRENT_PROTOCOL_VERSION


def is_protocol_version_supported(
    protocol_version: ProtocolVersion,
    supported_protocol_versions: tuple[ProtocolVersion, ...] = SUPPORTED_PROTOCOL_VERSIONS,  # noqa: E501
) -> bool:
    return protocol_version in supported_protocol_versions


def negotiate_protocol_version(
    requested_protocol_version: ProtocolVersion,
    supported_protocol_versions: tuple[ProtocolVersion, ...] = SUPPORTED_PROTOCOL_VERSIONS,  # noqa: E501
) -> ProtocolVersion | None:
    if requested_protocol_version in supported_protocol_versions:
        return requested_protocol_version
    return None

def negotiate_capabilities(
    request: HandshakeRequest,
    provider_identity: ComponentIdentity,
    available_capabilities: CapabilityMatrix,
    supported_protocol_versions: tuple[ProtocolVersion, ...] = SUPPORTED_PROTOCOL_VERSIONS,  # noqa: E501
) -> HandshakeResponse:
    negotiated_protocol_version = negotiate_protocol_version(
        request.protocol_version,
        supported_protocol_versions,
    )
    response_protocol_version = (
        max(supported_protocol_versions)
        if supported_protocol_versions
        else CURRENT_PROTOCOL_VERSION
    )

    if negotiated_protocol_version is None:
        supported_versions_rendered = ", ".join(
            str(version) for version in supported_protocol_versions
        ) or "none"
        return HandshakeResponse(
            provider_identity=provider_identity,
            status="rejected",
            offered_capabilities=CapabilityMatrix(),
            reason=(
                "Unsupported protocol version: "
                f"{request.protocol_version}. "
                "Provider supports: "
                f"{supported_versions_rendered}"
            ),
            missing_required_capabilities=(),
            missing_optional_capabilities=(),
            protocol_version=response_protocol_version,
        )

    if request.client_identity.interface != provider_identity.interface:
        return HandshakeResponse(
            provider_identity=provider_identity,
            status="rejected",
            offered_capabilities=CapabilityMatrix(),
            reason=(
                "Interface mismatch: client requested "
                f"{request.client_identity.interface!r} but provider exposes "
                f"{provider_identity.interface!r}"
            ),
            missing_required_capabilities=(),
            missing_optional_capabilities=(),
            protocol_version=negotiated_protocol_version,
        )

    overlapping_capabilities = tuple(
        name
        for name in request.required_capabilities
        if name in request.optional_capabilities
    )
    if overlapping_capabilities:
        return HandshakeResponse(
            provider_identity=provider_identity,
            status="rejected",
            offered_capabilities=CapabilityMatrix(),
            reason=(
                "Capabilities cannot be both required and optional: "
                + ", ".join(overlapping_capabilities)
            ),
            missing_required_capabilities=(),
            missing_optional_capabilities=(),
            protocol_version=negotiated_protocol_version,
        )

    missing_required = [
        name for name in request.required_capabilities
        if not available_capabilities.has_capability(name)
    ]

    if missing_required:
        return HandshakeResponse(
            provider_identity=provider_identity,
            status="rejected",
            offered_capabilities=CapabilityMatrix(),
            reason=f"Missing required capabilities: {', '.join(missing_required)}",
            missing_required_capabilities=tuple(missing_required),
            missing_optional_capabilities=(),
            protocol_version=negotiated_protocol_version,
        )

    missing_optional = [
        name for name in request.optional_capabilities
        if not available_capabilities.has_capability(name)
    ]

    if missing_optional:
        return HandshakeResponse(
            provider_identity=provider_identity,
            status="degraded",
            offered_capabilities=available_capabilities,
            reason=(
                "Missing optional capabilities: "
                + ", ".join(missing_optional)
            ),
            missing_required_capabilities=(),
            missing_optional_capabilities=tuple(missing_optional),
            protocol_version=negotiated_protocol_version,
        )

    return HandshakeResponse(
        provider_identity=provider_identity,
        status="accepted",
        offered_capabilities=available_capabilities,
        missing_required_capabilities=(),
        missing_optional_capabilities=(),
        protocol_version=negotiated_protocol_version,
    )
