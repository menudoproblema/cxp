# Catálogo de Runtime (Environment)

## Interfaz Base
- **Nombre:** `runtime/environment`
- **Descripción:** Catálogo para la observación y configuración del entorno de ejecución (ej. Pod de Kubernetes, Lambda, VM).

### Esquemas de Resultado
- `SecretValue`: Valor desencriptado y versionado.
- `ResourceReport`: Métricas puntuales de CPU y Memoria.

### Capacidades
1. **`configuration`**: (Requerida en `core`) Acceso a variables de entorno o mapas de configuración estructurados.
2. **`secrets`**: Extracción segura de credenciales (Vault, AWS Secrets Manager).
3. **`resources`**: Monitorización de cuotas y consumo de CPU/Memoria del propio runtime.

### Tiers
- **`core`**: Entorno básico observable.
- **`secure`**: Entorno con inyección de secretos.
- **`managed`**: Entorno completamente gestionado con monitorización de recursos disponible.
