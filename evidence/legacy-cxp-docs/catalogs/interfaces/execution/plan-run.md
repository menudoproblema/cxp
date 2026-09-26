# Catálogo de Execution Plan-Run

## Interfaz
Este catálogo define el vocabulario canónico de capabilities para la interfaz
`execution/plan-run`.

Modela un contrato concreto para engines con ejecución materializada y soporte
opcional de planificación tipada, validación previa y observabilidad de
ejecución.

## Familia
`execution/plan-run` satisface la familia abstracta [`execution/engine`](./engine.md).

## Compatibilidad Pública
Aunque el contrato canónico vive en `execution/plan-run`, CXP mantiene aliases
legacy para no romper integraciones existentes:

- `EXECUTION_ENGINE_INTERFACE == "execution/plan-run"`
- `EXECUTION_ENGINE_CATALOG is PLAN_RUN_EXECUTION_CATALOG`
- `cxp.catalogs.interfaces.execution.engine` sigue reexportando este contrato
  concreto

Los símbolos nuevos y explícitos para este catálogo son `PLAN_RUN_EXECUTION_*`.

## Capabilities
- `run`
- `planning`
- `input_validation`
- `execution_status`
- `execution_stream`

## Operaciones por Capability
### `run`
- `run` -> `run.result`

### `planning`
- `plan.analyze` -> `plan.analyzed`
- `plan.explain` -> `plan.explained`
- `plan.simulate` -> `plan.simulated`

### `input_validation`
- `input.validate` -> `input.validated`

### `execution_status`
- `execution.status` -> `execution.status`

### `execution_stream`
- `execution.subscribe` -> `execution.subscription`
- `execution.tail` -> `execution.tail`

## Tiers
### `core`
- `run`

### `planned`
- `run`
- `planning`

### `advanced`
- `run`
- `planning`
- `input_validation`
- `execution_status`
- `execution_stream`

## Perfiles Reutilizables
- `plan-run-core`: exige `run`.
- `plan-run-planned`: extiende `plan-run-core` y exige `planning`.
- `plan-run-advanced`: extiende `plan-run-planned` y exige `input_validation`, `execution_status` y `execution_stream`.

## Flujo de Consumo Recomendado
Un consumidor de `execution/plan-run` suele trabajar en dos pasos:

1. elegir un perfil reutilizable que refleje el minimo operativo que necesita;
2. validar un `ComponentCapabilitySnapshot` contra ese perfil antes de asumir operaciones concretas.

En la practica:

- `plan-run-core` sirve para engines que solo necesitan ejecutar;
- `plan-run-planned` sirve para tooling que necesita explicar o simular antes de correr;
- `plan-run-advanced` sirve para orquestadores que esperan validacion previa, inspeccion de estado y streaming de ejecucion.

## Procedencia
Este catálogo toma como referencia semánticas comunes de engines con ejecución
materializada, planificación tipada, validación previa y seguimiento de la
ejecución en curso.
