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

COSECHA_PLUGIN_INTERFACE = "cosecha/plugin"

COSECHA_PLUGIN_LIFECYCLE = "plugin_lifecycle"
COSECHA_PLUGIN_SURFACE_PUBLICATION = "surface_publication"
COSECHA_PLUGIN_CAPABILITY_REQUIREMENTS = "capability_requirements"
COSECHA_PLUGIN_TIMING_SUMMARY = "timing_summary"
COSECHA_PLUGIN_TELEMETRY_EXPORT = "telemetry_export"

COSECHA_PLUGIN_INITIALIZE = "plugin.initialize"
COSECHA_PLUGIN_START = "plugin.start"
COSECHA_PLUGIN_FINISH = "plugin.finish"
COSECHA_PLUGIN_AFTER_SESSION_CLOSED = "plugin.after_session_closed"

COSECHA_PLUGIN_CORE_TIER = "core"
COSECHA_PLUGIN_CONSTRAINED_TIER = "constrained"
COSECHA_PLUGIN_TIMING_SIDECAR_TIER = "timing_sidecar"
COSECHA_PLUGIN_TELEMETRY_SIDECAR_TIER = "telemetry_sidecar"
COSECHA_PLUGIN_REPORTING_SIDECAR_TIER = "reporting_sidecar"

COSECHA_PLUGIN_CORE_PROFILE_NAME = "cosecha-plugin-core"
COSECHA_PLUGIN_CONSTRAINED_PROFILE_NAME = "cosecha-plugin-constrained"
COSECHA_PLUGIN_TIMING_SIDECAR_PROFILE_NAME = (
    "cosecha-plugin-timing-sidecar"
)
COSECHA_PLUGIN_TELEMETRY_SIDECAR_PROFILE_NAME = (
    "cosecha-plugin-telemetry-sidecar"
)
COSECHA_PLUGIN_REPORTING_SIDECAR_PROFILE_NAME = (
    "cosecha-plugin-reporting-sidecar"
)

_PLUGIN_NAME_FIELD = TelemetryFieldRequirement(name="cosecha.plugin.name")


class SurfacePublicationMetadata(msgspec.Struct, frozen=True):
    provided_surfaces: tuple[str, ...] = ()


class CapabilityRequirementsMetadata(msgspec.Struct, frozen=True):
    required_capabilities: tuple[str, ...] = ()


class PluginOutputMetadata(msgspec.Struct, frozen=True):
    output_formats: tuple[str, ...] = ()


def _plugin_span(name: str, description: str) -> CapabilityTelemetry:
    return CapabilityTelemetry(
        spans=(
            TelemetrySpanSpec(
                name=name,
                required_attributes=(_PLUGIN_NAME_FIELD,),
                description=description,
            ),
        ),
    )


COSECHA_PLUGIN_CATALOG = register_catalog(
    CapabilityCatalog(
        interface=COSECHA_PLUGIN_INTERFACE,
        description=(
            "Canonical catalog for Cosecha plugins with explicit lifecycle, "
            "surface publication and declared sidecar capabilities."
        ),
        capabilities=(
            CatalogCapability(
                name=COSECHA_PLUGIN_LIFECYCLE,
                description="Plugin initialization and shutdown lifecycle.",
                telemetry=CapabilityTelemetry(
                    spans=(
                        TelemetrySpanSpec(
                            name="plugin.initialize",
                            required_attributes=(_PLUGIN_NAME_FIELD,),
                        ),
                        TelemetrySpanSpec(
                            name="plugin.start",
                            required_attributes=(_PLUGIN_NAME_FIELD,),
                        ),
                        TelemetrySpanSpec(
                            name="plugin.finish",
                            required_attributes=(_PLUGIN_NAME_FIELD,),
                        ),
                        TelemetrySpanSpec(
                            name="plugin.after_session_closed",
                            required_attributes=(_PLUGIN_NAME_FIELD,),
                        ),
                    ),
                ),
                operations=(
                    CatalogOperation(
                        name=COSECHA_PLUGIN_INITIALIZE,
                        result_type="none",
                    ),
                    CatalogOperation(
                        name=COSECHA_PLUGIN_START,
                        result_type="none",
                    ),
                    CatalogOperation(
                        name=COSECHA_PLUGIN_FINISH,
                        result_type="none",
                    ),
                    CatalogOperation(
                        name=COSECHA_PLUGIN_AFTER_SESSION_CLOSED,
                        result_type="none",
                    ),
                ),
            ),
            CatalogCapability(
                name=COSECHA_PLUGIN_SURFACE_PUBLICATION,
                description="Publish plugin surfaces offered to the core.",
                metadata_schema=SurfacePublicationMetadata,
            ),
            CatalogCapability(
                name=COSECHA_PLUGIN_CAPABILITY_REQUIREMENTS,
                description="Publish declared plugin capability requirements.",
                metadata_schema=CapabilityRequirementsMetadata,
            ),
            CatalogCapability(
                name=COSECHA_PLUGIN_TIMING_SUMMARY,
                description="Produce timing summaries for the session.",
                metadata_schema=PluginOutputMetadata,
                telemetry=_plugin_span(
                    "plugin.timing.print_report",
                    "Timing summary emission span.",
                ),
            ),
            CatalogCapability(
                name=COSECHA_PLUGIN_TELEMETRY_EXPORT,
                description="Export telemetry streams to external sinks.",
                metadata_schema=PluginOutputMetadata,
                telemetry=_plugin_span(
                    "plugin.telemetry.sink.start",
                    "Telemetry sink startup span.",
                ),
            ),
        ),
        tiers=(
            ConformanceTier(
                name=COSECHA_PLUGIN_CORE_TIER,
                required_capabilities=(
                    COSECHA_PLUGIN_LIFECYCLE,
                    COSECHA_PLUGIN_SURFACE_PUBLICATION,
                ),
                description="Minimal plugin lifecycle contract.",
            ),
            ConformanceTier(
                name=COSECHA_PLUGIN_CONSTRAINED_TIER,
                required_capabilities=(
                    COSECHA_PLUGIN_LIFECYCLE,
                    COSECHA_PLUGIN_SURFACE_PUBLICATION,
                    COSECHA_PLUGIN_CAPABILITY_REQUIREMENTS,
                ),
                description="Plugin with explicit capability constraints.",
            ),
            ConformanceTier(
                name=COSECHA_PLUGIN_REPORTING_SIDECAR_TIER,
                required_capabilities=(
                    COSECHA_PLUGIN_LIFECYCLE,
                    COSECHA_PLUGIN_SURFACE_PUBLICATION,
                    COSECHA_PLUGIN_CAPABILITY_REQUIREMENTS,
                    COSECHA_PLUGIN_TIMING_SUMMARY,
                    COSECHA_PLUGIN_TELEMETRY_EXPORT,
                ),
                description=(
                    "Plugin that contributes both timing and telemetry "
                    "sidecars."
                ),
            ),
            ConformanceTier(
                name=COSECHA_PLUGIN_TIMING_SIDECAR_TIER,
                required_capabilities=(
                    COSECHA_PLUGIN_LIFECYCLE,
                    COSECHA_PLUGIN_SURFACE_PUBLICATION,
                    COSECHA_PLUGIN_CAPABILITY_REQUIREMENTS,
                    COSECHA_PLUGIN_TIMING_SUMMARY,
                ),
                description="Plugin that contributes a timing reporting sidecar.",
            ),
            ConformanceTier(
                name=COSECHA_PLUGIN_TELEMETRY_SIDECAR_TIER,
                required_capabilities=(
                    COSECHA_PLUGIN_LIFECYCLE,
                    COSECHA_PLUGIN_SURFACE_PUBLICATION,
                    COSECHA_PLUGIN_CAPABILITY_REQUIREMENTS,
                    COSECHA_PLUGIN_TELEMETRY_EXPORT,
                ),
                description="Plugin that contributes a telemetry export sidecar.",
            ),
        ),
    )
)

COSECHA_PLUGIN_CORE_PROFILE = CapabilityProfile(
    name=COSECHA_PLUGIN_CORE_PROFILE_NAME,
    interface=COSECHA_PLUGIN_INTERFACE,
    requirements=(
        CapabilityRequirement(
            capability_name=COSECHA_PLUGIN_LIFECYCLE,
            required_operations=(
                COSECHA_PLUGIN_INITIALIZE,
                COSECHA_PLUGIN_START,
                COSECHA_PLUGIN_FINISH,
                COSECHA_PLUGIN_AFTER_SESSION_CLOSED,
            ),
        ),
        CapabilityRequirement(
            capability_name=COSECHA_PLUGIN_SURFACE_PUBLICATION,
            required_metadata_keys=("provided_surfaces",),
        ),
    ),
    description="Core lifecycle and surface publication profile.",
)

COSECHA_PLUGIN_CONSTRAINED_PROFILE = CapabilityProfile(
    name=COSECHA_PLUGIN_CONSTRAINED_PROFILE_NAME,
    interface=COSECHA_PLUGIN_INTERFACE,
    requirements=(
        CapabilityRequirement(
            capability_name=COSECHA_PLUGIN_CAPABILITY_REQUIREMENTS,
            required_metadata_keys=("required_capabilities",),
        ),
    ),
    description="Profile for plugins that publish capability requirements.",
)

COSECHA_PLUGIN_TIMING_SIDECAR_PROFILE = CapabilityProfile(
    name=COSECHA_PLUGIN_TIMING_SIDECAR_PROFILE_NAME,
    interface=COSECHA_PLUGIN_INTERFACE,
    requirements=(
        CapabilityRequirement(
            capability_name=COSECHA_PLUGIN_TIMING_SUMMARY,
            required_metadata_keys=("output_formats",),
        ),
    ),
    description="Profile for plugins that publish timing sidecars.",
)

COSECHA_PLUGIN_TELEMETRY_SIDECAR_PROFILE = CapabilityProfile(
    name=COSECHA_PLUGIN_TELEMETRY_SIDECAR_PROFILE_NAME,
    interface=COSECHA_PLUGIN_INTERFACE,
    requirements=(
        CapabilityRequirement(
            capability_name=COSECHA_PLUGIN_TELEMETRY_EXPORT,
            required_metadata_keys=("output_formats",),
        ),
    ),
    description="Profile for plugins that publish telemetry sidecars.",
)

COSECHA_PLUGIN_REPORTING_SIDECAR_PROFILE = CapabilityProfile(
    name=COSECHA_PLUGIN_REPORTING_SIDECAR_PROFILE_NAME,
    interface=COSECHA_PLUGIN_INTERFACE,
    requirements=(
        *COSECHA_PLUGIN_TIMING_SIDECAR_PROFILE.requirements,
        *COSECHA_PLUGIN_TELEMETRY_SIDECAR_PROFILE.requirements,
    ),
    description="Profile for plugins that publish both timing and telemetry sidecars.",
)

__all__ = (
    "COSECHA_PLUGIN_AFTER_SESSION_CLOSED",
    "COSECHA_PLUGIN_CAPABILITY_REQUIREMENTS",
    "COSECHA_PLUGIN_CATALOG",
    "COSECHA_PLUGIN_CONSTRAINED_PROFILE",
    "COSECHA_PLUGIN_CONSTRAINED_PROFILE_NAME",
    "COSECHA_PLUGIN_CONSTRAINED_TIER",
    "COSECHA_PLUGIN_CORE_PROFILE",
    "COSECHA_PLUGIN_CORE_PROFILE_NAME",
    "COSECHA_PLUGIN_CORE_TIER",
    "COSECHA_PLUGIN_FINISH",
    "COSECHA_PLUGIN_INITIALIZE",
    "COSECHA_PLUGIN_INTERFACE",
    "COSECHA_PLUGIN_LIFECYCLE",
    "COSECHA_PLUGIN_REPORTING_SIDECAR_PROFILE",
    "COSECHA_PLUGIN_REPORTING_SIDECAR_PROFILE_NAME",
    "COSECHA_PLUGIN_REPORTING_SIDECAR_TIER",
    "COSECHA_PLUGIN_START",
    "COSECHA_PLUGIN_SURFACE_PUBLICATION",
    "COSECHA_PLUGIN_TELEMETRY_SIDECAR_PROFILE",
    "COSECHA_PLUGIN_TELEMETRY_SIDECAR_PROFILE_NAME",
    "COSECHA_PLUGIN_TELEMETRY_SIDECAR_TIER",
    "COSECHA_PLUGIN_TELEMETRY_EXPORT",
    "COSECHA_PLUGIN_TIMING_SIDECAR_PROFILE",
    "COSECHA_PLUGIN_TIMING_SIDECAR_PROFILE_NAME",
    "COSECHA_PLUGIN_TIMING_SIDECAR_TIER",
    "COSECHA_PLUGIN_TIMING_SUMMARY",
    "CapabilityRequirementsMetadata",
    "PluginOutputMetadata",
    "SurfacePublicationMetadata",
)
