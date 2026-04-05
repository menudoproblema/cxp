# Catálogo de Execution Engine

## Interfaz
Este catálogo define la familia abstracta `execution/engine`.

No publica capabilities, operaciones ni tiers. Su función es servir como
objetivo de compatibilidad para contratos concretos de ejecución.

## Compatibilidad Pública
La familia abstracta usa símbolos propios:

- `EXECUTION_ENGINE_FAMILY_INTERFACE`
- `EXECUTION_ENGINE_FAMILY_CATALOG`

Por compatibilidad histórica, los símbolos legacy:

- `EXECUTION_ENGINE_INTERFACE`
- `EXECUTION_ENGINE_CATALOG`
- `cxp.catalogs.interfaces.execution.engine`

siguen apuntando al contrato concreto [`execution/plan-run`](./plan-run.md),
no a esta familia abstracta.

## Rol
La familia `execution/engine` representa “algún tipo de engine orientado a
ejecución” expuesto al orquestador.

Los contratos concretos deben declararse en interfaces hijas y relacionarse con
esta familia mediante `satisfies_interfaces`.

## Catálogos Concretos Relacionados
- [`execution/plan-run`](./plan-run.md)

## Validación
Al ser un catálogo abstracto:

- no valida `CapabilityMatrix`;
- no valida snapshots de capabilities;
- no define tiers ni profiles.

Sí participa en la jerarquía de interfaces durante el handshake cuando un
provider concreto satisface esta familia.
