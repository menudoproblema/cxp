# `cosecha/instrumentation`

Catalogo first-party para instrumentaciones de sesion de Cosecha.

## Proposito
Separa instrumentaciones como coverage del lifecycle de plugins y las
modela como componentes que preparan bootstrap y producen resumentes de
sesion estructurados. La persistencia del resumen dentro del artefacto
de sesion pertenece al core, no a la instrumentacion.

## Capabilities
- `instrumentation_bootstrap`
- `session_summary`
- `structured_summary`

## Operaciones
- `instrumentation.prepare`
- `instrumentation.collect`

## Tiers
- `summary`
- `structured`
