# Plan de cierre de la siguiente versión de CXP

## Estado y alcance del documento

- Estado: alcance implementado; acreditación técnica vinculada a los gates y
  artefactos de la candidata exacta. Publicación en PyPI autorizada después
  del cierre técnico; su ejecución se registra por separado.
- Fecha de revisión: 2026-09-03.
- Versión de partida: CXP 3.1.0.
- Base inspeccionada: `6b5b555cbaf39c89cbe1ae0ca5955a88b049f8cf`.
- Objetivo: CXP 4.0.0, revisada a partir de la candidata local 4.0.0rc1.
- Propietario de este plan: CXP.

Este documento conserva el alcance y los criterios de cierre del trabajo
autorizado por el mantenedor. La autorización inicial de implementación no incluía
publicar, crear tags, hacer commits ni modificar consumidores. Una orden posterior
autoriza preparar el commit, etiquetar `v4.0.0` y publicar en PyPI; el push de Git
queda en manos del mantenedor y no se modifican consumidores. La especificación
del contrato nuevo vive en [intercambio documental v1](../protocol/exchange-v1.md).
Las secciones de recomendaciones siguientes conservan la base de diseño; la
especificación concreta las reglas necesarias para implementar y probar.

### Independencia del proyecto

CXP es un proyecto autónomo e independiente de gdynamics. Esta frontera está
confirmada; el mantenedor autorizó implementar este plan. Tener consumidores
en ese ecosistema no le transfiere la
autoridad sobre CXP ni obliga a adoptar su infraestructura de desarrollo.

No se incorporará `_standards`, no se registrará CXP en la gobernanza RFC
compartida y no se condicionará este plan a sus prefijos, catálogos o gates.
La exigencia de esa alta en la revisión anterior queda retirada.

La especificación, los esquemas, los vectores de conformidad, las decisiones
de diseño y las instrucciones de contribución tendrán su fuente en CXP.
Su aprobación corresponderá a quienes mantengan CXP. Si resulta
útil utilizar RFCs o ADRs, serán documentos locales con un proceso propio,
sin exigir ahora otra infraestructura de gobernanza.

Las validaciones necesarias deberán poder ejecutarse desde un clon de CXP con
sus dependencias de desarrollo, sin clonar repositorios de gdynamics ni acceder
a servicios internos. Se conservan las herramientas generales y los estándares
abiertos que aporten valor. Las pruebas de integración específicas de
cada consumidor pertenecen a ese consumidor.

## Resultado que queremos entregar

Una versión de CXP que permita intercambiar y evaluar declaraciones de
capacidades sin depender de Python, con validación consistente, contexto
explícito, resultados reproducibles y una transición documentada desde 3.1.

La versión estará cerrada técnicamente cuando cumpla todos sus criterios de
aceptación y pueda instalarse como artefacto construido. La publicación será
una decisión posterior y separada. Pasar pruebas locales no acredita ninguna
de esas dos condiciones por sí solo.

### Dentro

- Contrato documental nuevo: semántica, JSON Schema y vectores de conformidad.
- Validación estructural y semántica consistente, con diagnósticos completos.
- Snapshots aislados de mutaciones externas y contexto de evaluación explícito.
- Requisitos sobre soporte efectivo, valores, conjuntos y rangos.
- Registros aislables y referencias versionadas a catálogos.
- Magnitudes contractuales con representación exacta y unidades definidas.
- Catálogos nuevos mínimos para describir impresión y acabado por separado.
- Garantías descriptivas de operaciones y tratamiento prudente de reintentos.
- Compatibilidad, empaquetado, documentación y criterios de publicación.

### Fuera

- Maquinaria concreta, drivers, descubrimiento de dispositivos y conexiones.
- Ejecución de trabajos, colas, persistencia, reservas y reintentos automáticos.
- Geometría, análisis PDF, composición y recetas de producción.
- Cambios de código o dependencias de aplicaciones consumidoras.
- Migración completa de todos los catálogos al contrato nuevo.
- Creación de un lenguaje de programación o un solucionador universal.
- Separación inmediata en varias distribuciones Python.
- Nuevos SDKs completos, firmas digitales y certificaciones de conformidad.
- Cambios de licencia o de Python mínimo como efecto lateral de esta versión.
- Incorporación de `_standards` o de la gobernanza compartida de gdynamics.

## Nueva revisión: conclusiones y correcciones

Las revisiones recibidas refuerzan el diagnóstico anterior. Se incorporan
versionado documental, distinción de idempotencia no declarada y vectores
portables. Se corrigen las siguientes afirmaciones antes de planificar:

1. Un conjunto finito de fixtures no demuestra conformidad al 100 %. La
   especificación define el significado; los fixtures comprueban ejemplos y
   fronteras. Una contradicción entre ambos bloquea el cierre.
2. Añadir una propiedad de versión a la forma heredada no protege frente al
   lector 3.1: puede ignorarla. Una envolvente distinta tampoco hace fallar a
   todos los decoders antiguos; `CapabilityMatrix` puede aceptarla como una
   matriz vacía porque sus campos tienen valores por defecto.
3. Una extensión crítica desconocida no es una capacidad incompatible ni un
   simple dato ausente. La recomendación es rechazar el documento para
   evaluación, sin ejecutar parcialmente sus requisitos.
4. `null` no significa universalmente "no soportado". Esa interpretación no
   se deduce de JSON y debe pertenecer al contrato de cada propiedad.
5. `idempotent=False` es prudente para `print.submit`. No se cambia a `True`.
   El contrato nuevo distinguirá garantía no declarada de no idempotencia.
6. La reproducibilidad exige fijar las entradas, pero no obliga por sí sola
   a utilizar JCS. La recomendación de usar JCS y SHA-256 es una elección
   explícita para identificar contenido, no un requisito impuesto por JSON.
7. No encontrar un consumidor que compruebe una excepción de construcción no
   demuestra que nadie dependa de ella. Se conserva esa superficie heredada
   salvo una ruptura explícitamente documentada.
8. Versionar catálogos no equivale a publicarlos independientemente. En esta
   versión se conserva una distribución; se acepta y documenta ese acoplamiento
   de empaquetado, sin confundirlo con la versión de la especificación.

### Comprobaciones realizadas en esta revisión

Sobre la base indicada y `msgspec 0.20.0`, se ha comprobado en memoria:

- El lector heredado de requisitos ignora campos adicionales de versión y
  extensiones críticas, aun cuando tienen significado obligatorio para el
  emisor.
- Añadir `schema` a la raíz heredada de un snapshot no provoca su rechazo.
- Una envolvente distinta es rechazada por el decoder de snapshots al faltar
  `component_name` en su raíz, pero aceptada por el de `CapabilityMatrix`
  como matriz vacía. No existe una garantía general de rechazo retrospectivo.
- Un campo `Decimal` acepta un número JSON incluso con `strict=True`; una
  anotación Python no impone por sí sola "cadena decimal en el intercambio".
- Omitir `CatalogOperation.idempotent` y asignarle `False` producen actualmente
  el mismo valor.

Baseline local vigente: `pytest -q tests` pasa 192 pruebas; `ruff check .`
pasa; `mypy src` pasa sobre 66 archivos. Son controles del sistema existente,
no pruebas de la funcionalidad propuesta. No se ha ejecutado aquí toda la
matriz de CI ni una migración de consumidores.

## Decisiones recomendadas para congelar el alcance

Estas decisiones se adoptan para la implementación autorizada. La redacción
de propuesta conserva su contexto histórico; los detalles definitivos están
en la especificación de intercambio v1 y la guía de migración. Esa autoridad
no se delega en los tests ni en el resultado de una ejecución.

### Versión y compatibilidad

Se propone planificar el conjunto como **4.0.0**, porque se revisan contratos
de validación y publicación de catálogos que no deben prometerse compatibles
sin evidencia. No es una autorización para retirar APIs innecesariamente.

Se mantendrían Python >=3.12, `msgspec`, la licencia vigente, los imports
heredados principales y las fachadas `get_catalog` y `register_catalog`.
El handshake v1 y los perfiles heredados conservarían su significado.

El contrato documental enriquecido usaría una familia y una versión propias.
No se deduce su versión del número del paquete. Para integraciones vivas,
se propone una negociación optativa de protocolo v2 que autorice el intercambio
nuevo, manteniendo v1 para el heredado y sin downgrade automático de requisitos.

Los lectores y exportadores nuevos serán explícitos; no habrá autodetección
permisiva que desemboque en un parser 3.1. Los documentos offline llevarán una
envolvente distinta y se abrirán mediante el lector de esa familia, que
comprobará tipo y versión antes de interpretar su contenido. La entrega 0
fijará la envolvente y el anuncio de familias/versiones admitidas en vivo.

No se introducirán valores falsos de soporte para forzar errores en clientes
antiguos. Tampoco se afirmará que el software antiguo puede comprender o
rechazar de forma segura cualquier documento nuevo. Los límites de esa
garantía forman parte de la guía de migración.

### Autoridad, nombres y extensiones

- La especificación semántica gobierna la interpretación.
- JSON Schema 2020-12 gobierna la forma del intercambio nuevo.
- La suite portable contrasta implementaciones con esos contratos.
- Python es una implementación, no la única fuente de verdad.
- El intercambio nuevo utiliza `snake_case`; no admite aliases camelCase
  implícitos. Las proyecciones externas heredadas no se renombran desde CXP.
- Los catálogos de terceros usan identificadores con espacio de nombres;
  identidad y versión son componentes explícitos, no strings ambiguos que
  cada consumidor deba partir de manera diferente.
- Las referencias se resuelven contra registros suministrados al proceso;
  un identificador URI no autoriza consultas de red ni imports de código.
- La zona de extensiones es explícita. Las extensiones no críticas pueden
  preservarse sin interpretarse; las críticas desconocidas impiden evaluar.

El rechazo por formato inválido y el rechazo por contrato no soportado serán
categorías diferentes de diagnóstico. Ninguna produce un veredicto funcional.
La prohibición de evaluar una extensión crítica desconocida se aplica también
si aparece dentro de un requisito; no se promete un resultado parcial.

### Evaluación y ausencia de información

- `compatible`: se cumplen los requisitos según las entradas y política.
- `incompatible`: existe un incumplimiento demostrado.
- `indeterminate`: las entradas válidas y entendidas no permiten decidir.

Una propiedad ausente no demuestra que una capacidad sea inexistente.
`null` solo se admite cuando lo permite el esquema; su significado debe estar
definido allí y en la semántica de la propiedad. No se convierte en cero,
false, ilimitado ni no soportado mediante una regla global.

No se añade `unknown` al enum heredado. La ausencia de conocimiento se expresa
en el modelo nuevo sin alterar `accepted_noop`. Los requisitos nuevos exigen
soporte efectivo por defecto; una política explícita puede admitir noop para
casos donde tenga sentido. Los perfiles heredados conservan su política.

El vocabulario inicial se limita a igualdad, pertenencia, inclusión de un
conjunto requerido, rangos y composición lógica. No contiene expresiones
ejecutables ni un operador por cada nombre equivalente de los borradores.

La composición usa estas reglas:

| Combinación | Regla |
| --- | --- |
| Todas las condiciones | Un incumplimiento demostrado basta para incompatibilidad; si no hay incumplimientos pero falta información, el resultado es indeterminado. |
| Alguna condición | Una condición satisfecha basta; si ninguna se satisface y queda información desconocida, el resultado es indeterminado. |
| Lista de condiciones vacía | Se rechaza como requisito mal formado, sin asumir una verdad vacía. |

La entrega 0 fijará límites inclusivos/exclusivos, origen e incremento de los
rangos discretos, tipos comparables y rutas de propiedades. No se inicia el
evaluador mientras estas reglas sigan abiertas. La política de autorizar una
acción queda fuera: no se transforma incertidumbre en incompatibilidad para
simular un rechazo operativo.

### Contexto, evidencia e inmutabilidad

Los documentos nuevos separan proveedor, sujeto de la declaración, referencia
del catálogo, revisión de configuración, observación y procedencia. Soporte,
disponibilidad, conectividad y consumibles no se reducen a un solo enum.

La fuente de una afirmación no determina automáticamente su veracidad. Una
observación en vivo y una prueba empírica pueden acreditar hechos distintos.
No se fusionan declaraciones contradictorias tomando máximos ni haciendo la
unión de capacidades. La resolución debe ser explícita o quedar sin resolver.

La evaluación recibe un contexto temporal explícito cuando necesita comprobar
vigencia. No consulta el reloj, la red ni un registro mutable durante el
cálculo. Sus entradas normalizadas son propiedad del evaluador y no comparten
diccionarios o listas mutables con el emisor. Una vista sobre un diccionario
que otro actor puede modificar no satisface esta garantía.

Se propone conservar referencias verificables al contenido exacto de catálogo,
snapshot, requisitos y contexto. Para esa identificación se recomienda
SHA-256 sobre JSON normalizado y canonicalizado con JCS; los metadatos de
huella se mantienen fuera del contenido que se hashea. Se documentará la
normalización previa y la versión semántica del evaluador. El hash identifica
contenido, no prueba autenticidad ni corrección física.

La entrega 0 fijará también los límites numéricos del JSON canonicalizable,
incluidas las extensiones preservadas. No se admitirá una conversión con pérdida
para poder calcular la huella; las magnitudes decimales seguirán siendo cadenas.

### Magnitudes e idempotencia

Las magnitudes contractuales nuevas usan cadena decimal y unidad explícita.
Los números JSON en esos campos se rechazan antes de la conversión a Decimal.
Se define una gramática decimal, longitudes máximas y normalización; no se
aceptan NaN, infinitos ni redondeos silenciosos.

El conjunto inicial de unidades se limita a longitud (`um`, `mm`, `in`, `pt`),
masa (`g`, `kg`), resolución (`dpi`) y ángulo (`deg`). Las conversiones dentro
de cada dimensión se definen mediante relaciones exactas, incluido el punto
de 1/72 de pulgada. Una conversión no representable como decimal finito no se
redondea para decidir un requisito: la comparación debe preservar el valor
exacto o rechazar la conversión según el contrato. Esto no crea un motor de
geometría ni obliga a sustituir floats de telemetría.

En operaciones nuevas se distinguirán tres declaraciones: garantía de
idempotencia, no idempotencia y garantía desconocida/no declarada. Si una
garantía depende de clave de deduplicación, alcance o duración, esas condiciones
deben ser explícitas; no se promete idempotencia incondicional.

La conversión desde un `False` heredado no puede recuperar si fue omitido o
explícito. Se proyectará conservadoramente como garantía desconocida, salvo
que una definición revisada de catálogo declare no idempotencia. `print.submit`
sin garantía de deduplicación se declarará no idempotente. `retryable=True`
seguirá sin autorizar repetir una operación.

### Distribución de catálogos

La 4.0 propuesta mantiene una distribución Python. Cada catálogo nuevo tiene
identidad, versión contractual y owner explícitos. Los cambios de un catálogo
de producto no obligan a cambiar la versión de la especificación genérica.

Se conserva el acoplamiento de releases del paquete y se documenta. Separar
distribuciones queda fuera de esta entrega; no se promete independencia de
publicación que todavía no existe. Los catálogos heredados y sus fachadas no
se eliminan para lograr una separación meramente nominal.

## Reducción de conceptos y aprovechamiento del sistema vigente

| Pieza | Garantía que protege y mecanismo vigente | Disposición propuesta | Garantía diferencial o motivo |
| --- | --- | --- | --- |
| Handshake v1 | Negociación mínima existente en `handshake.py`. | `reuse` | Se conserva; no puede acreditar comprensión del documento enriquecido. |
| Intercambio nuevo | Las formas heredadas descartan campos desconocidos. | `justify` | Familia documental y lector explícitos, con negociación de comprensión. |
| Especificación y esquemas | La autoridad actual reside principalmente en structs y validadores Python. | `justify` | Contrato interpretable sin importar Python. |
| `CapabilityMatrix` | Proyección de presencia existente. | `reuse` | Útil para su alcance original; no sustituye descriptores ricos. |
| `accepted_noop` | Semántica vigente y probada. | `reuse` | Se conserva y se exige soporte efectivo mediante política explícita nueva. |
| Validación de metadatos | Conversión y booleano que pierden parte del diagnóstico. | `consolidate` | Un resultado detallado alimenta las fachadas booleanas sin duplicar reglas. |
| Registro por defecto | `get_catalog`, `register_catalog` y carga heredada por imports. | `reuse` | Preserva entrypoints; el evaluador nuevo usa un registro aislado. |
| Perfil ligado al registro global | `CapabilityProfile.__post_init__` consulta el registro. | `derive` | Documento nuevo desacoplado y resolución explícita; fachada heredada conservada. |
| Snapshot validado | Struct congelado con metadata potencialmente mutable. | `justify` | Copia normalizada independiente y entradas fijadas para evaluación. |
| Operadores duplicados o código embebido | Los borradores multiplican nombres para la misma comprobación. | `remove` | Un vocabulario pequeño protege las mismas garantías sin un intérprete general. |
| Enum único de disponibilidad | No existe una semántica ortogonal en la propuesta de enum mixto. | `remove` | Separar dimensiones evita perder estados simultáneos. |
| Magnitudes exactas | Algunos DTOs actuales usan floats con unidad en el nombre. | `justify` | Representación nueva común y comparación exacta sin migrar todos los DTOs. |
| Identificación de entradas | Identidades actuales no fijan por sí solas el contenido evaluado. | `justify` | Referencias de contenido permiten comprobar qué se evaluó. |
| Catálogos de impresión | `printing/production` mezcla impresión y acabado. | `consolidate` | Contratos nuevos por responsabilidad, sin retirar todavía los antiguos. |
| Múltiples distribuciones | Un paquete actual alberga núcleo y catálogos. | `remove` | Se excluye de esta versión: no es necesario para evaluar capacidades. |
| Telemetría, proveedores sync/async | Superficies existentes reutilizables. | `reuse` | No requieren una refundación para entregar el contrato nuevo. |

## Fases de trabajo

Los entregables de implementación están materializados. Ninguna fase se
acredita por intención: el cierre técnico exige los gates de la candidata
exacta, registrados fuera del paquete para no crear evidencia autorreferencial.

| Fase | Entregables y comprobación |
| --- | --- |
| 0 | `docs/protocol/exchange-v1.md`, JSON Schema, inventario API/wire 3.1 y vectores portables con resultados esperados. |
| 1 | Diagnósticos compartidos, validación de metadatos y catálogos/bindings; `tests/test_validation_integrity.py`. |
| 2 | `cxp.exchange.documents`, `registry`, `quantities`, `negotiation`; pruebas de límites, mutaciones y rechazo. |
| 3 | Evaluador puro, contexto, rangos exactos y tablas trivaluadas; `tests/test_exchange.py` y vectores. |
| 4 | Cinco catálogos JSON, seis contratos de payloads de operaciones y ejemplos empaquetados; `docs/catalogs/exchange-reference.md`. |
| 5 | API/wire congelados, segundo motor de esquema, CI y gates propios, migración, changelog y verificación de wheel/sdist. |
| 6 técnica | Versión `4.0.0`, construcción reproducible y manifiesto de fuente/hashes, matriz completa y `dist/4.0.0/release-evidence.json` generado por los scripts. |
| Publicación | No autorizada ni ejecutada. Requiere revisión de consumidores y decisión humana sobre los artefactos exactos. |

La guía [de publicación](../release.md) y `CONTRIBUTING.md` documentan los
comandos. Un informe ausente o cuya huella no coincide no acredita el cierre.
No se han modificado consumidores ni incorporado infraestructura de gdynamics.

### Fase 0. Aceptar alcance y cerrar contrato

Objetivo: disponer de una especificación revisable antes de desarrollar.

Alcance mínimo:

- Formalizar el contrato en documentación propia de CXP y obtener aceptación
  del objetivo 4.0 mediante la revisión del propio proyecto.
- Inventariar la API pública, campos y errores cuyo comportamiento se conserva.
- Fijar campos, tipos y errores de documentos, requisitos, snapshots y resultados.
- Cerrar versión, negociación, nombres, extensiones, ausencia/null, idempotencia,
  aritmética, canonicalización y límites de recursos.
- Definir qué reglas viven en esquema y cuáles en validación semántica.
- Diseñar vectores positivos y negativos con resultado esperado y trazabilidad.

Criterio de cierre: contrato aprobado, sin decisiones materiales delegadas al
implementador; inventario explícito de rupturas y preservaciones; cada regla
con un criterio de aceptación y al menos un vector representativo. No se
declara cerrada esta fase con este plan narrativo.

### Fase 1. Diagnósticos e integridad

Objetivo: que la validación tenga un significado único y explicable.

Alcance mínimo:

- Empezar por el resultado detallado de validación de metadatos.
- Añadir detección de duplicados dentro del ámbito de identidad de capacidades,
  operaciones y definiciones. Compartir un nombre de operación entre capacidades
  distintas no constituye por sí solo un duplicado.
- Comprobar coherencia entre bindings, resultados y catálogo.
- Comprobar tiers, referencias y conflictos de contratos compuestos.
- Validar datos equivalentes de forma equivalente, con independencia de su
  representación admitida.
- Mantener fachadas booleanas y documentar cada endurecimiento observable.

Criterio de cierre: regresiones reproducidas se rechazan con códigos y rutas
estables; controles positivos siguen pasando; los catálogos incorporados
superan los controles aplicables sin exclusiones globales.

### Fase 2. Documentos, registros y snapshots

Objetivo: crear el recorrido estricto desde bytes hasta entradas evaluables.

Alcance mínimo:

- Publicar esquemas y exportadores del intercambio nuevo.
- Implementar lector explícito, extensión crítica y límites de recursos.
- Rechazar claves JSON duplicadas antes de que el parser las pierda.
- Resolver referencias sin red contra un registro aislado e inmutable durante
  la evaluación; mantener las fachadas globales heredadas.
- Normalizar magnitudes y separar copias de datos mutables del llamador.
- Implementar identificación de contenido y contexto explícito.
- Probar negociación nueva, rechazo y ausencia de downgrade silencioso.

Criterio de cierre: bytes inválidos o no soportados nunca llegan al evaluador;
dos registros independientes no interfieren; modificar datos fuente después
de validar no cambia las entradas fijadas ni sus referencias de contenido.

### Fase 3. Evaluador enriquecido

Objetivo: resolver requisitos conocidos con un resultado determinista.

Alcance mínimo:

- Soporte efectivo y política explícita para noop.
- Comparaciones, conjuntos, rangos y composición lógica del contrato aceptado.
- Magnitudes exactas, ausencia/null y vigencia con tiempo explícito.
- Resultados funcionales separados de rechazos de documento.
- Diagnósticos ordenados determinísticamente, con requisito y dato de origen.
- Sin ejecución de operaciones, consultas de red ni acceso a reloj implícito.

Criterio de cierre: todos los vectores aceptados se resuelven igual en runs
repetidos y en la matriz de Python; la evaluación no modifica sus entradas.
Un dato desconocido no se convierte en compatibilidad por un valor por defecto.

### Fase 4. Catálogos de referencia y contratos de operaciones

Objetivo: demostrar reutilización y cerrar el mínimo industrial dentro de CXP.

Alcance mínimo:

- Un catálogo genérico pequeño, no industrial, para evitar que el evaluador
  dependa de reglas específicas de impresión.
- Contratos mínimos distintos para descripción física, procesamiento documental,
  envío/seguimiento y acabado. No se presupone herencia de operaciones.
- Tipos de metadata separados para plegado y encuadernación.
- Declaraciones explícitas de idempotencia y límites de las confirmaciones.
- Separar solicitud aceptada, resultado informado y resultado desconocido;
  no equiparar un resultado asíncrono genérico con producción física confirmada.
- Ejemplos sin marcas ni equipos reales que acrediten restricciones conjuntas.
- Preservar catálogos heredados y publicar su correspondencia y límites.

Criterio de cierre: un consumidor de ejemplo únicamente con documentos puede
obtener los tres veredictos; un proceso de acabado no necesita fingir que
imprime; el ejemplo no depende de un driver, máquina ni otro proyecto.

### Fase 5. Compatibilidad, conformidad y artefactos

Objetivo: comprobar la versión que realmente se va a distribuir.

Alcance mínimo:

- Congelar vectores legacy con procedencia de versión y licencia conocidas.
- Matriz de lectores/emisores antiguos y nuevos, incluyendo el caso de parser
  legado permisivo; comprobar los adaptadores de selección de formato.
- Verificar imports, exports, registro por defecto, perfiles y errores heredados.
- Conservar y ampliar pytest, Ruff y mypy; ejecutar Python 3.12, 3.13 y 3.14.
- Fijar el mínimo real de `msgspec` y probarlo junto a la versión soportada
  actual; no depender accidentalmente de la instalada en el entorno local.
- Ejecutar fixtures JSON con un validador de esquema independiente y contrastar
  el resultado esperado de semántica con la implementación Python.
- Construir wheel y sdist, comprobarlos e instalarlos en entornos limpios.
- Verificar schemas, catálogos, ejemplos, datos y marcadores de tipado incluidos
  en los artefactos; probar sin editable installs ni rutas locales inyectadas.
- Ejecutar las validaciones locales y de CI sin repositorios hermanos ni
  servicios internos del ecosistema gdynamics.
- Actualizar documentación de integración, errores, migración y changelog.

Criterio de cierre: el artefacto candidato supera los gates desde una instalación
limpia; ninguna ruptura carece de explicación y migración; los riesgos de
consumidores conocidos tienen evidencia o una condición explícita que impida
publicar. No se afirma conformidad universal por pasar estos fixtures.

### Fase 6. Candidata y autorización de publicación

Objetivo: separar cierre técnico de distribución pública.

Alcance mínimo:

- Preparar una candidata identificada como `4.0.0rc1` cuando proceda, sin publicar
  ni crear un tag automáticamente.
- Auditar el diff final, licencias de artefactos, cambios incompatibles y gates.
- Registrar revisiones y hashes exactos de artefactos; cualquier cambio invalida
  la evidencia alcanzada y exige regenerar la candidata.
- Resolver fuera de este plan las dependencias de consumidores que no permitan
  o no controlen la actualización; no modificar sus repos desde esta tarea.
- Definir contingencia: conservar versiones anteriores, fijar versiones conocidas,
  no sobrescribir artefactos publicados ni interpretar documentos nuevos como
  antiguos durante una vuelta atrás.
- Pedir autorización explícita de publicación y del destino.

Criterio de cierre técnico: candidata íntegra, matriz verde y sin bloqueos
contractuales ni de compatibilidad. Criterio de publicación: autorización
humana sobre la candidata exacta. Criterio posterior: instalación y smoke
desde el artefacto publicado, sin asumir que el upload demuestra funcionamiento.

## Matriz mínima de aceptación

| Caso | Resultado esperado | Fase responsable |
| --- | --- | --- |
| Declaración válida y requisito satisfecho | Compatible con referencias de entradas. | 3 |
| Límite conocido incumplido | Incompatible con valor y requisito identificados. | 3 |
| Dato necesario no comunicado | Indeterminado, sin inventar un valor. | 3 |
| `null` prohibido por esquema | Rechazo estructural antes de evaluar. | 2 |
| `null` permitido | Interpretación exacta definida por esa propiedad, no regla global. | 3 |
| Extensión crítica desconocida en raíz o requisito | Documento no soportado; ninguna evaluación parcial. | 2 |
| Extensión no crítica desconocida | Conservada según contrato, sin aportar garantías funcionales. | 2 |
| Documento nuevo dirigido a integración legacy | Integración impide el envío/lectura incompatible; no confía en el decoder viejo. | 5 |
| Emisor exige contrato nuevo y receptor solo v1 | Negociación rechazada; sin pérdida silenciosa de restricciones. | 2 |
| Claves JSON o IDs contractuales duplicados | Rechazo explícito, no first-wins ni last-wins. | 1 y 2 |
| Struct y diccionario con contenido inválido equivalente | Mismo diagnóstico semántico al validar por la entrada admitida. | 1 |
| Mutación del diccionario original | No altera el snapshot normalizado ya aceptado. | 2 |
| Binding de operación contradictorio | Validación rechazada. | 1 |
| Registro aislado con referencia ausente o conflictiva | Error identificable sin consultar un registro global de respaldo. | 2 |
| `accepted_noop` con requisito de ejecución efectiva | Incompatible; política legacy no alterada. | 3 |
| Decimal enviado como número JSON | Rechazo en un campo contractual de cadena decimal. | 2 |
| Conversión no finita en decimal | No se redondea silenciosamente para decidir cumplimiento. | 3 |
| Condiciones conocidas junto a desconocidas | Resultado de las tablas de composición aceptadas. | 3 |
| Snapshot caducado para la política solicitada | No acredita vigencia; resultado y motivo definidos por la política. | 3 |
| Misma entrada, registro fijado y contexto | Mismo resultado semántico y mismos identificadores de contenido. | 3 |
| Garantía de idempotencia omitida | Desconocida, distinta de una no idempotencia declarada. | 4 |
| Error transitorio de operación no idempotente | No se recomienda repetición automática sin reconciliación. | 4 |
| Uso de APIs heredadas preservadas | Contrato publicado conservado según inventario de fase 0. | 5 |
| Instalación desde wheel/sdist | Mismos contratos y recursos que la fuente candidata. | 5 |

## Condiciones de publicación y dependencias externas

La implementación de este plan pertenece a CXP. Las comprobaciones de
compatibilidad no autorizan cambios en repositorios consumidores.

La publicación de una major requiere revisar consumidores conocidos que
fijan la familia anterior y consumidores que admiten cualquier major futura.
Se necesita evidencia sobre resolución de dependencias e integración, no solo
imports aislados. Los resultados detallados y remediaciones pertenecen a sus
owners; no se copian aquí como un registro paralelo de despliegue.

No se publica si ocurre cualquiera de estas condiciones:

- Falta aceptación del contrato, su autoridad o su versión objetivo.
- Un lector puede perder requisitos dentro de una integración declarada segura.
- Hay divergencia entre especificación, esquema, fixtures e implementación.
- Una ruptura no tiene política de migración explícita.
- La candidata cambió desde que se ejecutaron los gates.
- Los artefactos no contienen los recursos necesarios o dependen del checkout.
- Queda una dependencia externa necesaria sin resolver ni coordinar.
- No hay autorización explícita para publicar.

La evidencia debe distinguir siempre "implementado", "candidato comprobado",
"autorizado para publicar" y "publicado verificado". No se fusionan en un
único indicador de trabajo terminado.

## Orden y antipatrones

Secuencia principal: contrato → diagnósticos/integridad → documentos y registros
→ evaluación → catálogos → compatibilidad/artefactos → publicación autorizada.

Los fixtures de cada fase se construyen junto a su implementación; no se
posponen todas las pruebas a la fase 5. Tras congelar el contrato pueden avanzar
en paralelo la preparación documental y el arnés de conformidad, pero ninguna
fase posterior se da por cerrada sin sus dependencias.

Evitar:

- Publicar un núcleo con semántica todavía pendiente de decidir.
- Cambiar firmas o estados heredados simplemente para reutilizar clases.
- Llamar "compatible" a un requisito que el lector no comprendió.
- Deduplicar silenciosamente declaraciones contradictorias.
- Reemplazar tests negativos por exclusiones o cambios globales de lint.
- Tratar un hash como firma o como prueba de veracidad.
- Abrir catálogos de fabricantes antes de comprobar el modelo genérico.
- Declarar independencia de catálogos mientras comparten release de paquete.
- Confundir el plan o la candidata con permiso para publicar.

## Fuentes y trazabilidad

### Fuentes vigentes del repositorio

- [Arquitectura actual](../architecture.md).
- [Capacidades](../../src/cxp/capabilities.py).
- [Descriptores](../../src/cxp/descriptors.py).
- [Catálogos y perfiles](../../src/cxp/catalogs/base.py).
- [Handshake](../../src/cxp/handshake.py).
- [Integración](../../src/cxp/integration.py).
- [Resultados y errores](../../src/cxp/catalogs/results.py).
- [Catálogo actual de impresión](../../src/cxp/catalogs/interfaces/printing/family.py).
- [Catálogo actual de producción](../../src/cxp/catalogs/interfaces/printing/production.py).
- [Guía actual de errores](../protocol/errors.md).
- [Configuración del paquete](../../pyproject.toml).
- [CI actual](../../.github/workflows/ci.yml).

### Referencias externas

- [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html): relación entre
  compatibilidad de API y versiones; no decide por sí solo nuestro alcance.
- [JSON Schema 2020-12](https://json-schema.org/draft/2020-12/json-schema-core):
  contrato estructural y tratamiento de vocabularios.
- [RFC 8785](https://www.rfc-editor.org/rfc/rfc8785.html): canonicalización JCS
  propuesta para identificar contenido; no sustituye la semántica de CXP.

El censo detallado de consumidores se conserva como evidencia temporal de la
revisión, no como documentación de otro repositorio dentro de CXP. Su base debe
refrescarse antes de una futura aceptación o implementación.
