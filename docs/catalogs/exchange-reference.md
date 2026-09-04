# Catálogos del intercambio v1

Son recursos JSON con owner `CXP maintainers` y namespace `org.cxp`. Cada
recurso tiene versión contractual propia. Comparten distribución con CXP, no ciclo de publicación
independiente. Cambiar un catálogo no cambia automáticamente la especificación.
Cada referencia fija además el SHA-256: una misma identidad/version no debe
reutilizarse para publicar otro contrato.

| Catálogo | Representa | No representa |
| --- | --- | --- |
| `software-service` | Límites, formatos y región de un servicio genérico. | Un driver industrial. |
| `physical-printing` | Superficie imprimible, material y tintas de una configuración. | RIP, trabajos, reserva o posición geométrica. |
| `document-processing` | Formatos, transparencia, tintas planas y contrato de análisis. | Ejecución del análisis PDF. |
| `job-submission` | Envío y observación de trabajos como operaciones distintas. | Cola, persistencia, reintentos o producción ejecutada. |
| `finishing` | Plegado y encuadernación con definiciones diferentes. | Una capacidad de impresión heredada. |

`physical-printing` conserva 1.0.0 como versión predeterminada y añade 1.1.0
para adopción explícita. La nueva versión mantiene sus cinco propiedades y suma:

- `max_loaded_mass`: masa total cargada en la configuración;
- `max_object_width` y `max_object_length`: límites de un objeto o montaje;
- `print_mode_id`: identificador local estable del modo configurado;
- `resolution_x` y `resolution_y`: el par de resolución seleccionado.

`max_width` y `max_height` continúan siendo el área imprimible X/Y;
`max_thickness` es el límite Z. Estas propiedades no describen colocación,
colisiones, un útil, un modo certificado por el fabricante ni combinaciones
posibles entre máximos de configuraciones diferentes.

Las propiedades de `finishing.folding` son patrones, número de pliegues y tamaño
de hoja. Las de `finishing.binding` son espesor del bloque, longitud de lomo y
métodos. Sus esquemas JSON son tipos documentales separados; no se reutiliza una
metadata genérica que fuerce a una encuadernadora a fingir que imprime.

Los catálogos expresan afirmaciones de una configuración, no máximos agregados de
configuraciones mutuamente excluyentes. No hay uniones automáticas de snapshots,
prioridad por clase de evidencia ni herencia implícita de operaciones. Para una
declaración conjunta personalizada se publica un catálogo propio, revisado y
versionado; para procesos distintos se conservan evaluaciones separadas.

Los ejemplos son mínimos: no certifican plausibilidad física ni el vocabulario
de cada fabricante. Validar valores físicos, combinaciones de materiales y
evidencias sigue correspondiendo al productor del snapshot y al consumidor.

## Operaciones y resultados

Los seis contratos `org.cxp:<nombre>:1` viven en `schemas/operations-v1.json`:

- `submission-request`: ID de solicitud y referencia opaca del documento;
  clave de idempotencia opcional que no crea por sí sola una garantía.
- `submission-receipt`: `accepted` requiere ID de trabajo; `rejected` requiere
  motivo y no admite ID de trabajo; `unknown` exige motivo y permite un ID si
  llegó a conocerse. Ninguno demuestra impresión física.
- `job-query`: ID de trabajo para consultar.
- `job-observation`: resultado `pending`, `succeeded`, `failed`, `cancelled`
  o `unknown`, instante, procedencia y alcance `submission`, `processing` o
  `physical_production`. Una afirmación de éxito físico exige referencia de
  evidencia; CXP no consulta ni autentica esa evidencia. Fallo/desconocimiento
  requieren motivo.
- `document-request`: solicitud de procesamiento de una referencia documental.
- `document-result`: éxito con referencia de salida, fallo o desconocimiento
  con motivo. La salida de un análisis puede ser un informe, no otro PDF.

`operation_schema(tipo)` entrega el esquema; `validate_operation_payload`
valida y devuelve una copia. Son payloads de operaciones, no nuevas envolventes
del protocolo. Sus identificadores no se resuelven a imports ni URLs.

`submit` es `not_idempotent`; las observaciones y el análisis descriptivo son
`guaranteed`. Si una implementación de análisis tiene efectos repetibles no
idempotentes, debe publicar otra garantía, no adoptar este contrato sin revisión.
Una garantía condicionada exige clave, alcance y duración. CXP solo las describe.

`legacy_idempotency(False)` produce `unknown`: no puede distinguir omisión de
declaración explícita. La revisión del envío industrial sí declara no
idempotencia. `retryable=True` nunca equivale a permiso de repetición.

## Correspondencia con 3.1

`printing/manager`, `printing/label` y `printing/production` se conservan. Sus
nombres de operación, DTOs y metadata no se convierten automáticamente a estos
catálogos. La descripción física se aproxima a `physical-printing`, el envío a
`job-submission` y el acabado a `finishing`, pero la correspondencia es
conceptual, no un adaptador sin pérdida.

Los floats heredados no acreditan precisión decimal original. Tampoco un
`AsyncWorkReport` acredita éxito físico ni un catálogo de impresora prueba la
capacidad de su RIP. La migración requiere publicar explícitamente datos,
configuración, procedencia y referencias versionadas.
