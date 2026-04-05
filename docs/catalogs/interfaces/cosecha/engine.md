# `cosecha/engine`

Catálogo first-party para engines de Cosecha.

## Propósito
Normaliza el vocabulario común de engines sin acoplarlo a Gherkin o Pytest como contratos separados.

## Capabilities
- `engine_lifecycle`
- `test_lifecycle`
- `draft_validation`
- `selection_labels`
- `definition_knowledge`
- `plan_explanation`
- `static_definition_discovery`
- `on_demand_definition_materialization`
- `engine_dependency_knowledge`

## Telemetría
La telemetría canónica actual es `span-only` e incluye:

- `engine.collect`
- `engine.session.start`
- `engine.session.finish`
- `engine.test.start`
- `engine.test.finish`
- `engine.test.execute`
- `engine.test.phase`
- `engine.draft.validate`
- `engine.definition.resolve`
- `engine.plan.analyze`
- `engine.plan.explain`
- `engine.plan.simulate`
- `engine.dependencies.describe`

Campos mínimos esperados:

- `cosecha.engine.name`
- `cosecha.operation.name`
- `cosecha.outcome`

Campos adicionales por ejecución de test:

- `cosecha.node.id`
- `cosecha.node.stable_id`
- `cosecha.phase`
