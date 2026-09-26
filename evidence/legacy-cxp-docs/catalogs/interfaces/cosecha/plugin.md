# `cosecha/plugin`

Catálogo first-party para plugins de Cosecha.

## Propósito
Describe lifecycle, surfaces publicadas y capacidades laterales
declaradas explicitamente por plugins del framework.

## Capabilities
- `plugin_lifecycle`
- `surface_publication`
- `capability_requirements`
- `timing_summary`
- `telemetry_export`

## Metadata
- `provided_surfaces`
- `required_capabilities`
- `output_formats`

## Telemetría
La telemetría canónica actual es `span-only`:

- `plugin.initialize`
- `plugin.start`
- `plugin.finish`
- `plugin.after_session_closed`
- `plugin.timing.print_report`
- `plugin.telemetry.sink.start`

Campo mínimo esperado:

- `cosecha.plugin.name`
