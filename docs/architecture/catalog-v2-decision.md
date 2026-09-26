# Decisión local: catálogo documental v2

Estado: aceptada para implementación el 26-09-2026 por la instrucción de
ejecutar la propuesta definitiva de catálogos. Esta decisión pertenece a CXP;
no incorpora RFCs ni semántica propietaria de Cosecha, Mongoeco o Mochuelo.
Publicar un artefacto sigue siendo una decisión separada.

## Problema observado

Los catálogos exchange v1 de las migraciones Cosecha y Mongoeco describen
`metadata_keys` como `string_set`, pero el catálogo no limita sus miembros al
vocabulario real del owner. Un typo puede parecer un hecho comunicado y llegar
a una evaluación. Cosecha necesita distinguir operaciones, scopes y perfiles
por su contrato, y Mongoeco necesita separar opciones y operaciones de
consulta, actualización, agregación y búsqueda. Esos owners conservarán la
autoría de sus vocabularios; CXP debe rechazar tokens que el catálogo exacto
declare ajenos.

Las cotas físicas y de configuración expresadas por los productos usan enteros,
decimales exactos y cantidades con dimensión. El catálogo v1 fija sus tipos,
pero no puede invalidar un valor que esté fuera del dominio admitido por el
contrato del propietario. Una condición de requisito `range` no sustituye la
validación intrínseca de la declaración, porque otra rama puede no preguntar
por esa propiedad. Además, la trazabilidad de un catálogo completo necesita
anclaje de su significado por capacidad, propiedad y operación.

## Decisión

Se añade `cxp.catalog` `spec_version: 2` con schema independiente y uso opt-in.
Las cadenas y conjuntos declaran dominio abierto o cerrado explícito. Las
propiedades numéricas pueden declarar extremos tipados e inclusividad. Cada
elemento y el catálogo declaran fuente, revisión y localizador. Los formatos
v1 se conservan; snapshot y requisitos v1 pueden referirse exactamente a un
catálogo v2 porque la forma de sus valores y referencias no cambia.

La semántica, campos, errores y matriz de lectores están en
[catalog-v2.md](../protocol/catalog-v2.md). CXP valida todos los documentos y
ramas antes de evaluar. Un token o valor fuera del dominio del catálogo es un
error contractual, no un veredicto incompatible. Un valor válido que no cumple
el requisito sí es incompatible. La ausencia de un dato requerido permanece
indeterminate. No se consulta una fuente documental para decidir conformidad.

## Alternativas descartadas

- Dejar dominios y cotas en extensiones no críticas permitiría que un lector
  ignorase la garantía. Una extensión crítica v1 no puede evaluarse sin cambiar
  el lector y su negociación.
- Añadir las restricciones a `cxp.catalog` v1 reescribiría su contrato y
  cambiaría hashes históricos.
- Un registro central de vocabularios o resolución por import/network
  contradiría la propiedad local y el pinning exacto.
- Definir tiers jerárquicos o `at_least` genérico no resuelve los límites ni
  conserva condiciones multidimensionales.

## Aceptación observable

- Lectura v1 intacta; lector antiguo rechaza v2; acuerdo v1 no admite v2.
- Dominios con permutación dan bytes idénticos; duplicados y tokens ajenos
  rechazan tanto observación como constantes de requisitos.
- Las cotas comparan exactamente, con dimensión y extremos inclusivos o
  exclusivos; contradicciones y exceso rechazan antes de evaluar.
- Un `any` no oculta la rama inválida. Snapshot/requisitos v1 conservan su
  versión y el núcleo puro no carga validadores.
- API y CLI coinciden; ambos validadores JSON Schema comprueban estructura;
  los oráculos semánticos portables siguen independientes.
- Wheel/sdist y consumidores se verifican para la minor que adopte v2; ninguna
  versión de catálogo propietario cambia sin identidad, versión y SHA nuevos.

La decisión de qué propiedades concretas migran a v2 pertenece a la matriz
por elemento y a los catálogos de cada propietario. La implementación de CXP
por sí sola no cierra esa matriz ni el plan de convergencia.
