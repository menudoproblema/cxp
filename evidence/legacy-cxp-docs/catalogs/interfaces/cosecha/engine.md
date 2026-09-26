# `cosecha/engine`

Catálogo first-party para engines de Cosecha.

## Propósito
Normaliza el vocabulario comun de engines sin ocultar los origenes
reales del conocimiento que publican.

## Capabilities
- `engine_lifecycle`
- `test_lifecycle`
- `draft_validation`
- `selection_labels`
- `project_definition_knowledge`
- `library_definition_knowledge`
- `project_registry_knowledge`
- `plan_explanation`
- `static_definition_discovery`
- `on_demand_definition_materialization`
- `engine_dependency_knowledge`

`selection_labels` incluye `run` como operacion publica ademas de las
operaciones de planning.

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
