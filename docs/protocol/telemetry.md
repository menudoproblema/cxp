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

- una taxonomía estándar de eventos por dominio;
- semántica de negocio asociada a cada estado de salud;
- vocabulario canónico de métricas por interfaz.

Esas piezas se introducirán más adelante cuando el contrato de telemetría madure.
