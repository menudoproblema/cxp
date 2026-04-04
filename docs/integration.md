# Integración

## Superficie Mínima de Integración
El repositorio define una superficie de integración deliberadamente pequeña. 

Esa superficie mínima se apoya en:

- `ComponentIdentity`
- `CapabilityMatrix`
- handshake
- telemetría síncrona o asíncrona

Además, CXP ofrece una capa opcional de descripción rica cuando un integrador necesite publicar algo más que una lista plana de capabilities.

### Síncrona vs Asíncrona
CXP soporta tanto integraciones bloqueantes (síncronas) como no bloqueantes (asíncronas). Esto es crítico para componentes que realizan I/O (como `mongoeco2`).

## Protocolos de Proveedor
Un proveedor puede implementar la interfaz síncrona o asíncrona:

```python
from collections.abc import AsyncIterator, Iterator

from cxp import (
    CapabilityMatrix,
    ComponentCapabilitySnapshot,
    ComponentIdentity,
    TelemetrySnapshot,
)

# Síncrono
class MyProvider:
    def cxp_identity(self) -> ComponentIdentity: ...
    def cxp_capabilities(self) -> CapabilityMatrix: ...
    def cxp_capability_snapshot(self) -> ComponentCapabilitySnapshot: ...
    def cxp_telemetry_provider_id(self) -> str: ...
    def cxp_telemetry_snapshot(self) -> TelemetrySnapshot | None: ...
    def cxp_telemetry_stream(self) -> Iterator[TelemetrySnapshot]: ...

# Asíncrono
class MyAsyncProvider:
    async def cxp_identity(self) -> ComponentIdentity: ...
    async def cxp_capabilities(self) -> CapabilityMatrix: ...
    async def cxp_capability_snapshot(self) -> ComponentCapabilitySnapshot: ...
    def cxp_telemetry_provider_id(self) -> str: ...
    async def cxp_telemetry_snapshot(self) -> TelemetrySnapshot | None: ...
    async def cxp_telemetry_stream(self) -> AsyncIterator[TelemetrySnapshot]: ...
```

## Negociación (Handshake)
La negociación se realiza mediante los ayudantes proporcionados:

```python
from cxp import (
    negotiate_with_async_provider,
    negotiate_with_async_provider_catalog,
    negotiate_with_provider,
    negotiate_with_provider_catalog,
)

# Caso síncrono
response = negotiate_with_provider(request, provider)

# Caso asíncrono
response = await negotiate_with_async_provider(request, async_provider)

# Caso síncrono validando además contra catálogo
response = negotiate_with_provider_catalog(request, provider, catalog)

# Caso asíncrono validando además contra catálogo
response = await negotiate_with_async_provider_catalog(
    request,
    async_provider,
    catalog,
)
```

La negociación valida `protocol_version`. Si el provider no soporta la versión pedida, la respuesta se rechaza explícitamente.
También rechaza identidades con `interface` incompatibles entre cliente y provider.
Si faltan solo `optional_capabilities`, la negociación responde con estado `degraded` en lugar de `rejected`.
Si quieres que la respuesta quede validada también contra el catálogo canónico, usa las variantes `*_catalog(...)`.
Cuando falten capabilities requeridas u opcionales, la respuesta también lo expone de forma estructurada en `missing_required_capabilities` y `missing_optional_capabilities`.
El request no debe repetir una misma capability en `required_capabilities` y `optional_capabilities`; CXP lo rechaza explícitamente.

## Cuándo Usar `CapabilityMatrix`
Usa `CapabilityMatrix` cuando necesites:

- negociar soporte mínimo durante el handshake;
- validar tiers de conformidad;
- intercambiar solo la superficie funcional esencial del provider.

Ese es el contrato mínimo y estable del protocolo.

## Cuándo Usar Descriptores Ricos
Usa `CapabilityDescriptor`, `ComponentCapabilitySnapshot` y `ComponentDependencyRule` cuando necesites publicar:

- nivel de soporte por capability;
- operaciones tipadas asociadas;
- atributos o metadata enriquecida;
- dependencias declarativas entre componentes.

Esta capa es útil para orquestadores que necesiten inspección estructural más rica, pero no sustituye al handshake.
La proyección recomendada hacia handshake sigue siendo la negociable (`supported`). Si necesitas una vista plana que conserve `accepted_noop` para diagnóstico local, úsala fuera del handshake.

Cuando un provider la expone, los helpers recomendados son:

```python
from cxp import (
    collect_provider_capability_snapshot,
    collect_provider_capability_snapshot_async,
)

snapshot = collect_provider_capability_snapshot(provider)
async_snapshot = await collect_provider_capability_snapshot_async(async_provider)
```

Estos helpers:

- inyectan `identity` si el snapshot no la trae;
- rechazan snapshots cuya identidad no coincide con la del provider;
- mantienen separado el uso de snapshots ricos respecto al handshake.

## Telemetría
De igual forma, la recolección de telemetría soporta ambos modos:

```python
from cxp import collect_provider_telemetry, collect_provider_telemetry_async

# Caso síncrono
snapshot = collect_provider_telemetry(provider)

# Caso asíncrono
snapshot = await collect_provider_telemetry_async(async_provider)
```

Si el provider expone telemetría continua, también puede publicar un stream de snapshots:

```python
from cxp import stream_provider_telemetry, stream_provider_telemetry_async

for snapshot in stream_provider_telemetry(provider):
    ...

async for snapshot in stream_provider_telemetry_async(async_provider):
    ...
```

Si el provider puede producir ráfagas grandes de telemetría, puedes acotar el buffer:

```python
from cxp import TelemetryBuffer

buffer = TelemetryBuffer(
    provider_id="mongoeco2",
    max_items=1000,
    overflow_policy="drop_oldest",
)
```

Las políticas disponibles son `raise`, `drop_newest` y `drop_oldest`.

## Ejemplo Completo (Async)
```python
from cxp import (
    Capability,
    CapabilityMatrix,
    ComponentIdentity,
    HandshakeRequest,
    negotiate_with_async_provider,
)

class MongoProvider:
    async def cxp_identity(self) -> ComponentIdentity:
        return ComponentIdentity(
            interface="database/mongodb",
            provider="mongoeco2",
            version="3.0.0",
        )

    async def cxp_capabilities(self) -> CapabilityMatrix:
        return CapabilityMatrix(
            capabilities=(
                Capability(name="read"),
                Capability(name="write"),
            )
        )

request = HandshakeRequest(
    client_identity=ComponentIdentity(
        interface="database/mongodb",
        provider="cosecha",
        version="1.0.0",
    ),
    required_capabilities=("read",),
)

response = await negotiate_with_async_provider(request, MongoProvider())
```

## Responsabilidades del Orquestador
1. Construir un `HandshakeRequest`.
2. Negociar contra el adaptador del proveedor (usando la versión `async` si el proveedor lo requiere).
3. Validar la respuesta contra el catálogo con `validate_capability_matrix()`, `validate_capability_names()`, `satisfied_tiers()` o `invalid_capability_metadata()` cuando aplique, o directamente negociar con `negotiate_with_provider_catalog()` / `negotiate_with_async_provider_catalog()`.
4. Si el provider publica descriptores ricos, recogerlos mediante `collect_provider_capability_snapshot()` o `collect_provider_capability_snapshot_async()`.
5. Validarlos contra el catálogo con `validate_component_snapshot()` o `is_component_snapshot_compliant()`.
6. Consumir `TelemetrySnapshot` periódicamente.

Si la interfaz usa operaciones tipadas además de capabilities, el catálogo también puede describirlas mediante `CatalogOperation`. Ese enriquecimiento vive en la capa de catálogo y no cambia el handshake básico.

## Ejemplos Ejecutables
El repositorio incluye ejemplos mínimos ya ejecutables:

- `examples/sync_provider.py`
- `examples/async_provider.py`
- `examples/async_telemetry_stream.py`
- `examples/component_descriptors.py`

Los dos primeros muestran identidad, capabilities, handshake y snapshot de telemetría. El tercero muestra telemetría continua mediante stream asíncrono. El cuarto muestra cómo publicar un `ComponentCapabilitySnapshot` y una `ComponentDependencyRule` sin tocar el handshake.
