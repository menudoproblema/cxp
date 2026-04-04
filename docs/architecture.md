# Arquitectura

## Propósito
CXP es un protocolo pequeño para la interoperabilidad semántica entre un orquestador y un componente de software. Permite que un componente declare qué puede hacer e informe de lo que está ocurriendo mientras se ejecuta, sin acoplar a ninguna de las dos partes a internals específicos del provider.

## Límites del Núcleo
El núcleo del protocolo es deliberadamente estrecho.

- `ComponentIdentity` da a un componente una identidad estable dentro del protocolo.
- `CapabilityMatrix` transporta la superficie funcional ofrecida por un provider.
- `HandshakeRequest` y `HandshakeResponse` resuelven el paso inicial de negociación.
- La negociación incluye una validación explícita de `protocol_version`.
- `TelemetrySnapshot` transporta eventos, métricas y spans agregados.
- Los adaptadores del lado provider exponen esos contratos mediante variantes síncronas y asíncronas de `CapabilityProvider`, `TelemetryProvider` y `TelemetryStreamProvider`.
- Cuando un provider publica descriptores ricos, puede exponerlos mediante `CapabilitySnapshotProvider` o `AsyncCapabilitySnapshotProvider`.

Sobre ese núcleo existe una capa semántica opcional para describir componentes y relaciones de forma más rica:

- `CapabilityDescriptor` modela una capability con nivel de soporte, operaciones, atributos y metadata opcional.
- `ComponentCapabilitySnapshot` describe un componente completo con sus capabilities enriquecidas.
- `ComponentDependencyRule` expresa dependencias declarativas entre componentes sin imponer políticas concretas de un orquestador.

## Qué Le Corresponde a CXP
- Contratos a nivel de protocolo compartidos por orquestadores y providers.
- Catálogos genéricos de capabilities indexados por interfaz.
- Operaciones tipadas opcionales asociadas a capabilities cuando el dominio lo necesite.
- Esquemas tipados opcionales de metadata cuando una capability necesite validación estructural.
- Descriptores enriquecidos para publicar grafos de capacidades y relaciones declarativas entre componentes.
- El envelope mínimo de telemetría necesario para intercambiar información estructurada de runtime.

Los catálogos concretos de dominio pueden existir en el repositorio sin que eso implique que su vocabulario esté cerrado. El núcleo del protocolo y la superficie mínima de integración sí se consideran la parte estable en esta fase.

## Qué No Le Corresponde a CXP
- Internals de runtime específicos de un provider.
- Lifecycle, scheduling, placement o políticas de recursos del orquestador.
- Semánticas ricas de dominio que siguen siendo locales a un único provider.
- Políticas de readiness y degradación más allá de la superficie actual del protocolo.
- Políticas específicas de proyección, diagnosis o coordinación propias de un framework concreto.

## Capas
El repositorio se organiza en cuatro capas.

- Contratos del núcleo del protocolo.
- Capa semántica opcional de descriptores ricos.
- Guía de integración para orquestadores y providers.
- Catálogos específicos por interfaz, organizados en código bajo `src/cxp/catalogs/interfaces/`.

Esta separación mantiene el protocolo pequeño, deja la negociación mínima intacta y permite publicar modelos más ricos sin convertir el core en una copia de Cosecha ni de ningún otro consumidor.
