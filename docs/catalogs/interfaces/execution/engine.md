# Catálogo de Execution Engine

## Interfaz
Este catálogo define el vocabulario canónico de capabilities para la interfaz `execution/engine`.

## Capabilities
- `run`
- `planning`
- `draft_validation`
- `live_execution_observability`

## Operaciones por Capability
### `run`
- `run` -> `run.result`

### `planning`
- `plan.analyze` -> `plan.analyzed`
- `plan.explain` -> `plan.explained`
- `plan.simulate` -> `plan.simulated`

### `draft_validation`
- `draft.validate` -> `draft.validated`

### `live_execution_observability`
- `execution.subscribe` -> `execution.subscribe`
- `execution.live_status` -> `execution.live_status`
- `execution.live_tail` -> `execution.live_tail`

## Tiers
### `core`
- `run`
- `planning`

### `advanced`
- `run`
- `planning`
- `draft_validation`
- `live_execution_observability`

## Procedencia
Este catálogo toma como referencia la semántica pública que Cosecha ya expresa para engines de ejecución, planificación tipada, validación de draft y observabilidad viva.
