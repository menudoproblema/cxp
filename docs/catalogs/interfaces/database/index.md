# Catálogos de Base de Datos

CXP organiza las capacidades de persistencia bajo una jerarquía que permite interoperabilidad básica y especialización por motor.

## 1. Familia Base (`database/common`)
Interfaz abstracta que define el vocabulario común para cualquier persistencia estructurada.
- **Capacidades:** `connectivity`, `read`, `write`, `observability`.
- **Esquemas:** `DbCursor`, `DbWriteResult`, `DbQueryInput`.

## 2. SQL (`database/sql`)
Especialización para bases de datos relacionales.
- **Capacidades:** `dialect`, `ddl`, `transactions`, `migrations`, `pooling`.
- **Esquema:** `SqlTransactionId`.

## 3. MongoDB (`database/mongodb`)
Catálogo canónico para persistencia documental MongoDB-like.
- [Ver especificación completa](./mongodb.md)
- **Capacidades:** `read`, `write`, `aggregation`, `transactions`, `change_streams`, `search`, `vector_search`, `topology_discovery`.
- **Tiers:** `core`, `search`, `platform`.
