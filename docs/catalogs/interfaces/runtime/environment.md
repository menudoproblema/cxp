# Catálogo de Runtime (Environment)

## Interfaz Base
- **Nombre:** `runtime/environment`
- **Descripción:** Catálogo para la observación y configuración del entorno de ejecución (ej. Pod de Kubernetes, Lambda, VM).

### Esquemas de Resultado
- `SecretValue`: Valor desencriptado y versionado.
- `ResourceReport`: Métricas puntuales de CPU y Memoria.
- `RuntimeHealthReport`: Estado de readiness del runtime.
- `ActionResult`: Confirmación mínima para operaciones de control.

### Capacidades
1. **`configuration`**: (Requerida en `core`) Acceso a variables de entorno o mapas de configuración estructurados.
2. **`secrets`**: Extracción segura de credenciales (Vault, AWS Secrets Manager).
3. **`resources`**: Monitorización de cuotas y consumo de CPU/Memoria del propio runtime.
4. **`health`**: Inspección explícita de readiness mediante `runtime.health_check`.
5. **`lifecycle`**: Control de recarga gestionada mediante `runtime.reload`.

### Tiers
- **`core`**: Entorno básico observable.
- **`managed`**: Entorno con readiness checks y control de recarga.
