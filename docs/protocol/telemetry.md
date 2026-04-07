# Protocolo de Telemetría

## Propósito
La telemetría en CXP es el sobre estructurado mínimo necesario para que un provider reporte hechos en tiempo de ejecución y medidas agregadas a un orquestador.

## Modelo Actual
La API actual expone estos tipos y helpers:

- `TelemetryEvent`
- `TelemetryMetric`
- `TelemetrySpan`
- `TelemetrySnapshot`
- `TelemetryContext`
- `TelemetryBuffer`

Un `TelemetrySnapshot` contiene:

- `provider_id`: identidad textual del emisor;
- `status`: estado declarado del componente;
- `events`: hechos discretos de runtime;
- `metrics`: medidas agregadas;
- `spans`: trabajo temporal ya cerrado;
- `is_heartbeat`: marca opcional para snapshots periódicos.
- `dropped_items`: número de elementos descartados desde el último `flush()` del buffer.

## Eventos y Métricas
`TelemetryEvent` modela un hecho puntual e incluye:

- `event_type`
- `severity`
- `payload`
- `timestamp`
- `trace_id`

`TelemetryMetric` modela una medida agregada e incluye:

- `name`
- `value`
- `unit`
- `labels`
- `timestamp`

`TelemetrySpan` modela trabajo temporal ya cerrado e incluye:

- `trace_id`
- `span_id`
- `parent_span_id`
- `name`
- `start_time`
- `end_time`
- `attributes`

## Helpers Disponibles
La API actual también incluye:

- `TelemetrySnapshot.heartbeat(...)`: crea un snapshot periódico de forma rápida.
- `TelemetryContext`: propaga `trace_id` al crear eventos. Si no recibe uno explícito, genera un identificador estable y lo reutiliza para eventos y spans del mismo contexto.
- `TelemetryContext.create_metric(...)`: crea métricas aplicando el mismo
  contexto operacional.
- `TelemetryContext.create_span(...)`: crea spans cerrados asociados al `trace_id`.
- `TelemetryBuffer`: acumula eventos, métricas y spans antes de generar un snapshot. Puede configurarse con `max_items` para evitar crecimiento indefinido.

```python
from cxp import TelemetryBuffer, TelemetryContext

context = TelemetryContext(trace_id="trace-123")
buffer = TelemetryBuffer(provider_id="example-mongodb")
buffer.record_event(context.create_event("command_started"))
buffer.record_span(
    context.create_span(
        "mongo.find",
        start_time=1.0,
        end_time=1.2,
    )
)
buffer.record_metric("ops", 1)
snapshot = buffer.flush(status="healthy", is_heartbeat=True)
```

## Telemetría Contextual
Además de `trace_id`, CXP define una convención compartida para correlación
operacional transversal:

- `cxp.request.id`
- `cxp.session.id`
- `cxp.operation.id`
- `cxp.parent.operation.id`

Estos campos no sustituyen a `trace_id`, `span_id` ni `parent_span_id`.

Su papel es distinto:

- `trace_id/span_id` mantienen la correlación técnica de tracing;
- los campos `cxp.*.id` permiten correlacionar request, sesión y operación
  entre dominios semánticamente distintos.

En v1 esta convención es aditiva:

- `TelemetryContext` puede inyectarla automáticamente;
- los catálogos first-party no están obligados a exigirla de forma global;
- `validate_telemetry_snapshot(...)` no la impone por defecto.

```python
from cxp import TelemetryContext

context = TelemetryContext(
    trace_id="trace-123",
    request_id="req-42",
    session_id="sess-9",
    operation_id="op-15",
    parent_operation_id="op-root",
)

event = context.create_event("browser.action.started")
span = context.create_span(
    "browser.action",
    start_time=1.0,
    end_time=1.2,
)
metric = context.create_metric(
    "browser.action.duration",
    0.2,
    unit="s",
)
```

`TelemetryContext` rellena esos campos solo cuando faltan. Si el caller pasa una
clave explícitamente en `payload`, `attributes` o `labels`, ese valor prevalece.

Si necesitas controlar qué ocurre al superar la capacidad, `TelemetryBuffer` soporta estas políticas:

- `raise`
- `drop_newest`
- `drop_oldest`

```python
from cxp import TelemetryBuffer

buffer = TelemetryBuffer(
    provider_id="example-mongodb",
    max_items=1000,
    overflow_policy="drop_oldest",
)
```

En los modos `drop_newest` y `drop_oldest`, el buffer mantiene un contador `dropped_items` y lo transporta también dentro de `TelemetrySnapshot.dropped_items`.
Si la política es `raise`, el buffer lanza `TelemetryBufferOverflow`.

## Streaming
Además del polling puntual de snapshots, el core admite providers que publiquen un stream continuo de `TelemetrySnapshot`:

- `TelemetryStreamProvider`
- `AsyncTelemetryStreamProvider`
- `stream_provider_telemetry(...)`
- `stream_provider_telemetry_async(...)`

## Lo Que Aún No Define el Núcleo
El núcleo actual no define todavía:

- una taxonomía universal de telemetría válida para todos los dominios;
- semántica de negocio asociada a cada estado de salud;
- obligatoriedad global de un mismo vocabulario de spans, métricas y eventos para todas las interfaces.

Lo que sí permite ahora el core es que cada catálogo de interfaz publique su
propio vocabulario canónico de telemetría cuando el dominio lo necesite.

Eso ya se usa en catálogos first-party como:

- `execution/plan-run`, con señales separadas para `run`, `planning` y estado;
- `database/mongodb`, con señales distintas para operaciones documentales,
  `aggregate`, `$search`, `$vectorSearch`, transacciones y topología.
- `browser/playwright`, con señales específicas para navegación, resolución de
  locators, acciones DOM, waits, red, screenshots y dialogs.
- `cosecha/engine`, `cosecha/reporter` y `cosecha/plugin`, con una convención
  `span-only` para lifecycle, knowledge, reporting y efectos de plugins.

## Semántica de Catálogo
Los catálogos de capabilities también pueden declarar semántica de telemetría
por capability.

Eso permite describir, para una capability concreta:

- spans canónicos;
- métricas canónicas;
- eventos canónicos;
- atributos, labels o claves de payload requeridas.

La API expone estos tipos:

- `CapabilityTelemetry`
- `TelemetryFieldRequirement`
- `TelemetrySpanSpec`
- `TelemetryMetricSpec`
- `TelemetryEventSpec`
- `TelemetryValidationResult`

Y cada `CapabilityCatalog` puede validar un `TelemetrySnapshot` contra un
conjunto de capabilities:

- `validate_telemetry_snapshot(snapshot, capability_names)`
- `is_telemetry_snapshot_compliant(snapshot, capability_names)`

La diferencia importante respecto a capabilities es esta: la validación de
telemetría comprueba semántica de los elementos emitidos, pero no exige que
todas las señales definidas aparezcan en cada snapshot.

Además, la validación ignora por defecto señales extra ajenas al subconjunto de
capabilities que se esté comprobando. Si el integrador necesita un modo más
estricto, puede usar `reject_unknown_signals=True`.
