# `cosecha/reporter`

Catálogo first-party para reporters de Cosecha.

## Propósito
Modela la superficie comun de reporters que proyectan resultados y
declaran de forma explicita si generan salida humana o estructurada.

## Capabilities
- `report_lifecycle`
- `result_projection`
- `artifact_output`
- `structured_output`
- `human_output`

`artifact_output`, `structured_output` y `human_output` son ejes
ortogonales, no opciones excluyentes. `artifact_output` describe
persistencia o escritura final; `structured_output` y `human_output`
describen el tipo de salida. Un reporter puede satisfacer varias de
estas capabilities a la vez, por ejemplo un reporter HTML humano y
persistente o un reporter JSON estructurado y persistente.

## Metadata
- `output_kind`
- `artifact_formats`
- `supports_engine_specific_projection`

Los tiers del catálogo son conjuntos mínimos de conformidad, no una
clasificación exclusiva. Un mismo reporter puede conformar varios tiers
si publica las capabilities necesarias.

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
