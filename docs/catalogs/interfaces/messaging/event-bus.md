# Catálogo de Mensajería (Event Bus)

## Interfaz Base
- **Nombre:** `messaging/event-bus`
- **Descripción:** Base abstracta para sistemas de mensajería (NATS, Kafka, RabbitMQ). Soporta Pub/Sub, Request/Reply y persistencia.
- **Esquemas de Resultado:** `Message`, `MessageAck`.

### Capacidades Base
1. **`pub_sub`**: (Requerida en `core`) Distribución asíncrona uno-a-muchos (Eventos).
2. **`request_reply`**: Comunicación síncrona uno-a-uno, perfecta para CQRS Commands.
3. **`durable_streams`**: (Requerida en `reliable`) Persistencia de mensajes para reproducción (Event Sourcing).

## Especialización NATS
- **Nombre:** `messaging/nats`
- **Satisfacciones:** `messaging/event-bus`
- **Descripción:** Implementación fidedigna de NATS.io con soporte JetStream.

### Capacidades NATS
1. **`jetstream`**: (Requerida en `core`) Configuración de NATS JetStream para persistencia estricta.
2. **`subject_mapping`**: Soporte nativo de NATS para mapeo dinámico de subject.
