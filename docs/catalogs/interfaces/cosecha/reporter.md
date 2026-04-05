# `cosecha/reporter`

Catálogo first-party para reporters de Cosecha.

## Propósito
Modela la superficie común de reporters que proyectan resultados y generan salida humana o estructurada.

## Capabilities
- `report_lifecycle`
- `result_projection`
- `artifact_output`

## Metadata
- `output_kind`
- `artifact_formats`
- `supports_engine_specific_projection`

## Telemetría
La telemetría canónica actual es `span-only`:

- `reporter.start`
- `reporter.add_test`
- `reporter.add_test_result`
- `reporter.print_report`
- `reporter.output.write`

Campos mínimos esperados:

- `cosecha.reporter.name`
- `cosecha.reporter.output_kind`
