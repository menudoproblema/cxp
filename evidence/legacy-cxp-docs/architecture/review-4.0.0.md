# Cierre de la revisión de 4.0.0rc1

La revisión aportada por el mantenedor se ha contrastado con código, pruebas
y empaquetado. El resultado es la versión `4.0.0`. Su cierre técnico exige
los informes de la versión exacta y se distingue de la autorización posterior
del mantenedor para crear el commit, etiquetar y publicar en PyPI.

## Hallazgos principales

| Hallazgo | Resolución y comprobación |
| --- | --- |
| Sdist no reproducible | Normalización explícita de tar y gzip, conservando el contenido. Cada construcción ejecuta dos builds y exige hashes idénticos. Tests alteran orden, fechas, propietarios y nombre gzip en archivos temporales. |
| Dependencias obligatorias | `cxp` base solo requiere msgspec. `cxp[exchange]` declara jsonschema, referencing y rfc8785; el paquete raíz no los importa. Cada instalación de la matriz prueba primero la base sin extras y después el intercambio. |
| Validación completa en rutas calientes | Caché privada por instancia solo para árboles realmente inmutables de tipos propios. Listas anidadas y subclases externas no se memorizan. Tests comprueban llamadas, mutaciones, reemplazos y wire idéntico. |
| Vectores incompletos | La suite portable incorpora negociación, selección de versión, acuerdos parciales/rechazados, límites exclusivos, origen negativo y paso negativo inválido. Ya existía un vector de máximo exclusivo: esa parte del informe era demasiado amplia. |
| Diagnósticos genéricos | Códigos específicos y rutas al campo en requisitos, sin relajar el JSON Schema. También se comprueban ramas anidadas. |
| Enteros con códigos distintos | Se comprueba el rango entero antes de convertir a float. Misma pareja código/ruta para bytes y diccionarios, incluidos valores negativos y números no representables exactamente como binary64. |
| Formateo fuera de gates | Legado normalizado mecánicamente, sin exclusiones globales. Pre-commit ejecuta lint y formato sobre todo el árbol; el gate principal no duplica lint. |

La reproducción de rendimiento sobre Playwright con matrices y snapshots vacíos
dio aproximadamente 1,2 y 1,9 microsegundos por llamada en el entorno local;
validar explícitamente la definición sin caché costó unos 51 microsegundos.
Son una sonda de este entorno, no un SLA ni una comparación controlada con los
tiempos del informe. La garantía automatizada es que no se vuelve a recorrer
una definición inmutable en cada validación.

## Observaciones menores

- El acuerdo comprueba `document.spec_version`; no asume siempre la versión 1.
- Se precisa que `contains_all` sobre null no se satisface, incluso con conjunto
  requerido vacío. La propiedad ausente continúa siendo indeterminada.
- Se documentan segundos enteros de `max_age_seconds`, conservación de
  microsegundos e inclusividad del límite.
- No se amplían unidades ni se publican endpoints de esquemas: cm/m se pueden
  convertir exactamente antes de emitir v1; los URN identifican esquemas locales
  y no requieren resolución por red.

## Evidencia y frontera de publicación

La suite portable contiene 61 casos entre documentos, evaluación, rechazos,
canonicalización, negociación y acuerdos. Los tests Python complementan esos
vectores; no son una acreditación universal de conformidad.

Los resultados de construcción y la matriz Python/msgspec se registran en
`dist/4.0.0/`. `scripts/release_evidence.py` exige la fuente exacta, hashes,
doble construcción y pruebas completas de wheel y sdist, incluyendo instalación
base sin dependencias del intercambio. Los informes rc1 anteriores quedan
conservados, pero no acreditan esta versión.

El informe recibido comunica pruebas en consumidores externos. No se presentan
como ejecuciones de esta revisión ni sustituyen la coordinación de rangos de
dependencias e integración con sus owners. No se han modificado consumidores.
La orden posterior autoriza publicar 4.0.0 en PyPI. Esa ejecución conserva su
propia evidencia de artefactos e instalación desde el índice, conforme al
[procedimiento de publicación](../release.md). No se atribuyen a esta revisión
histórica las comprobaciones adicionales realizadas al publicar.
