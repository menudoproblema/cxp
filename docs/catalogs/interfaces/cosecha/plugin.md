# `cosecha/plugin`

Catálogo first-party para plugins de Cosecha.

## Propósito
Describe lifecycle, surfaces publicadas y efectos observables de plugins del framework.

## Capabilities
- `plugin_lifecycle`
- `surface_publication`
- `capability_requirements`
- `coverage_summary`
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
- `plugin.coverage.build_summary`
- `plugin.coverage.print_report`
- `plugin.timing.print_report`
- `plugin.telemetry.sink.start`

Campo mínimo esperado:

- `cosecha.plugin.name`
