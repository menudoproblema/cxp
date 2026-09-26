# Contexto de evaluación CXP, spec_version 2

`cxp.context` v2 añade `accepted_sources` al contexto v1. Es una lista obligatoria,
no vacía, sin repetidos, de `declared`, `observed` y `tested`. Su semántica es de
conjunto: el orden authored no cambia los bytes canónicos ni la huella. No existe
jerarquía de confianza entre las tres fuentes. Se rechazan tipos, valores o
repetidos inválidos antes de evaluar. El diagnóstico específico de repetición
es `duplicate_source` en el índice repetido; los demás errores estructurales
usan `schema_violation`.

El evaluador comprueba sujeto y revisión de configuración, después la fuente y
luego la vigencia temporal. Una fuente excluida da `indeterminate` con código
`source_not_accepted` para cada hoja; nunca es `incompatible`. La versión
semántica del evaluador para contexto v2 es `1.1.0`. El reporte sigue siendo
`cxp.evaluation` v1; su huella incluye la huella del contexto y esa versión.
Las entradas con contexto v1 siguen usando el evaluador `1.0.0`, con bytes y
resultados históricos intactos. No se añade este criterio a extensiones
no críticas: un lector que ignore un campo no puede afirmar la garantía.

El snapshot v1 conserva una sola `source` para todas sus capacidades. Un
productor no puede calificar el documento como `observed` porque sondeó solo
una parte. Debe omitir afirmaciones sin evidencia de esa fuente o producir
documentos separados. `source.reference` puede nombrar por contenido un informe
propietario con método, versión, condiciones y cobertura. CXP fija la referencia
en la huella del snapshot, pero no lee, interpreta ni autentica el informe. El
consumidor decide si las afirmaciones requeridas quedan cubiertas.

## Compatibilidad

| Lector / oferta | Contexto v1 | Contexto v2 |
| --- | --- | --- |
| Lector anterior a v2 | Lee con su semántica v1 | `unsupported_version`; no hay veredicto |
| Lector nuevo, oferta solo v1 | Lee con semántica v1 | `format_not_negotiated` |
| Lector nuevo, oferta v1 y v2 | Selecciona v2 por negociación; puede leer v1 fuera de ese acuerdo | Lee y evalúa procedencia |
| Integración que exige v2 | Rechaza por versión | Lee y evalúa procedencia |

La negociación conserva protocolo en vivo `2` y selecciona la versión máxima
común de cada familia. Solo `cxp.context` tiene versiones `(1, 2)`; las demás
familias siguen en v1. Un consumidor que exige procedencia debe ofrecer solo
contexto v2 y rechazar un acuerdo sin esa versión. No hay fallback automático.
Un contexto v2 incompleto o una semántica desconocida se rechaza como documento
inválido o contrato no soportado, antes de la lógica `all`/`any`.

El esquema estructural independiente está en
`src/cxp/exchange/schemas/context-v2.json`. `document_schema()` sin argumentos
sigue devolviendo el esquema v1 publicado. Para la nueva familia/versión se
consulta `document_schema(document_type="cxp.context", spec_version=2)` o
`cxp schema document --type cxp.context --spec-version 2`.

Los vectores portables de `src/cxp/exchange/vectors/context-v2.json` incluyen
documentos estructurales válidos e inválidos, un catálogo y snapshots como
datos, y evaluaciones con veredictos, códigos y versión semántica esperados.
Cubren las tres fuentes admitidas y excluidas, la precedencia de sujeto,
revisión, procedencia y vigencia, la semántica conservada de v1 y la igualdad
canónica del conjunto `accepted_sources`. Los oráculos están escritos desde
esta especificación; un consumidor puede ejecutarlos sin importar CXP.

Versión del paquete, `spec_version`, identidad/versión/huella de catálogo y
`evaluator_version` son identidades separadas. Un catálogo nuevo se fija por
namespace, nombre, versión SemVer y SHA-256 exactos; no se selecciona latest,
no se importa código por identificador y no se descarga nada.
