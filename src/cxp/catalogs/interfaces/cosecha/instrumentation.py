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
COSECHA_INSTRUMENTATION_ACTIVATE = "instrumentation.activate"
COSECHA_INSTRUMENTATION_COLLECT = "instrumentation.collect"

COSECHA_INSTRUMENTATION_SLOT_PROCESS_ARGV = "process.argv"
COSECHA_INSTRUMENTATION_SLOT_PROCESS_SITECUSTOMIZE = (
    "process.sitecustomize"
)
COSECHA_INSTRUMENTATION_SLOT_PROCESS_ENV = "process.environment"
COSECHA_INSTRUMENTATION_SLOT_PY_SETTRACE = "python.sys.settrace"
COSECHA_INSTRUMENTATION_SLOT_PY_SETPROFILE = "python.sys.setprofile"
COSECHA_INSTRUMENTATION_SLOT_PY_MONITORING = "python.sys.monitoring/<tool_id>"

COSECHA_INSTRUMENTATION_STRATEGY_PROCESS_WRAPPER = "process_wrapper"
COSECHA_INSTRUMENTATION_STRATEGY_SITECUSTOMIZE = "sitecustomize"
COSECHA_INSTRUMENTATION_STRATEGY_IN_PROCESS = "in_process"

COSECHA_INSTRUMENTATION_SUMMARY_TIER = "summary"
COSECHA_INSTRUMENTATION_STRUCTURED_TIER = "structured"
COSECHA_INSTRUMENTATION_COMPOSABLE_TIER = "composable"

COSECHA_INSTRUMENTATION_SUMMARY_PROFILE_NAME = (
    "cosecha-instrumentation-summary"
)
COSECHA_INSTRUMENTATION_STRUCTURED_PROFILE_NAME = (
    "cosecha-instrumentation-structured"
)
COSECHA_INSTRUMENTATION_COMPOSABLE_PROFILE_NAME = (
    "cosecha-instrumentation-composable"
)

_INSTRUMENTATION_NAME_FIELD = TelemetryFieldRequirement(
    name="cosecha.instrumentation.name"
)


class InstrumentationSummaryMetadata(msgspec.Struct, frozen=True):
    instrumentation_name: str
    summary_kind: str
    measurement_scope: str | None = None


class ActivationTrigger(msgspec.Struct, frozen=True):
    kind: str
    name: str


class InstrumentationBootstrapMetadata(msgspec.Struct, frozen=True):
    bootstrap_strategy: str | None = None
    runtime_slots: tuple[str, ...] = ()
    activation_triggers: tuple[ActivationTrigger, ...] = ()


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
                description=(
                    "Prepare bootstrap contributions for an instrumented "
                    "session."
                ),
                metadata_schema=InstrumentationBootstrapMetadata,
                telemetry=_instrumentation_span(
                    "instrumentation.prepare",
                    "Instrumentation bootstrap preparation span.",
                ),
                operations=(
                    CatalogOperation(
                        name=COSECHA_INSTRUMENTATION_PREPARE,
                        result_type="instrumentation.contribution",
                    ),
                    CatalogOperation(
                        name=COSECHA_INSTRUMENTATION_ACTIVATE,
                        result_type="instrumentation.activation_request",
                    ),
                ),
            ),
            CatalogCapability(
                name=COSECHA_INSTRUMENTATION_SESSION_SUMMARY,
                description=(
                    "Collect a session summary produced by the instrumentation."
                ),
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
                description=(
                    "Instrumentation that prepares and collects a session "
                    "summary."
                ),
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
            ConformanceTier(
                name=COSECHA_INSTRUMENTATION_COMPOSABLE_TIER,
                required_capabilities=(
                    COSECHA_INSTRUMENTATION_BOOTSTRAP,
                    COSECHA_INSTRUMENTATION_SESSION_SUMMARY,
                ),
                description=(
                    # Tiers in CXP intentionally validate capability presence
                    # only. Strict composability guarantees live in the
                    # dedicated profile below, which can also require
                    # operations and metadata.
                    "Instrumentation that declares bootstrap strategy, "
                    "runtime slots and activation triggers for composition."
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

COSECHA_INSTRUMENTATION_COMPOSABLE_PROFILE = CapabilityProfile(
    name=COSECHA_INSTRUMENTATION_COMPOSABLE_PROFILE_NAME,
    interface=COSECHA_INSTRUMENTATION_INTERFACE,
    requirements=(
        # Use the profile when negotiation needs composability guarantees.
        CapabilityRequirement(
            capability_name=COSECHA_INSTRUMENTATION_BOOTSTRAP,
            required_operations=(
                COSECHA_INSTRUMENTATION_PREPARE,
                COSECHA_INSTRUMENTATION_ACTIVATE,
            ),
            required_metadata_keys=(
                "bootstrap_strategy",
                "runtime_slots",
                "activation_triggers",
            ),
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
    description="Composable instrumentation profile.",
)

__all__ = (
    "ActivationTrigger",
    "COSECHA_INSTRUMENTATION_BOOTSTRAP",
    "COSECHA_INSTRUMENTATION_CATALOG",
    "COSECHA_INSTRUMENTATION_COMPOSABLE_PROFILE",
    "COSECHA_INSTRUMENTATION_COMPOSABLE_PROFILE_NAME",
    "COSECHA_INSTRUMENTATION_COMPOSABLE_TIER",
    "COSECHA_INSTRUMENTATION_COLLECT",
    "COSECHA_INSTRUMENTATION_INTERFACE",
    "COSECHA_INSTRUMENTATION_ACTIVATE",
    "COSECHA_INSTRUMENTATION_PREPARE",
    "COSECHA_INSTRUMENTATION_SESSION_SUMMARY",
    "COSECHA_INSTRUMENTATION_SLOT_PROCESS_ARGV",
    "COSECHA_INSTRUMENTATION_SLOT_PROCESS_ENV",
    "COSECHA_INSTRUMENTATION_SLOT_PROCESS_SITECUSTOMIZE",
    "COSECHA_INSTRUMENTATION_SLOT_PY_MONITORING",
    "COSECHA_INSTRUMENTATION_SLOT_PY_SETPROFILE",
    "COSECHA_INSTRUMENTATION_SLOT_PY_SETTRACE",
    "COSECHA_INSTRUMENTATION_STRATEGY_IN_PROCESS",
    "COSECHA_INSTRUMENTATION_STRATEGY_PROCESS_WRAPPER",
    "COSECHA_INSTRUMENTATION_STRATEGY_SITECUSTOMIZE",
    "COSECHA_INSTRUMENTATION_STRUCTURED_PROFILE",
    "COSECHA_INSTRUMENTATION_STRUCTURED_PROFILE_NAME",
    "COSECHA_INSTRUMENTATION_STRUCTURED_SUMMARY",
    "COSECHA_INSTRUMENTATION_STRUCTURED_TIER",
    "COSECHA_INSTRUMENTATION_SUMMARY_PROFILE",
    "COSECHA_INSTRUMENTATION_SUMMARY_PROFILE_NAME",
    "COSECHA_INSTRUMENTATION_SUMMARY_TIER",
    "InstrumentationBootstrapMetadata",
    "InstrumentationSummaryMetadata",
    "StructuredSummaryMetadata",
)
