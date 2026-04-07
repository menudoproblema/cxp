# Catálogo de Video Streaming

## Interfaz Base
- **Nombre:** `media/video-streaming`
- **Satisfacciones:** `execution/plan-run` (para monitorización asíncrona de transcodificación).
- **Descripción:** Entrega de vídeo bajo demanda (VOD), empaquetado adaptativo (ABR) y pipelines de transcodificación.

### Esquemas de Resultado
- `MediaManifest`: Valida formato, duración, bitrates y si el vídeo está cifrado.
- `TranscodingJob`: Resultado compatible con la capa de ejecución (hereda de `AsyncWorkReport`).

### Capacidades
1. **`adaptive_streaming`**: (Requerida en `core`) Entrega de contenido ABR mediante manifiestos HLS o DASH.
2. **`transcoding`**: Transcodificación de vídeo raw en perfiles de calidad (renditions).
3. **`drm_protection`**: Protección de contenido (Widevine, PlayReady).
4. **`live_ingest`**: Soporte para directos.

### Tiers
- **`core`**: Proveedor estándar de entrega VOD.
- **`transcoder`**: Proveedor con capacidad de procesar e ingerir vídeo.

### Telemetría
Emite métricas de QoE (Quality of Experience) unificadas:
- `media.playback.bitrate` (bps)
- `media.playback.buffering_seconds` (s)
