# Catálogo de Storage (Blob)

## Interfaz Base
- **Nombre:** `storage/blob`
- **Descripción:** Almacenamiento de objetos S3-compatible (S3, GCS, Azure Blob).

### Esquemas de Resultado
- `BlobMetadata`: Metadatos del objeto (tamaño en bytes, content_type).
- `PresignedUrl`: URLs efímeras con firma temporal para delegación de subidas/bajadas.
- `ResourceList`: Para paginación de objetos.

### Capacidades
1. **`object_management`**: (Requerida en `core`) Subir, borrar y leer metadata de archivos.
2. **`object_listing`**: Listar o iterar objetos con un prefijo.
3. **`presigned_urls`**: Generación de delegaciones criptográficas al cliente.
4. **`versioning`**: Soporte para buckets con múltiples versiones del mismo objeto.

### Tiers
- **`core`**: Almacenamiento base sin capacidades de listado o URLs efímeras.
- **`explorer`**: Soporta `object_listing`.
- **`secure-access`**: Soporta delegación vía `presigned_urls`.
