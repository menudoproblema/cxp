# Intercambio documental CXP, versión 1

## Alcance y autoridad

Especificación del intercambio enriquecido implementado por `cxp.exchange`
en la serie 4.0. La versión del documento es `1`; la negociación en vivo usa
protocolo `2`. Ninguna de ellas se deduce de la versión del paquete Python.
El handshake y los DTOs heredados siguen usando sus contratos anteriores.

Este documento define la semántica. Los esquemas JSON distribuidos con CXP
definen la estructura. Los vectores portables comprueban ambas cosas, pero
no sustituyen la especificación ni acreditan conformidad universal.

No se ejecutan operaciones ni se descubren máquinas. Tampoco se consultan
relojes, redes, registros globales, rutas de archivos o código suministrado
por un documento. La autorización para producir o reintentar pertenece al
consumidor, no al evaluador.

## Documentos y límites

Un documento es un objeto JSON UTF-8 con `document_type`, `spec_version` y
`payload`. Los tipos son `cxp.catalog`, `cxp.snapshot`, `cxp.requirements`,
`cxp.context`, `cxp.evaluation`, `cxp.exchange_request` y
`cxp.exchange_response`. Cada payload tiene un esquema propio. El lector
exige explícitamente el tipo esperado; no prueba parsers heredados como
alternativa. El productor no puede entregar una familia nueva a una
integración que solo declare comprender el formato antiguo.

Se usan nombres `snake_case`. Las claves desconocidas se rechazan fuera de
las zonas explícitas de datos o extensiones. No hay aliases implícitos.
Los documentos tienen un máximo de 1 MiB UTF-8, 32 niveles de anidamiento,
20 000 nodos (contando también las claves) y 16 384 caracteres por cadena.
El árbol de requisitos admite como máximo 1 000 nodos en total.
Cada colección contractual
tiene además un máximo de 1 000 elementos. Los límites se aplican antes de
validar esquemas o calcular requisitos. No pueden relajarse mediante datos
de entrada. Se vuelven a comprobar después de insertar los valores por
defecto: todo documento exportado debe poder leerse con los mismos límites.
Un consumidor puede imponer un límite de tamaño inferior.

Las claves JSON duplicadas, números no finitos, Unicode con sustitutos
aislados y enteros fuera de `[-9007199254740991, 9007199254740991]` se
rechazan, incluso dentro de extensiones. Los números no enteros del JSON
general tienen semántica IEEE 754 binary64; una representación decimal que
no conserva su valor decimal tras la conversión se rechaza. Las magnitudes
contractuales y decimales exactos nunca usan números JSON.

## Extensiones y errores

La envolvente y cada nodo de requisito admiten `extensions`, un objeto
indexado por identificadores con namespace, y `critical_extensions`, una
lista de esas claves. Cada clave crítica debe existir en `extensions` y no
puede repetirse. La versión 1 base no implementa extensiones críticas:
cualquier clave crítica causa `UnsupportedContractError` sobre el documento
completo, aunque figure en una rama de `any` que otra condición satisfaga.
No existe una opción para declarar extensiones comprendidas sin implementar
su semántica. Añadir soporte requiere otra implementación/versionado explícito.

Las extensiones no críticas se conservan en las entradas y sus huellas,
pero no aportan capacidades ni alteran resultados. Los formatos/versiones
desconocidos también generan `UnsupportedContractError`. Una forma inválida,
referencia incoherente, clave duplicada o límite excedido genera
`InvalidDocumentError`. Ambos conservan diagnósticos con código y ruta JSON
Pointer y nunca producen un veredicto funcional.

Los diagnósticos se ordenan de forma determinista por ruta y código. En
requisitos se identifican `step_requires_origin` (ruta al origen ausente),
`origin_requires_step` (ruta al paso ausente) y `duplicate_set_value` (ruta al
miembro repetido de `contains_all`), incluso dentro de grupos anidados.
El esquema conserva sus restricciones: estos códigos precisan el rechazo,
no reemplazan su validación. Un entero fuera del rango seguro se clasifica
como `unsafe_integer` antes de convertirlo a float, tanto desde JSON como
desde un objeto Python equivalente. Su
mensaje es explicativo; código y ruta son la superficie estable. Se acota
la representación de valores observados y no se incluye una copia completa
del documento en una excepción.

## Catálogos y propiedades

Cada catálogo tiene `identity` (`namespace`, `name`, `version`), `owner` y
una lista `capabilities`. La identidad no contiene rutas Python. Namespace
y nombre son ASCII no vacíos; la versión es una versión SemVer completa.
Una referencia añade `sha256`, la huella exacta del documento del catálogo.
Una identidad/version no puede resolver a dos contenidos distintos dentro
del mismo registro. No se resuelven referencias por red.

Una capacidad declara `name`, `properties` y `operations`. Las propiedades
son un objeto de nombres estables a definiciones; cada definición declara
`kind`: `string`, `boolean`, `integer`, `decimal`, `quantity` o `string_set`.
`quantity` declara una dimensión: `length`, `mass`, `resolution` o `angle`.
Una propiedad opcional puede faltar sin que el proveedor afirme no soportarla.
Si admite `null`, declara `nullable: true` y un `null_meaning` descriptivo
no vacío. `null` es un valor literal para igualdad o pertenencia; nunca es
cero, ilimitado o no soportado. Un rango sobre `null` no se satisface.

Las claves de `properties` son simples; no contienen `/` ni `~`. Los
requisitos las referencian mediante el JSON Pointer `/properties/<nombre>`.
La versión 1 no admite expresiones JSONPath, comodines ni navegación por
atributos Python. Una ruta no declarada por el catálogo es un requisito
inválido, no una propiedad ausente del proveedor.

Cada operación declara `name`, `result_type` y `idempotency`; puede declarar
`input_type`. Estos tipos son identificadores documentales con namespace,
no nombres importables. Una operación se identifica dentro de su capacidad.
La declaración de una capacidad no implica que implemente otra. Compartir
nombre de operación entre capacidades no genera herencia.

La idempotencia declara `state`: `guaranteed`, `not_idempotent` o `unknown`.
Omitir la declaración equivale a `unknown`. Una garantía condicionada incluye
`key`, `scope` y `window_seconds` positivos. No equivale a garantía
incondicional. CXP describe las condiciones; no genera claves, recuerda
peticiones ni ejecuta reintentos. Un `False` heredado se adapta a `unknown`
salvo revisión explícita del catálogo. Una operación de envío de impresión
sin deduplicación se declara `not_idempotent`.

## Snapshots y contexto

El snapshot declara `provider_id`, `subject_id`, `catalog`,
`configuration_revision`, `observed_at`, `source` y `capabilities`.
`source` identifica `kind` (`declared`, `observed`, `tested`) y `reference`.
`observed_at` y todos los instantes usan UTC `YYYY-MM-DDTHH:MM:SS[.ffffff]Z`.
La procedencia no establece una jerarquía automática de confianza.

Cada capacidad observada tiene `name`, `support` y `properties`; puede
declarar `operations` mediante bindings con `name` y `result_type`.
`support` es `supported`, `accepted_noop` o `unsupported`. Una capacidad no
declarada es información desconocida, no un cuarto estado del enum heredado.
Bindings duplicados, operaciones o propiedades ajenas al catálogo, resultados
contradictorios y valores del tipo/dimensión incorrectos invalidan el snapshot.
No se materializan valores de ejemplo o defaults de catálogo como observados.

Los datos observados opcionales `availability`, `connectivity` y `consumables`
son dimensiones independientes. No cambian `support`. El evaluador base no
deduce que un dispositivo puede producir ahora únicamente porque soporte
una operación. El cliente debe revisar las condiciones operativas por separado.

El contexto declara `subject_id` y `configuration_revision`, y puede declarar
`as_of` y `max_age_seconds`. Este último es un entero no negativo de segundos;
la edad observada conserva microsegundos y el límite es inclusivo. Un máximo
de edad exige `as_of`. Las identidades
de sujeto o revisiones distintas no se mezclan: dan resultado indeterminado.
Un snapshot posterior a `as_of` o anterior a `as_of - max_age_seconds` tampoco
acredita vigencia. El límite de antigüedad es inclusivo. Sin política temporal
no se introduce una caducidad implícita. La ausencia de `as_of` no consulta
el reloj. Cada evaluación recibe exactamente un snapshot; no fusiona
afirmaciones conflictivas ni elige automáticamente la más favorable.

## Requisitos

Un documento de requisitos declara la referencia exacta `catalog` y un nodo
`requirement`. Todos los nodos tienen un `id` único dentro del documento.
Los nodos compuestos usan `operator: all|any` y `conditions` no vacío.
Los nodos hoja tienen `capability`, `operator` y `require_effective`, cuyo
valor por defecto es `true`. Pueden exigir `operations`, una lista de nombres
que deben estar declarados tanto en el catálogo como en el snapshot.

Los operadores hoja son:

| Operador | Contrato |
| --- | --- |
| `support` | Comprueba el soporte y las operaciones exigidas. |
| `equals` | La propiedad indicada por `path` es igual a `value`. |
| `one_of` | La propiedad es uno de los valores de `values`, una lista no vacía. |
| `contains_all` | El conjunto `string_set` contiene todos los miembros de `values`. |
| `range` | La propiedad numérica cumple los límites y, si se declara, el paso. |

Las comparaciones son tipadas: `true` no es igual a `1`; una cadena no se
convierte implícitamente en un número. Dos cantidades de la misma dimensión
se comparan tras conversión exacta; dimensiones diferentes invalidan el
requisito. Dos `string_set` se comparan sin atender al orden; no admiten
duplicados. `contains_all` con una lista requerida vacía es válido y exige
que la propiedad esté presente y bien formada; los grupos lógicos vacíos
y `one_of` vacío no son válidos. Si el catálogo permite un `string_set` nulo,
`contains_all` sobre ese `null` no se satisface, ni siquiera con lista requerida
vacía: `null` no es un conjunto. La ausencia de la propiedad sigue siendo
indeterminada.

`range` declara al menos `minimum` o `maximum`, y opcionalmente
`minimum_inclusive` y `maximum_inclusive` (ambos `true` por defecto).
Si los límites coinciden, ambos deben ser inclusivos. Un rango invertido
es inválido. `step` debe ser positivo y requiere `origin`; `origin` sin
`step` es inválido. Se comprueba que `(valor - origin) / step` sea entero
exacto, incluso para valores negativos. Límites, origen y paso tienen el
tipo y dimensión de la propiedad. No se aplican tolerancias implícitas.

## Evaluación

La validación de todos los documentos y requisitos precede a la evaluación.
Un nodo mal formado o no entendido no se oculta por cortocircuito lógico.

- `compatible`: todos los requisitos necesarios están acreditados.
- `incompatible`: existe un incumplimiento demostrado.
- `indeterminate`: documentos válidos y entendidos no bastan para decidir.

`unsupported` incumple el soporte. `accepted_noop` lo incumple cuando
`require_effective` es `true`; en caso contrario lo satisface, pero no
aporta automáticamente propiedades ni operaciones no declaradas.
Una capacidad, propiedad u operación necesaria no informada da resultado
indeterminado. No se convierte en incompatibilidad mediante una política
operativa de denegación. Los datos expresamente distintos del requisito dan
incompatibilidad. Dentro de una hoja, un incumplimiento conocido domina la
ausencia de una operación requerida; son condiciones conjuntas. Un contexto
no aplicable o caduco invalida antes el uso de toda la declaración.

En `all`, cualquier incompatible domina; después domina indeterminate y,
solo si no hay ninguno, compatible. En `any`, cualquier compatible domina;
después indeterminate y, si todos incumplen, incompatible. El resultado
conserva el diagnóstico de cada hoja en orden de recorrido del documento,
incluidas las ramas que no determinan el veredicto global.

El resultado documental incluye `verdict`, `evaluator_version`, referencias
de contenido de catálogo/snapshot/requisitos/contexto y `findings` por hoja
con ID, veredicto, código, ruta del requisito, `snapshot_path` y motivo.
La ruta al snapshot identifica el dato de origen, aunque una propiedad no
esté informada; es `null` si la capacidad completa no está informada.
Con las huellas de entrada y esas rutas se recuperan valor y requisito sin
duplicar documentos completos en cada diagnóstico. Un resultado recibido
es una declaración: verificar su corrección exige reevaluar las entradas.
La versión semántica inicial del
evaluador es `1.0.0`. El resultado no incluye timestamps generados, UUIDs
aleatorios ni detalles de un proceso local.

## Exactitud e identificación de contenido

Una cantidad es `{"value": "12.5", "unit": "mm"}`. Los decimales usan
`-?(0|[1-9][0-9]*)(\.[0-9]+)?`, como máximo 128 caracteres. No se aceptan
exponentes, `+`, espacios, NaN o infinitos. Se normalizan ceros negativos y
ceros fraccionarios finales, conservando el valor exacto. La propiedad
`decimal` usa la misma gramática sin unidad. Su comparación es exacta, pero
su cadena se conserva al calcular la huella: el lector documental no resuelve
catálogos y no puede distinguirla de una propiedad `string`. Por tanto,
`"0.30"` y `"0.3"` pueden tener huellas distintas y ser iguales al evaluar.

Unidades y factores exactos respecto a la base de cada dimensión:

| Dimensión | Base | Factores |
| --- | --- | --- |
| Longitud | mm | um = 1/1000; mm = 1; in = 127/5; pt = 127/360 |
| Masa | g | g = 1; kg = 1000 |
| Resolución | dpi | dpi = 1 |
| Ángulo | deg | deg = 1 |

`cm` y `m` no forman parte del vocabulario v1. Un adaptador puede convertirlos
exactamente a mm antes de emitir datos; no se aceptan aliases implícitos.

Las comparaciones usan aritmética racional exacta. No se modifica el contexto
decimal global y no se redondean conversiones no finitas como decimales.
La equivalencia física no exige la misma huella: conservar `1 in` o `25.4 mm`
identifica declaraciones distintas que pueden satisfacer el mismo requisito.

Una entrada aceptada posee una copia aislada y no modificable de sus datos.
Sus exportaciones devuelven copias; mutar una fuente o exportación no cambia
las evaluaciones posteriores. La huella es SHA-256 de la envolvente completa
normalizada y canonicalizada mediante JCS. No se incluyen huellas propias
en el contenido que se hashea. Arrays conservan su orden, salvo conjuntos
tipados, que se ordenan por punto de código Unicode. Los timestamps se normalizan a
UTC con seis cifras de microsegundos. Se materializan extensiones vacías,
listas críticas vacías, operaciones vacías de snapshots, nulabilidad falsa,
idempotencia desconocida y los valores por defecto de los requisitos.
No se ordenan las alternativas de `one_of`. Las extensiones opacas conservan
sus valores y órdenes de arrays. Las cadenas generales no se
normalizan en Unicode. Un hash identifica contenido, no prueba autenticidad
ni veracidad de una declaración.

## Negociación en vivo y compatibilidad

La solicitud anuncia `protocol_version: 2` y `formats`: tipos documentales
con `spec_versions` admitidas. El receptor responde `accepted` únicamente
si comprende todos los tipos requeridos en una versión común; selecciona
la mayor versión común por tipo. La respuesta está ligada a la huella de
la solicitud. Si no hay acuerdo, responde `rejected` con motivo y sin
formatos seleccionados. No se degrada a protocolo 1 ni se eliminan requisitos.
Una respuesta aceptada se valida contra la solicitud antes de habilitar el
envío o lectura de documentos. La lista de familias no acredita extensiones
críticas que esta versión no comprende.

Los lectores offline exigen el tipo y versión del documento. No puede
garantizarse que todo lector 3.1 rechace una envolvente nueva: algunos aceptan
objetos desconocidos como una matriz vacía. La frontera segura es el lector
explícito o el acuerdo validado, no añadir un campo a un DTO antiguo.

La API heredada conserva imports, registro por defecto, validación en
construcción de perfiles, estados de soporte, providers sync/async y
telemetría. Se endurece el rechazo de datos inválidos, duplicados y bindings
contradictorios. Estos cambios y los campos de diagnóstico añadidos se
inventarían en la guía de migración; no se retiran contratos antiguos por
comodidad de implementación.

## Referencias

El `$id` URN de cada esquema es una identidad, no un servicio de resolución.
El esquema se distribuye en el paquete y la validación no requiere red.
Publicar una URL estable en el futuro no debe introducir descargas implícitas.

- [JCS, RFC 8785](https://www.rfc-editor.org/rfc/rfc8785.html).
- [JSON Schema 2020-12](https://json-schema.org/draft/2020-12/json-schema-core).
- [Plan de implementación](../architecture/next-release-plan.md).
