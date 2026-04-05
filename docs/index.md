# Documentación de CXP

## Visión General
CXP es un protocolo de interoperabilidad semántica para componentes de software y sus orquestadores.

Permite que un componente publique:

- qué puede hacer mediante capacidades;
- qué está ocurriendo en runtime mediante telemetría.

El protocolo se mantiene orientado a datos y agnóstico respecto a la implementación para poder usarse entre librerías, runtimes, servicios y capas de orquestación.

## Mapa de Documentación
- [Arquitectura](./architecture.md)
- [Integración](./integration.md)
- [Protocolo de Capacidades](./protocol/capabilities.md)
- [Descriptores de Capacidades](./protocol/descriptors.md)
- [Protocolo de Telemetría](./protocol/telemetry.md)
- [Catálogos](./catalogs/index.md)
- [Catálogo de Browser Automation](./catalogs/interfaces/browser/automation.md)
- [Catálogo de Playwright Browser](./catalogs/interfaces/browser/playwright.md)
- [Catálogo de Cosecha Engine](./catalogs/interfaces/cosecha/engine.md)
- [Catálogo de Cosecha Reporter](./catalogs/interfaces/cosecha/reporter.md)
- [Catálogo de Cosecha Plugin](./catalogs/interfaces/cosecha/plugin.md)
- [Catálogo de MongoDB](./catalogs/interfaces/database/mongodb.md)
- [Catálogo de HTTP Transport](./catalogs/interfaces/transport/http.md)
- [Catálogo de HTTP Application](./catalogs/interfaces/application/http.md)
- [Catálogo de HTTP Application Framework](./catalogs/interfaces/application/http-framework.md)
- [Catálogo de WSGI Application](./catalogs/interfaces/application/wsgi.md)
- [Catálogo de ASGI Application](./catalogs/interfaces/application/asgi.md)
- [Catálogo de Execution Engine](./catalogs/interfaces/execution/engine.md)
- [Catálogo de Execution Plan-Run](./catalogs/interfaces/execution/plan-run.md)

Nota rápida:
- `browser/automation` documenta la familia abstracta.
- `browser/playwright` documenta el contrato concreto actual.
- `cosecha/engine`, `cosecha/reporter` y `cosecha/plugin` documentan contratos concretos para extensiones propias de Cosecha.
- `execution/engine` documenta la familia abstracta.
- `execution/plan-run` documenta el contrato concreto actual.
- Los exports legacy `EXECUTION_ENGINE_*` siguen representando el contrato concreto por compatibilidad.

## Ejemplos
El repositorio incluye ejemplos ejecutables en:

- `examples/sync_provider.py`
- `examples/async_provider.py`
- `examples/async_telemetry_stream.py`
- `examples/component_descriptors.py`
