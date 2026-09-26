# `cosecha/runtime`

Catalogo first-party para runtime providers de Cosecha.

## Proposito
Modela ejecucion, aislamiento, workers, recursos y observabilidad live
como contrato propio del runtime, no del engine.

## Capabilities
- `injected_execution_plans`
- `isolated_processes`
- `persistent_workers`
- `run_scoped_resources`
- `worker_scoped_resources`
- `live_execution_observability`

## Operaciones
- `run`
- `execution.subscribe`
- `execution.live_status`
- `execution.live_tail`

## Tiers
- `local`
- `process`
- `observable`
