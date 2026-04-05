# Catálogo de HTTP Application

> Estado actual: familia abstracta. No define capabilities canónicas propias y existe para expresar compatibilidad entre contratos concretos de aplicación HTTP.

## Interfaz
Este catálogo representa la familia abstracta `application/http`.

## Rol
- permitir que un consumer pida "cualquier aplicación HTTP";
- servir como objetivo de compatibilidad para `application/wsgi` y `application/asgi`;
- no sustituir a los catálogos concretos cuando haya que validar capabilities, tiers o metadata.

## Capabilities
No define capabilities, operaciones, tiers ni perfiles reutilizables.

Los integradores deben usar:

- [`application/wsgi`](./wsgi.md) cuando necesiten el contrato WSGI;
- [`application/asgi`](./asgi.md) cuando necesiten el contrato ASGI;
- [`application/http-framework`](./http-framework.md) cuando necesiten la semántica de framework HTTP antes publicada bajo `application/http`.

## Compatibilidad
- `application/wsgi` satisface `application/http`
- `application/asgi` satisface `application/http`
- `application/http` no satisface por sí misma a `application/wsgi` ni `application/asgi`

## Ejemplos
Pedir cualquier aplicación HTTP:

```python
from cxp import ComponentIdentity, HandshakeRequest

request = HandshakeRequest(
    client_identity=ComponentIdentity(
        interface="application/http",
        provider="cosecha",
        version="1.0.0",
    ),
    required_capabilities=(),
)
```

El handshake podrá aceptar un provider `application/wsgi` o `application/asgi`.

## Deprecación
La semántica anterior de framework HTTP se mantiene en `application/http-framework`.
