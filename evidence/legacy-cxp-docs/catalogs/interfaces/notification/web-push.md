# Catálogo de Notificaciones Push (WebPush)

## Interfaz Base
- **Nombre:** `notification/common`
- **Descripción:** Base abstracta para todos los proveedores de notificaciones (WebPush, FCM, APNs, Email, SMS).
- **Esquema de Resultado:** `PushResult`

## Especialización WebPush
- **Nombre:** `notification/web-push`
- **Satisfacciones:** `notification/common`
- **Descripción:** Especialización para el estándar W3C Web Push, exigiendo configuración criptográfica VAPID.

### Capacidades
1. **`vapid_configuration`**: (Requerida en `core`) Permite al orquestador validar si las claves públicas y subjects están correctamente configurados (VapidMetadata).
2. **`delivery`**: (Requerida en `core`) Envío de notificaciones al endpoint del navegador. Emite la métrica `push.web.sent`.

### Tiers
- **`core`**: Proveedor WebPush estándar y fidedigno, con VAPID y soporte para delivery unificado.
