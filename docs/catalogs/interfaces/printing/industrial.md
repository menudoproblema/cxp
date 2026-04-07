# Catálogos de Impresión Industrial

El dominio de impresión física se estructura en tres capas, desde el servidor genérico hasta acabados complejos.

## 1. Interfaz Base (`printing/manager`)
Abstracta. Define el ciclo de vida de un trabajo físico (encolado, impresión, error) usando el esquema `PrintJobStatus` (compatible con ejecución asíncrona) y monitorización de hardware (`PrinterStatus`).

## 2. Impresión de Etiquetas (`printing/label`)
Especializada en lenguajes industriales como ZPL o TSPL (ej. Zebra, TSC).
- **`zpl_language`**: Soporte nativo ZPL.
- **`media_validation`**: Permite al orquestador verificar si la impresora tiene el papel con las dimensiones (`LabelMetadata`) y sensores correctos antes de imprimir.

## 3. Impresión de Producción (`printing/production`)
Especializada en volumen y acabado físico (ej. Konica Minolta).
- **`folding`**: Plegador (tríptico, z-fold).
- **`gluing`**: Encolador (encuadernación).
- **`color_calibration`**: Calibración exacta de color.

### Tiers
Cada subfamilia exige un Tier (ej. `industrial` para Zebra, `finisher` para Konica) para asegurar que el hardware orquestado es fidedigno y compatible.
