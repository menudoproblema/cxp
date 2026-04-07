# Catálogo de Cache (Key-Value)

## Interfaz Base
- **Nombre:** `cache/key-value`
- **Descripción:** Catálogo fidedigno para proveedores de caché en memoria (Redis, Memcached).
- **Esquema de Resultado:** `CacheValue` (incluye soporte para comprobar si la clave existe y su TTL).

### Capacidades
1. **`read_write`**: (Requerida en `core`) Operaciones atómicas de GET, SET y DELETE.
2. **`expiration`**: Soporte para establecer tiempos de vida (Time-To-Live) en las claves.
3. **`counters`**: Incrementos y decrementos atómicos rápidos, ideales para *Rate Limiting*.

### Tiers
- **`core`**: Almacén clave-valor estándar.
- **`ephemeral`**: Almacén con soporte de expiración automática de datos.

### Telemetría
Emite métricas de operaciones totales etiquetadas por `cache.hit` para calcular el *hit ratio* de forma unificada en el orquestador.
