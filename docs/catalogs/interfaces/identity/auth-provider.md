# Catálogo de Identidad (Auth Provider)

## Interfaz Base
- **Nombre:** `identity/auth-provider`
- **Descripción:** Catálogo para proveedores de validación de identidad y control de acceso (IAM, Auth0, Keycloak).

### Esquemas de Resultado
- `AuthClaims`: Claims unificados extraídos del token (JWT).
- `UserProfile`: Perfil completo resuelto a partir de una identidad.

### Capacidades
1. **`token_introspection`**: (Requerida en `core`) Validación offline u online de tokens de seguridad y extracción de *claims*.
2. **`user_info`**: Resolución de identidades a perfiles ricos de usuario.
3. **`policy_enforcement`**: Evaluación de reglas de acceso (RBAC o ABAC) antes de permitir la ejecución.

### Tiers
- **`core`**: Validador básico de tokens.
- **`full-iam`**: Sistema completo con gestión de políticas y resolución de perfiles.
