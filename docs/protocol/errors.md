# Errores Estructurados en CXP (`CxpError`)

`CxpError` es un esquema compartido de la capa semántica opcional de CXP. Sirve para que catálogos y resultados enriquecidos expresen fallos legibles por máquina sin ampliar el núcleo del protocolo.

## Estructura del Error
Cuando una interfaz o un resultado enriquecido necesita publicar un error estructurado, puede usar el siguiente esquema:

```python
class CxpError(msgspec.Struct, frozen=True):
    code: str           # Código máquina (ej. "AUTH_EXPIRED")
    message: str        # Descripción humana
    retryable: bool     # Indicación de si un reintento es útil
    details: dict       # Datos extra (ej. stack trace, códigos de hardware)
```

## Ventajas de la Fidelidad de Error

1. **Reintentos Inteligentes**: Si un trabajo de impresión falla con `retryable: True` y el código `PAPER_JAM`, el orquestador puede esperar a que la impresora esté lista y reintentar automáticamente.
2. **Gobernanza Offline**: En notificaciones Push, un error con código `TOKEN_EXPIRED` indica al backend que debe borrar ese token de la base de datos inmediatamente.
3. **Análisis Agregado**: El orquestador puede generar informes sobre qué proveedores fallan más y por qué códigos específicos, facilitando el mantenimiento preventivo.

## Ejemplos de Códigos Estándar

| Dominio | Código | retryable | Significado |
| :--- | :--- | :--- | :--- |
| **Database** | `CONNECTION_LOST` | `True` | Fallo temporal de red. |
| **Identity** | `INSUFFICIENT_SCOPES` | `False` | El token es válido pero no tiene permisos. |
| **Printing** | `MEDIA_MISMATCH` | `False` | El papel cargado no coincide con el diseño. |
| **Storage** | `QUOTA_EXCEEDED` | `False` | El bucket está lleno. |

## Uso en Operaciones Asíncronas
Cualquier interfaz que devuelva un `AsyncWorkReport` (como `RunResult`, `TaskStatus` o `PrintJobStatus`) incluirá este objeto en su campo `error` cuando el estado sea `failure`.
