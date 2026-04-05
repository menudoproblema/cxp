# Catálogos

## Propósito
Un catálogo CXP define el vocabulario interoperable de una interfaz concreta.

Su papel no es negociar capabilities ni ejecutar comportamiento. Su papel es definir nombres canónicos y tiers de conformidad para que providers y orquestadores hablen el mismo lenguaje de dominio.

En el estado actual del repositorio, la infraestructura genérica de catálogos está cerrada, pero los vocabularios concretos de dominio siguen siendo revisables. Eso significa que los catálogos existentes deben leerse como base de trabajo interoperable, no todavía como estándar definitivo.

## Responsabilidades
- Asociar un nombre de `interface` estable a un dominio interoperable.
- Definir nombres canónicos de capabilities para esa interfaz.
- Definir tiers de conformidad cuando el dominio necesite perfiles comunes de soporte.
- Dejar los detalles específicos del provider en metadata o extensiones de nivel superior.

## No Responsabilidades
- Un catálogo no implementa el handshake.
- Un catálogo no ejecuta la lógica del provider.
- Un catálogo no sustituye a la telemetría.
- Un catálogo no transporta configuración específica de una implementación.

## Modelo en Código
La capa genérica de catálogos expone:

- `CapabilityCatalog`
- `CatalogCapability`
- `CatalogOperation`
- `ConformanceTier`
- `CatalogRegistry`

Además, un catálogo puede declararse como abstracto y expresar compatibilidad
con otras interfaces mediante `satisfies_interfaces`.

Los catálogos concretos de dominio se construyen sobre esa capa genérica y viven en código bajo `src/cxp/catalogs/interfaces/`.
Los catálogos first-party se registran automáticamente en `DEFAULT_CATALOG_REGISTRY` al importar el paquete, y el registro ya no sobrescribe interfaces distintas de forma silenciosa: una duplicada conflictiva lanza error salvo que se use reemplazo explícito.
La idempotencia del registro se apoya en la igualdad estructural de `msgspec.Struct`, incluyendo la identidad real de tipos usados como `metadata_schema`.

Catálogos first-party actuales:

- [`cosecha/engine`](./interfaces/cosecha/engine.md)
- [`cosecha/reporter`](./interfaces/cosecha/reporter.md)
- [`cosecha/plugin`](./interfaces/cosecha/plugin.md)
- [`browser/automation`](./interfaces/browser/automation.md)
- [`browser/playwright`](./interfaces/browser/playwright.md)
- [`database/mongodb`](./interfaces/database/mongodb.md)
- [`transport/http`](./interfaces/transport/http.md)
- [`application/http`](./interfaces/application/http.md)
- [`application/http-framework`](./interfaces/application/http-framework.md)
- [`application/wsgi`](./interfaces/application/wsgi.md)
- [`application/asgi`](./interfaces/application/asgi.md)
- [`execution/engine`](./interfaces/execution/engine.md)
- [`execution/plan-run`](./interfaces/execution/plan-run.md)

Nota sobre execution:

- `execution/engine` es una familia abstracta de compatibilidad.
- `execution/plan-run` es el contrato first-party concreto.
- Los aliases legacy `EXECUTION_ENGINE_*` siguen apuntando al contrato
  concreto `execution/plan-run`.

Nota sobre browser:

- `browser/automation` es una familia abstracta de compatibilidad.
- `browser/playwright` es el contrato first-party concreto actual.

Nota sobre Cosecha:

- `cosecha/engine`, `cosecha/reporter` y `cosecha/plugin` son contratos concretos.
- Están pensados para extensiones propias de Cosecha y no participan en la validación de runtime profiles reservados como `application/*`, `database/*`, `execution/*` o `transport/*`.

## Capabilities y Operaciones
Un catálogo puede describir dos niveles:

- `Capability`: área funcional interoperable.
- `Operation`: acción tipada asociada a una capability.

Esto permite modelar interfaces donde no basta con decir "qué puede hacer", sino también "qué operaciones concretas publica". Es especialmente útil en catálogos como `execution/plan-run`.

La misma autoridad semántica del catálogo puede reutilizarse sobre la capa rica de descriptores:

- `validate_capability_descriptors(...)`
- `validate_component_snapshot(...)`
- `is_component_snapshot_compliant(...)`

Eso permite validar snapshots completos de componente sin convertir el catálogo en parte del handshake.

Los catálogos abstractos existen para compatibilidad de familia y no deben
usarse como objetivo de validación de capabilities.

## Telemetría Asociada
Un `CatalogCapability` también puede declarar semántica de telemetría asociada
a esa capability.

Eso permite definir spans, métricas y eventos canónicos esperables para una
surface funcional dada, junto con los atributos o labels mínimos que deben
acompañarlos.

La validación de telemetría no forma parte del handshake. Es una validación
opcional posterior sobre `TelemetrySnapshot`.

## Metadata Tipada
Una `CatalogCapability` también puede declarar un `metadata_schema`. Ese esquema actúa como contrato esperado para la metadata publicada por el provider en la `CapabilityMatrix`.

La capa de catálogo expone helpers para validarlo tanto sobre `CapabilityMatrix` como sobre descriptores ricos:

- `validate_capability_matrix(matrix, ...)`
- `invalid_capability_metadata(matrix)`
- `is_capability_matrix_compliant(matrix, ...)`
- `validate_component_snapshot(snapshot)`
- `is_component_snapshot_compliant(snapshot, ...)`

`validate_capability_matrix(...)` devuelve un resultado rico con:

- capabilities desconocidas;
- metadata inválida;
- tier requerido desconocido;
- capabilities ausentes para satisfacer un tier requerido.

```python
import msgspec

from cxp import Capability, CapabilityCatalog, CapabilityMatrix, CatalogCapability


class PlanningMetadata(msgspec.Struct, frozen=True):
    mode: str
    explain: bool = False


catalog = CapabilityCatalog(
    interface="execution/plan-run",
    capabilities=(
        CatalogCapability(
            name="planning",
            metadata_schema=PlanningMetadata,
        ),
    ),
)

matrix = CapabilityMatrix(
    capabilities=(
        Capability(
            name="planning",
            metadata={"mode": "strict", "explain": True},
        ),
    ),
)

assert catalog.invalid_capability_metadata(matrix) == ()
```

## Validación Básica
La API actual permite comprobar dos cosas:

1. si un conjunto de nombres contiene capabilities desconocidas para el catálogo;
2. qué tiers de conformidad satisface ese conjunto.

```python
from cxp import get_catalog

catalog = get_catalog("database/mongodb")
assert catalog is not None

unknown = catalog.validate_capability_names(("read", "write", "custom_feature"))
tiers = catalog.satisfied_tiers(("read", "write", "transactions", "aggregation", "change_streams"))
```
