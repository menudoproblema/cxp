# Catálogo de Notificaciones Push Móviles

## Interfaz Base
- **Nombre:** `notification/mobile-push`
- **Satisfacciones:** `notification/common`
- **Descripción:** Catálogo fidedigno para el envío de notificaciones a dispositivos Android e iOS.

### Capacidades
1. **`fcm_protocol`**: Envío mediante Google Firebase. Requiere `FcmMetadata` (Project ID).
2. **`apns_protocol`**: Envío mediante Apple Push (HTTP/2). Requiere `ApnsMetadata` (Team ID, Key ID, Bundle ID).
3. **`topic_management`**: Gestión de suscripción a canales o tópicos de interés desde el servidor.

### Tiers
- **`cross-platform`**: (Recomendado) Asegura que el proveedor puede alcanzar tanto el ecosistema Google como Apple de forma fidedigna.

### Fidelidad de Token
La operación `notification.send` devuelve un `PushResult`. Si el dispositivo ha desinstalado la app o el token ha expirado, el flag `is_expired` será `True`, permitiendo la limpieza automática de la base de datos de dispositivos.
