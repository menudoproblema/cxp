# Catálogos de Interfaces CXP

CXP organiza capacidades del sistema en catálogos semánticos estructurados por familias de interfaz. Estos catálogos pueden definir capacidades, operaciones, esquemas tipados opcionales y convenciones compartidas de telemetría sin ampliar el núcleo del protocolo.

## 1. Familias Abstractas
Definen vocabulario común y relaciones de compatibilidad entre interfaces concretas.
- `application/http`
- `browser/automation`
- `database/common`
- `execution/engine`
- `messaging/event-bus`
- `notification/common`
- `printing/manager`
- `transport/http-family`

## 2. Capa de Computación y Ejecución
Gestiona el ciclo de vida de tareas, colas de trabajo y el contexto de ejecución.
- [Execution (Plan-Run)](interfaces/execution/plan-run.md): Contrato concreto para ejecución materializada, planificación, validación y observabilidad.
- [Queue (Task Engine)](interfaces/queue/task-engine.md): Procesamiento en background, monitorización y cancelación de tareas.
- [Runtime Environment](interfaces/runtime/environment.md): Gestión de secretos, configuración y recursos.
- [Application (ASGI/WSGI)](interfaces/application/asgi.md): Servidores y frameworks web de bajo nivel.
- [HTTP Framework](interfaces/application/http-framework.md): Semántica de alto nivel para aplicaciones web (routing, validation).

## 2. Capa de Persistencia (Data Layer)
Gestión de estado y almacenamiento de datos.
- [Database (SQL/NoSQL)](interfaces/database/index.md): Persistencia estructurada y documental.
- [Storage (Blob)](interfaces/storage/blob.md): Almacenamiento de objetos y archivos.
- [Cache (Key-Value)](interfaces/cache/key-value.md): Memoria rápida y estado efímero.

## 3. Capa de Seguridad e Identidad
Validación de identidades y permisos.
- [Auth Provider](interfaces/identity/auth-provider.md): Validación de tokens (JWT), perfiles de usuario y políticas (RBAC/ABAC).

## 4. Capa de Comunicaciones
Movimiento de información y eventos.
- [Transport (HTTP/WebSocket)](interfaces/transport/index.md): Semántica de red request/response (H1.1, H2, H3), WebSocket, SSE y TLS.
- [Messaging (Event Bus)](interfaces/messaging/event-bus.md): Pub/Sub y colas de eventos con persistencia (ej. NATS JetStream).
- [Notification (WebPush)](interfaces/notification/web-push.md): Notificaciones al usuario (Push, WebPush).

## 5. Capa de Experiencia y Media
Interacción con el usuario y contenido pesado.
- [Browser (Automation)](interfaces/browser/automation.md): Control de navegadores (Playwright) incluyendo LocalStorage.
- [Media (Streaming)](interfaces/media/video-streaming.md): Vídeo adaptativo (HLS/DASH) y transcodificación.

## 6. Capa Física e Industrial
Orquestación de hardware y periféricos.
- [Printing (Industrial)](interfaces/printing/industrial.md): Impresión de etiquetas (ZPL, Zebra) y acabados físicos (Konica Minolta).

## Convenciones Compartidas
Muchos catálogos reutilizan convenciones comunes para mantener coherencia entre proveedores:
1. **Telemetría Compartida**: Reutilización creciente de nombres de campos y unidades cuando aporta interoperabilidad.
2. **Esquemas Tipados Opcionales**: Validación estructural en metadata, entradas o resultados cuando el dominio lo necesita.
3. **Tiers de Conformidad**: Definición clara del nivel `core` y de superficies más avanzadas.
