# Catálogos de Transporte y Comunicaciones

El dominio de transporte en CXP consolida los protocolos de red bajo una jerarquía fidedigna para asegurar conectividad moderna.

## 1. Familia HTTP (`transport/http`)
La base abstracta para cualquier comunicación Request/Response.
- **Capacidades Base:** `request_dispatch`, `sse` (Server-Sent Events), `tls` (SSL).
- **Esquema:** `HttpResponse` (incluye la versión del protocolo).

## 2. HTTP/2 (`transport/http2`)
Especialización que añade capacidades modernas.
- **`multiplexing`**: Peticiones concurrentes en la misma conexión.
- **`server_push`**: Promesas push (`HttpPushPromise`).

## 3. HTTP/3 (`transport/http3`)
Especialización QUIC.
- **`quic_transport`**: Transporte UDP seguro.
- **`connection_migration`**: Supervivencia a cambios de IP.

## 4. WebSocket (`transport/websocket`)
Interfaz independiente para canales full-duplex.
- **`full_duplex`**: Envío y recepción concurrente.
- **`binary_streams`**: Soporte para frames binarios, vital para transmisión de media en tiempo real.
- **Esquema:** `WebSocketMessage`.

## Estándar de Fidelidad
Toda la capa de transporte utiliza los campos de telemetría de `common.py` (ej. `HTTP_METHOD`, `HTTP_STATUS`) para garantizar que la latencia y los bytes de red se correlacionan perfectamente con los eventos emitidos por los servidores de aplicación (ASGI/WSGI).
