from __future__ import annotations

import msgspec

from cxp.catalogs.base import (
    CapabilityCatalog,
    CapabilityTelemetry,
    CatalogCapability,
    CatalogOperation,
    TelemetryFieldRequirement,
    TelemetrySpanSpec,
    register_catalog,
)

COSECHA_PLUGIN_INTERFACE = 'cosecha/plugin'

COSECHA_PLUGIN_LIFECYCLE = 'plugin_lifecycle'
COSECHA_PLUGIN_SURFACE_PUBLICATION = 'surface_publication'
COSECHA_PLUGIN_CAPABILITY_REQUIREMENTS = 'capability_requirements'
COSECHA_PLUGIN_COVERAGE_SUMMARY = 'coverage_summary'
COSECHA_PLUGIN_TIMING_SUMMARY = 'timing_summary'
COSECHA_PLUGIN_TELEMETRY_EXPORT = 'telemetry_export'

COSECHA_PLUGIN_INITIALIZE = 'plugin.initialize'
COSECHA_PLUGIN_START = 'plugin.start'
COSECHA_PLUGIN_FINISH = 'plugin.finish'
COSECHA_PLUGIN_AFTER_SESSION_CLOSED = 'plugin.after_session_closed'

_PLUGIN_NAME_FIELD = TelemetryFieldRequirement(name='cosecha.plugin.name')


class SurfacePublicationMetadata(msgspec.Struct, frozen=True):
    provided_surfaces: tuple[str, ...] = ()


class CapabilityRequirementsMetadata(msgspec.Struct, frozen=True):
    required_capabilities: tuple[str, ...] = ()


class PluginOutputMetadata(msgspec.Struct, frozen=True):
    output_formats: tuple[str, ...] = ()


def _plugin_span(
    name: str,
    description: str,
) -> CapabilityTelemetry:
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
            'Canonical catalog for Cosecha plugins with lifecycle, surface '
            'publication, and optional reporting side effects.'
        ),
        capabilities=(
            CatalogCapability(
                name=COSECHA_PLUGIN_LIFECYCLE,
                description='Plugin initialization and shutdown lifecycle.',
                telemetry=CapabilityTelemetry(
                    spans=(
                        TelemetrySpanSpec(
                            name='plugin.initialize',
                            required_attributes=(_PLUGIN_NAME_FIELD,),
                        ),
                        TelemetrySpanSpec(
                            name='plugin.start',
                            required_attributes=(_PLUGIN_NAME_FIELD,),
                        ),
                        TelemetrySpanSpec(
                            name='plugin.finish',
                            required_attributes=(_PLUGIN_NAME_FIELD,),
                        ),
                        TelemetrySpanSpec(
                            name='plugin.after_session_closed',
                            required_attributes=(_PLUGIN_NAME_FIELD,),
                        ),
                    ),
                ),
                operations=(
                    CatalogOperation(
                        name=COSECHA_PLUGIN_INITIALIZE,
                        result_type='none',
                    ),
                    CatalogOperation(
                        name=COSECHA_PLUGIN_START,
                        result_type='none',
                    ),
                    CatalogOperation(
                        name=COSECHA_PLUGIN_FINISH,
                        result_type='none',
                    ),
                    CatalogOperation(
                        name=COSECHA_PLUGIN_AFTER_SESSION_CLOSED,
                        result_type='none',
                    ),
                ),
            ),
            CatalogCapability(
                name=COSECHA_PLUGIN_SURFACE_PUBLICATION,
                description='Publish plugin surfaces offered to the core.',
                metadata_schema=SurfacePublicationMetadata,
            ),
            CatalogCapability(
                name=COSECHA_PLUGIN_CAPABILITY_REQUIREMENTS,
                description=(
                    'Publish plugin capability requirements against the '
                    'active system.'
                ),
                metadata_schema=CapabilityRequirementsMetadata,
            ),
            CatalogCapability(
                name=COSECHA_PLUGIN_COVERAGE_SUMMARY,
                description='Produce or print session coverage summaries.',
                metadata_schema=PluginOutputMetadata,
                telemetry=CapabilityTelemetry(
                    spans=(
                        TelemetrySpanSpec(
                            name='plugin.coverage.build_summary',
                            required_attributes=(_PLUGIN_NAME_FIELD,),
                        ),
                        TelemetrySpanSpec(
                            name='plugin.coverage.print_report',
                            required_attributes=(_PLUGIN_NAME_FIELD,),
                        ),
                    ),
                ),
            ),
            CatalogCapability(
                name=COSECHA_PLUGIN_TIMING_SUMMARY,
                description='Produce timing summaries for the session.',
                metadata_schema=PluginOutputMetadata,
                telemetry=_plugin_span(
                    'plugin.timing.print_report',
                    'Timing summary emission span.',
                ),
            ),
            CatalogCapability(
                name=COSECHA_PLUGIN_TELEMETRY_EXPORT,
                description='Export telemetry streams to external sinks.',
                metadata_schema=PluginOutputMetadata,
                telemetry=_plugin_span(
                    'plugin.telemetry.sink.start',
                    'Telemetry sink startup span.',
                ),
            ),
        ),
    )
)

__all__ = (
    'COSECHA_PLUGIN_AFTER_SESSION_CLOSED',
    'COSECHA_PLUGIN_CAPABILITY_REQUIREMENTS',
    'COSECHA_PLUGIN_CATALOG',
    'COSECHA_PLUGIN_COVERAGE_SUMMARY',
    'COSECHA_PLUGIN_FINISH',
    'COSECHA_PLUGIN_INITIALIZE',
    'COSECHA_PLUGIN_INTERFACE',
    'COSECHA_PLUGIN_LIFECYCLE',
    'COSECHA_PLUGIN_START',
    'COSECHA_PLUGIN_SURFACE_PUBLICATION',
    'COSECHA_PLUGIN_TELEMETRY_EXPORT',
    'COSECHA_PLUGIN_TIMING_SUMMARY',
)
