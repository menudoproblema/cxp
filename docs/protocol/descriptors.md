# Descriptores de Capacidades

## Propósito
La capa de descriptores permite publicar un modelo más rico que el handshake mínimo sin modificar `CapabilityMatrix`.

Su objetivo es describir:

- cómo soporta un componente cada capability;
- qué operaciones tipadas cuelgan de cada capability;
- qué atributos o metadata adicional acompañan a esa capability;
- qué dependencias declarativas existen entre componentes.

## Tipos Principales

### `CapabilityDescriptor`
Describe una capability concreta dentro de un componente.

Incluye:

- `name`
- `level`
- `summary`
- `stability`
- `attributes`
- `operations`
- `metadata`
- `delivery_mode`
- `granularity`

`level` usa tres valores:

- `supported`
- `accepted_noop`
- `unsupported`

`accepted_noop` cuenta como capability presente para validación estructural, pero no implica semántica de ejecución dentro del protocolo.
Al proyectar un `ComponentCapabilitySnapshot` a `CapabilityMatrix`, solo las capabilities con nivel `supported` pasan al handshake mediante `as_negotiated_capability_matrix()`.
Si un integrador necesita una proyección plana que también incluya `accepted_noop` para diagnóstico o planificación local, puede usar `as_capability_matrix_with_noop()`.

### `ComponentCapabilitySnapshot`
Describe un componente completo con identidad opcional y un conjunto de `CapabilityDescriptor`.

También expone helpers para:

- recuperar capabilities por nombre;
- obtener solo las capabilities ofrecidas;
- proyectar el snapshot a un `CapabilityMatrix`.

Si el snapshot se recoge mediante los helpers de provider:

- `collect_provider_capability_snapshot(...)`
- `collect_provider_capability_snapshot_async(...)`

la identidad del provider se inyecta automáticamente cuando el snapshot no la trae, y se rechaza si no coincide con la identidad declarada por el provider.

### `ComponentDependencyRule`
Describe una dependencia declarativa entre dos componentes.

El tipo mantiene deliberadamente abiertos estos campos:

- `dependency_kind`
- `projection_policy`

De este modo CXP no impone la taxonomía interna de un framework concreto.

## Relación con los Catálogos
Los catálogos siguen siendo la autoridad semántica de nombres, operaciones y metadata.

Sobre descriptores ricos, la API de catálogo ofrece:

- `validate_capability_descriptors(...)`
- `validate_component_snapshot(...)`
- `is_component_snapshot_compliant(...)`

Estas funciones validan:

- capabilities desconocidas;
- operaciones desconocidas por capability;
- metadata inválida cuando el catálogo declara `metadata_schema`.
- discrepancias entre `snapshot.identity.interface` y la `interface` del catálogo cuando la identidad está presente.

`DescriptorValidationResult` expone además `messages()` para obtener mensajes legibles por humanos a partir del resultado de validación.

## Superficie de Provider
La capa rica no forma parte del handshake, pero sí tiene una superficie first-party para providers:

```python
from cxp import ComponentCapabilitySnapshot, ComponentIdentity

class MyProvider:
    def cxp_identity(self) -> ComponentIdentity: ...
    def cxp_capability_snapshot(self) -> ComponentCapabilitySnapshot: ...
```

Y su variante asíncrona:

```python
from cxp import ComponentCapabilitySnapshot, ComponentIdentity

class MyAsyncProvider:
    async def cxp_identity(self) -> ComponentIdentity: ...
    async def cxp_capability_snapshot(self) -> ComponentCapabilitySnapshot: ...
```

Esta superficie sirve para inspección, diagnóstico y persistencia de estado semántico más rico. No sustituye a `cxp_capabilities()` ni al handshake.

## Ejemplo
```python
from cxp import (
    CapabilityDescriptor,
    CapabilityOperationBinding,
    ComponentCapabilitySnapshot,
    ComponentDependencyRule,
    ComponentIdentity,
    get_catalog,
)

snapshot = ComponentCapabilitySnapshot(
    component_name="gherkin",
    component_kind="engine",
    identity=ComponentIdentity(
        interface="execution/plan-run",
        provider="gherkin",
        version="1.0.0",
    ),
    capabilities=(
        CapabilityDescriptor(
            name="planning",
            level="supported",
            operations=(
                CapabilityOperationBinding(
                    operation_name="plan.analyze",
                    result_type="plan.analyzed",
                ),
                CapabilityOperationBinding(
                    operation_name="plan.explain",
                    result_type="plan.explained",
                ),
            ),
            metadata={"mode": "strict"},
        ),
    ),
)

dependency = ComponentDependencyRule(
    source_component="gherkin",
    target_component="pytest",
    dependency_kind="knowledge",
    projection_policy="diagnostic_only",
    required_capabilities=("planning",),
    required_operations=("plan.explain",),
)

catalog = get_catalog("execution/plan-run")
assert catalog is not None
assert catalog.is_component_snapshot_compliant(snapshot) is True
```
