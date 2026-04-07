from __future__ import annotations

import msgspec

from cxp.catalogs.base import (
    CapabilityCatalog,
    CapabilityProfile,
    CapabilityRequirement,
    CapabilityTelemetry,
    CatalogCapability,
    CatalogOperation,
    ConformanceTier,
    TelemetryFieldRequirement,
    TelemetrySpanSpec,
    register_catalog,
)

COSECHA_INSTRUMENTATION_INTERFACE = "cosecha/instrumentation"

COSECHA_INSTRUMENTATION_BOOTSTRAP = "instrumentation_bootstrap"
COSECHA_INSTRUMENTATION_SESSION_SUMMARY = "session_summary"
COSECHA_INSTRUMENTATION_STRUCTURED_SUMMARY = "structured_summary"

COSECHA_INSTRUMENTATION_PREPARE = "instrumentation.prepare"
COSECHA_INSTRUMENTATION_COLLECT = "instrumentation.collect"

COSECHA_INSTRUMENTATION_SUMMARY_TIER = "summary"
COSECHA_INSTRUMENTATION_STRUCTURED_TIER = "structured"

COSECHA_INSTRUMENTATION_SUMMARY_PROFILE_NAME = (
    "cosecha-instrumentation-summary"
)
COSECHA_INSTRUMENTATION_STRUCTURED_PROFILE_NAME = (
    "cosecha-instrumentation-structured"
)

_INSTRUMENTATION_NAME_FIELD = TelemetryFieldRequirement(
    name="cosecha.instrumentation.name"
)


class InstrumentationSummaryMetadata(msgspec.Struct, frozen=True):
    instrumentation_name: str
    summary_kind: str
    measurement_scope: str | None = None


class StructuredSummaryMetadata(msgspec.Struct, frozen=True):
    payload_formats: tuple[str, ...] = ()
    serializable: bool = True


def _instrumentation_span(name: str, description: str) -> CapabilityTelemetry:
    return CapabilityTelemetry(
        spans=(
            TelemetrySpanSpec(
                name=name,
                required_attributes=(_INSTRUMENTATION_NAME_FIELD,),
                description=description,
            ),
        ),
    )


COSECHA_INSTRUMENTATION_CATALOG = register_catalog(
    CapabilityCatalog(
        interface=COSECHA_INSTRUMENTATION_INTERFACE,
        description=(
            "Canonical catalog for Cosecha session instrumentation components, "
            "including bootstrap preparation and structured session summaries."
        ),
        capabilities=(
            CatalogCapability(
                name=COSECHA_INSTRUMENTATION_BOOTSTRAP,
                description="Prepare bootstrap contributions for an instrumented session.",
                telemetry=_instrumentation_span(
                    "instrumentation.prepare",
                    "Instrumentation bootstrap preparation span.",
                ),
                operations=(
                    CatalogOperation(
                        name=COSECHA_INSTRUMENTATION_PREPARE,
                        result_type="instrumentation.contribution",
                    ),
                ),
            ),
            CatalogCapability(
                name=COSECHA_INSTRUMENTATION_SESSION_SUMMARY,
                description="Collect a session summary produced by the instrumentation.",
                metadata_schema=InstrumentationSummaryMetadata,
                telemetry=_instrumentation_span(
                    "instrumentation.collect",
                    "Instrumentation collection span.",
                ),
                operations=(
                    CatalogOperation(
                        name=COSECHA_INSTRUMENTATION_COLLECT,
                        result_type="instrumentation.summary",
                    ),
                ),
            ),
            CatalogCapability(
                name=COSECHA_INSTRUMENTATION_STRUCTURED_SUMMARY,
                description=(
                    "Expose a structured summary payload that can be consumed "
                    "by CLI, remote clients or session artifact persistence."
                ),
                metadata_schema=StructuredSummaryMetadata,
                operations=(
                    CatalogOperation(
                        name=COSECHA_INSTRUMENTATION_COLLECT,
                        result_type="instrumentation.summary",
                    ),
                ),
            ),
        ),
        tiers=(
            ConformanceTier(
                name=COSECHA_INSTRUMENTATION_SUMMARY_TIER,
                required_capabilities=(
                    COSECHA_INSTRUMENTATION_BOOTSTRAP,
                    COSECHA_INSTRUMENTATION_SESSION_SUMMARY,
                ),
                description="Instrumentation that prepares and collects a session summary.",
            ),
            ConformanceTier(
                name=COSECHA_INSTRUMENTATION_STRUCTURED_TIER,
                required_capabilities=(
                    COSECHA_INSTRUMENTATION_BOOTSTRAP,
                    COSECHA_INSTRUMENTATION_SESSION_SUMMARY,
                    COSECHA_INSTRUMENTATION_STRUCTURED_SUMMARY,
                ),
                description=(
                    "Instrumentation that exposes a structured serializable "
                    "summary in addition to collecting it."
                ),
            ),
        ),
    )
)

COSECHA_INSTRUMENTATION_SUMMARY_PROFILE = CapabilityProfile(
    name=COSECHA_INSTRUMENTATION_SUMMARY_PROFILE_NAME,
    interface=COSECHA_INSTRUMENTATION_INTERFACE,
    requirements=(
        CapabilityRequirement(
            capability_name=COSECHA_INSTRUMENTATION_BOOTSTRAP,
            required_operations=(COSECHA_INSTRUMENTATION_PREPARE,),
        ),
        CapabilityRequirement(
            capability_name=COSECHA_INSTRUMENTATION_SESSION_SUMMARY,
            required_operations=(COSECHA_INSTRUMENTATION_COLLECT,),
            required_metadata_keys=(
                "instrumentation_name",
                "summary_kind",
            ),
        ),
    ),
    description="Summary-producing instrumentation profile.",
)

COSECHA_INSTRUMENTATION_STRUCTURED_PROFILE = CapabilityProfile(
    name=COSECHA_INSTRUMENTATION_STRUCTURED_PROFILE_NAME,
    interface=COSECHA_INSTRUMENTATION_INTERFACE,
    requirements=(
        CapabilityRequirement(
            capability_name=COSECHA_INSTRUMENTATION_STRUCTURED_SUMMARY,
            required_operations=(COSECHA_INSTRUMENTATION_COLLECT,),
            required_metadata_keys=("payload_formats",),
        ),
    ),
    description="Structured instrumentation profile.",
)

__all__ = (
    "COSECHA_INSTRUMENTATION_BOOTSTRAP",
    "COSECHA_INSTRUMENTATION_CATALOG",
    "COSECHA_INSTRUMENTATION_COLLECT",
    "COSECHA_INSTRUMENTATION_INTERFACE",
    "COSECHA_INSTRUMENTATION_PREPARE",
    "COSECHA_INSTRUMENTATION_SESSION_SUMMARY",
    "COSECHA_INSTRUMENTATION_STRUCTURED_PROFILE",
    "COSECHA_INSTRUMENTATION_STRUCTURED_PROFILE_NAME",
    "COSECHA_INSTRUMENTATION_STRUCTURED_SUMMARY",
    "COSECHA_INSTRUMENTATION_STRUCTURED_TIER",
    "COSECHA_INSTRUMENTATION_SUMMARY_PROFILE",
    "COSECHA_INSTRUMENTATION_SUMMARY_PROFILE_NAME",
    "COSECHA_INSTRUMENTATION_SUMMARY_TIER",
    "InstrumentationSummaryMetadata",
    "StructuredSummaryMetadata",
)
