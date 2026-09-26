# Catálogos de Transporte y Comunicaciones

El dominio de transporte en CXP consolida los protocolos de red bajo una jerarquía fidedigna para asegurar conectividad moderna.

## 1. HTTP Canónico (`transport/http`)
Contrato concreto y estable para transporte HTTP interoperable.
- **Capacidades Base:** `headers`, `cookies`, `auth_propagation`, `middleware_observable`, `streaming`, `network_transport`.

## 2. Familia HTTP (`transport/http-family`)
Familia abstracta para especializaciones request/response con operaciones y esquemas compartidos.
- **Capacidades Base:** `request_dispatch`, `tls`.
- **Esquemas:** `HttpDispatch`, `HttpResponse`, `TlsCertificate`.

## 3. HTTP/2 (`transport/http2`)
Especialización que añade capacidades modernas.
- **`multiplexing`**: Peticiones concurrentes en la misma conexión.
- **`server_push`**: Promesas push (`HttpPushPromise`).

## 4. HTTP/3 (`transport/http3`)
Especialización QUIC.
- **`quic_transport`**: Transporte UDP seguro.
- **`connection_migration`**: Supervivencia a cambios de IP.

## 5. WebSocket (`transport/websocket`)
Interfaz independiente para canales full-duplex.
- **`full_duplex`**: Envío y recepción concurrente.
- **`binary_streams`**: Soporte para frames binarios, vital para transmisión de media en tiempo real.
- **Esquema:** `WebSocketMessage`.

## Estándar de Fidelidad
La capa de transporte comparte vocabulario de telemetría y esquemas comunes cuando aporta interoperabilidad, pero no todas las interfaces usan exactamente el mismo conjunto de campos en esta versión.
