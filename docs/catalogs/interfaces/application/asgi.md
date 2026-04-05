# Catálogo de ASGI Application

> Estado actual: catálogo provisional. Modela el contrato interoperable de aplicaciones ASGI, incluyendo extensiones optativas relevantes para consumers reales.

## Interfaz
Este catálogo define el vocabulario canónico de capabilities para `application/asgi`.

## Capabilities Canónicas
- `http`: protocolo HTTP base con `http.scope.inspect`, `http.request.receive`, `http.disconnect.receive`, `http.response.start` y `http.response.body`.
- `websocket`: protocolo WebSocket con surface completa de connect, accept, receive, send, close y disconnect.
- `lifespan`: lifecycle de startup y shutdown.
- `tls`: extensión TLS con `tls.scope.inspect`.
- `websocket_denial_response`: denegación HTTP para WebSocket.
- `http_server_push`: `http.response.push`.
- `http_zero_copy_send`: `http.response.zerocopysend`.
- `http_path_send`: `http.response.pathsend`.
- `http_early_hints`: `http.response.early_hint`.
- `http_trailers`: `http.response.trailers`.

## Tiers de Conformidad
### HTTP Core
- `http`

### Web Core
- `http`
- `lifespan`

### Realtime
- `http`
- `lifespan`
- `websocket`

## Metadata Esperada
- `http`: `specVersion`, `httpVersions`
- `websocket`: `specVersion`, `subprotocols`
- `lifespan`: `specVersion`
- `tls`: `scopeKeys`

## Perfiles Reutilizables
- `asgi-http-core`
- `asgi-lifespan`
- `asgi-web-core`
- `asgi-realtime`
- `asgi-tls-aware`
- `asgi-extended-http`
- `asgi-websocket-denial`
- `asgi-early-hints`

## Compatibilidad
`application/asgi` satisface `application/http`.

## Ejemplos
Pedir explícitamente una aplicación ASGI:

```python
from cxp import ComponentIdentity, HandshakeRequest

request = HandshakeRequest(
    client_identity=ComponentIdentity(
        interface="application/asgi",
        provider="cosecha",
        version="1.0.0",
    ),
    required_capabilities=("http", "lifespan"),
)
```

Modelar una app ASGI servida junto a `transport/http`:

```python
from cxp import CapabilityDescriptor, ComponentCapabilitySnapshot, ComponentIdentity

app = ComponentCapabilitySnapshot(
    component_name="users-app",
    identity=ComponentIdentity(
        interface="application/asgi",
        provider="users-app",
        version="1.0.0",
    ),
    capabilities=(
        CapabilityDescriptor(name="http", level="supported"),
        CapabilityDescriptor(name="lifespan", level="supported"),
    ),
)

server = ComponentCapabilitySnapshot(
    component_name="uvicorn",
    identity=ComponentIdentity(
        interface="transport/http",
        provider="uvicorn",
        version="1.0.0",
    ),
    capabilities=(
        CapabilityDescriptor(name="network_transport", level="supported"),
        CapabilityDescriptor(name="streaming", level="supported"),
    ),
)
```
