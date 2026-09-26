# Catálogo CXP, spec_version 2

Este contrato opt-in amplía únicamente `cxp.catalog`. Snapshot y requisitos
siguen en `spec_version: 1`; sus referencias fijan la identidad, versión SemVer
y SHA-256 exactos del catálogo v2. Contexto v2 sigue siendo independiente. La
versión del paquete y `evaluator_version` tampoco se derivan del catálogo.

El esquema estructural independiente es `schemas/catalog-v2.json`. El lector
v1 rechaza el documento con `unsupported_version`. El lector nuevo acepta
catálogos v1 sin reinterpretar sus bytes ni restricciones. Una negociación
debe seleccionar `cxp.catalog` v2 expresamente; no se rebaja a v1 un catálogo
v2 que requiera sus garantías.

## Referencia documental

El catálogo, cada capacidad, cada propiedad y cada operación declaran
`source`: `reference`, `revision` y `locator` no vacíos. `scope` y `sha256`
son opcionales. `reference` nombra el documento o fuente del propietario;
`revision` fija su edición; `locator` identifica la parte que sustenta el
elemento. `scope` delimita la correspondencia cuando es parcial. CXP conserva
esos datos y los incluye en el hash; no descarga, ejecuta ni autentica la
fuente. La inclusión de una referencia no acredita conformidad del proveedor.

## Dominios de cadena

Las propiedades `string` y `string_set` declaran obligatoriamente `domain`.
`{"mode":"open"}` permite cualquier cadena del tipo. Un dominio cerrado
declara `{"mode":"closed","values":[...]}` con al menos un valor. Los valores
son literales sensibles a mayúsculas; no hay aliases ni jerarquía. Un miembro
duplicado rechaza el catálogo. El conjunto se ordena en bytes canónicos;
permutarlo no cambia su hash.

Una cadena o miembro observado fuera del dominio cerrado invalida el snapshot
con `value_outside_domain`. Lo mismo ocurre con una constante `equals`,
`one_of` o un miembro exigido por `contains_all`: el requisito es inválido antes
de cualquier rama `all`/`any`. Un valor válido que difiere del requisito es
`incompatible`. Una propiedad requerida ausente sigue siendo `indeterminate`.
`null` conserva la semántica v1 cuando la propiedad lo permite; no es miembro
del dominio.

## Límites numéricos

Las propiedades `integer`, `decimal` y `quantity` pueden declarar `bounds` con
`minimum` y/o `maximum`. El tipo del extremo coincide con el tipo de propiedad:
entero JSON seguro, cadena decimal exacta o cantidad con unidad y dimensión
correctas. Cada extremo admite `minimum_inclusive` o `maximum_inclusive`; si se
omite, es inclusivo. Una cota invertida o un intervalo vacío rechaza el
catálogo con `invalid_catalog_bounds`. Los límites se comparan con aritmética
exacta, incluso entre unidades de una misma dimensión.

Un valor observado fuera de los límites invalida el snapshot con
`below_catalog_minimum` o `above_catalog_maximum`. Las constantes `equals` y
`one_of` también deben pertenecer al dominio numérico del catálogo. Los
umbrales `minimum`/`maximum` de un requisito `range`, su `step` y su `origin`
son predicados, no valores declarados del proveedor: conservan las reglas de
tipo y dimensión v1 y pueden quedar fuera de las cotas del catálogo. Un
requisito `range` válido que el valor observado no satisface es
`incompatible`.

Los documentos v1 no obtienen dominios ni límites por defecto. Los límites
generales de tamaño, profundidad, nodos, referencias y números de exchange
siguen aplicándose antes y después de la normalización. No se admiten claves
desconocidas ni extensiones críticas sin implementación.

## Compatibilidad y oráculos

| Lector/acuerdo | Catálogo v1 | Catálogo v2 |
| --- | --- | --- |
| Lector anterior | Semántica v1 | `unsupported_version` |
| Lector nuevo, acuerdo v1 | Semántica v1 | `format_not_negotiated` |
| Lector nuevo, acuerdo v2 | Requiere acuerdo v1 aparte | Valida dominio, cotas y referencias |

Las pruebas de conformidad comparan el esquema con `jsonschema` y
`jsonschema-rs`, y fijan oráculos semánticos independientes: compatible,
incompatible, indeterminate, documento inválido y contrato no negociado. El
schema acredita estructura; el evaluador único resuelve la compatibilidad.
Los vectores portables están en `vectors/catalog-v2.json`; incluyen el
catálogo, snapshots y requisitos como datos, con resultados esperados escritos
desde este contrato. El catálogo con cotas invertidas es estructuralmente
válido y semánticamente inválido.
