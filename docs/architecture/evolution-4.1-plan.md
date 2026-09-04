# Plan de evolución de CXP: integración, capacidades y diagnósticos

## Estado, autoridad y objetivo

- Estado: **Implemented in worktree**; aprobado por el mantenedor el 2026-09-04.
- Cierre pendiente: commit, CI remota, etiqueta y publicación requieren órdenes
  posteriores y evidencia propia.
- Fecha: 2026-09-04.
- Base: CXP 4.0.0, commit `a6e352dae5b9ea244fcc415b4c9a4b0d1792a566`.
- Versión materializada: **4.1.0**, conservando los contratos indicados en este
  plan.
- Owner: CXP. La autorización cubre la implementación local; no cubre cambios
  en consumidores, commit, etiqueta, push ni publicación.

Queremos que un integrador pueda describir una configuración, declarar lo
que necesita, comprobar compatibilidad y entender el resultado sin construir
su propio evaluador ni aprender detalles internos de CXP.

Este plan incorpora las mejoras útiles de la revisión posterior a 4.0.0.
No reabre esa entrega ni sustituye su
[plan histórico](next-release-plan.md). La autoridad del comportamiento
vigente sigue en la [especificación v1](../protocol/exchange-v1.md).
Lo que aquí se describe como nuevo nació como propuesta y ya está materializado
en el worktree. La sección 14 separa la implementación local de la evidencia que
solo puede obtenerse después de commit, CI, etiqueta y publicación.

CXP sigue siendo autónomo: un solo repositorio y distribución, Python >=3.12,
licencia vigente y validaciones locales. No incorporamos `_standards`, registros
RFC de gdynamics, servicios internos ni dependencias de repositorios hermanos.
Este documento es la propuesta local; no necesita darse de alta en una
gobernanza externa para ser revisado o aprobado.

## 1. Punto de partida contrastado

| Observación | Estado en 4.0.0 | Decisión |
| --- | --- | --- |
| El extra `exchange` no existe. | Incorrecto: existe en `pyproject.toml` y en el wheel; README es coherente. | Conservar y cubrir como regresión; no aplicar esa corrección. |
| Faltan carga máxima y dimensiones del objeto. | Cierto en el catálogo de referencia; el motor ya admite cantidades de masa y longitud. | Ampliar el catálogo, no especializar el motor. |
| Faltan `cm` y `m`. | Exclusión expresa del vocabulario documental v1. | Facilitar entrada convertida a mm; no cambiar el lector v1. |
| Los incumplimientos usan `property_mismatch`. | Cierto; los códigos y resultados existentes tienen consumidores y vectores. | Añadir explicaciones optativas sin sustituir esos códigos. |
| No existe CLI. | Cierto; no hay entrypoint publicado. | Incorporar validación y evaluación como adaptadores finos. |
| Cada acceso a `payload` deserializa. | Cierto e intencionado: cada exportación es una copia aislada. | Vista tipada optativa y eliminación de lecturas redundantes internas. |
| Falta ejemplo pedagógico completo. | El módulo ejecutable recorre vectores; `examples/` contiene ejemplos legacy. | Añadir ejemplos comprensibles, sin retirar las pruebas portables. |
| La CI conoce una ruta fija de release. | `.github/workflows/ci.yml` usa `dist/4.0.0` en verificación y subida de evidencia. | Derivar las rutas de la candidata para no validar otra versión. |
| Las candidatas locales no están protegidas contra reemplazo. | El constructor mueve wheel, sdist y manifiesto sobre `dist/<versión>` sin comprobar evidencia previa. | Construcción atómica y rechazo de versiones ya publicadas o candidatas distintas. |
| La verificación salta de base a `dev`. | No existe una instalación aislada que solicite únicamente `cxp[exchange]`. | Probar base, extra de runtime y entorno de tests como alcances distintos. |
| La evidencia de licencias usa el entorno agregador. | Puede no coincidir con las dependencias instaladas dentro de wheel y sdist. | Capturar versiones, licencias y `pip check` dentro de cada entorno limpio. |
| La CI solo usa Linux. | La librería es portable, pero la futura CLI añade rutas, consola y códigos de salida. | Mantener la matriz completa en Linux y añadir smoke en macOS y Windows. |
| No hay tests generativos. | Hay vectores y casos límite manuales de buena calidad. | Añadir propiedades sobre exactitud, normalización, composición e inmutabilidad. |
| Esquemas y catálogos se descubren principalmente desde Python. | Los recursos son portables, pero no hay una interfaz de extracción para otras herramientas. | Añadir comandos de consulta y exportación sin crear otro registro. |
| No existe una política pública de estabilidad. | Changelog y migración explican versiones concretas, pero no qué superficies prometemos conservar. | Documentar API estable, deprecación y superficies experimentales. |
| La publicación depende de credenciales y controles operativos externos. | No hay workflow de publicación, política de seguridad ni attestations en el repositorio. | Añadir una ruta OIDC separada, mínima y aprobable, sin reconstruir artefactos. |

En la revisión precedente pasaron los 26 vectores de evaluación y las sondas
de unidades, aislamiento y carga. Son evidencia de la base, no acreditación
de esta propuesta ni sustituto de los gates de una futura candidata.

## 2. Fronteras y consumidores

| Elemento | Responsabilidad de CXP | Fuera de CXP |
| --- | --- | --- |
| Catálogo | Vocabulario, tipos, identidad, versión y referencias exactas. | Inventario de máquinas reales y elección de la configuración. |
| Snapshot | Declaración de capacidades con sujeto, contexto y procedencia. | Medir, autenticar o certificar físicamente la declaración. |
| Requisitos | Restricciones explícitas sobre lo declarado. | Calcular posiciones, carga o dimensiones a partir de un diseño. |
| Evaluación | Comparación exacta, tres veredictos y trazabilidad. | Autorizar producción, reservar capacidad o ejecutar operaciones. |
| Diagnóstico | Explicar el dato comparado y la condición incumplida. | Mensajes específicos del taller, traducciones y decisiones del operario. |
| CLI y API Python | Acceso consistente a las mismas reglas. | Un servicio persistente, UI, colas o motor de workflows. |

Tórculo podrá calcular las dimensiones y masa del montaje, seleccionar una
configuración y producir los documentos. CXP comprobará las restricciones
declaradas. Tórculo seguirá comprobando posición, origen, obstáculos,
tolerancias, zonas imprimibles, composición, PDF y preparación del trabajo.
Los controladores, RIP y conectores permanecen fuera de este plan.

La inspección local identifica Cosecha y Mongoeco como consumidores de APIs
heredadas, con dependencias `cxp>=4.0.0`. Tórculo todavía no contiene imports
Python de `cxp.exchange`, pero su plan de equipos lo declara como dependencia
estructural futura y fija actualmente 4.0.0. Es por tanto un consumidor de
diseño que debe probar la candidata antes de cambiar esa restricción. Esto no
demuestra ausencia de usuarios externos, imports dinámicos o catálogos privados.
Los contratos públicos se conservan aunque no encontremos un caller local.

El inventario operativo de consumidores y sus pruebas deberá refrescarse antes
de publicar. Su evidencia pertenece a cada consumidor; no se convierte en
dependencia de desarrollo de CXP ni autoriza migraciones desde este plan.

## 3. Compatibilidad que no se negocia dentro de esta entrega

1. Conservamos las APIs heredadas, imports, excepciones y registro existentes.
2. `evaluate_requirements(...)` sigue devolviendo un `Document`.
3. Para las mismas entradas, conservamos bytes normalizados, hashes, códigos,
   orden de findings y versión semántica del resultado documental vigente.
4. Conservamos `spec_version: 1` y la negociación optativa de protocolo v2.
   No confundimos esas versiones con la versión del paquete.
5. No sobrescribimos catálogos publicados ni reinterpretamos sus referencias.
6. `Document.payload` y `as_dict()` continúan devolviendo copias aisladas.
7. La instalación base sigue requiriendo solo `msgspec`; las dependencias de
   intercambio permanecen en `cxp[exchange]`.
8. No añadimos consultas de red, reloj implícito, imports por nombre de catálogo,
   fallback al registro legacy ni downgrade silencioso.
9. Las superficies públicas no se deducen de que un módulo pueda importarse:
   se inventariarán y documentarán explícitamente antes de publicar la candidata.

Una ruptura de cualquiera de estas garantías obliga a detener la entrega
afectada y presentar otra decisión de compatibilidad. No se rebaja el criterio
ni se cambia una fixture antigua para hacer pasar una 4.1.0 incompatible.

Versiones distintas que mantendremos separadas:

| Superficie | Propuesta |
| --- | --- |
| Paquete Python | 4.1.0 materializada; cierre remoto y publicación pendientes. |
| Documentos enriquecidos | v1 sin ampliación de vocabulario. |
| Negociación en vivo | Protocolo v2 sin cambios. |
| Catálogo físico | Nueva versión 1.1.0, conservando 1.0.0. |
| Evaluador documental | 1.0.0 mientras la proyección documental siga idéntica. |
| Detalle Python y presentación CLI | Superficies nuevas y optativas; no se anuncian como otro formato CXP. |

### 3.1. Política pública de estabilidad

Antes de publicar documentamos qué se considera estable. Como mínimo incluye
los exports públicos de `cxp` y `cxp.exchange`, las firmas documentadas, los
tipos y códigos de error públicos, las familias documentales/versiones, la
semántica del evaluador, los esquemas portables y cada identidad/version/hash
de catálogo ya publicado.

Los módulos y símbolos con guion bajo, helpers de `scripts/`, estructura interna
de ficheros y texto humano no documentado quedan fuera. Los formatos de salida
de CLI que se declaren JSON sí serán contrato; el texto orientativo de ayuda y
explicación podrá mejorar sin considerarse un protocolo.

Una superficie pública nueva es estable por defecto. Si necesitamos experimentar,
debe llevar una marca explícita, alcance y criterio para estabilizarla o retirarla;
no usamos «provisional» para evitar definir su contrato. Una retirada o cambio
incompatible de una API estable requiere una major. Una deprecación ordinaria
permanece al menos durante la siguiente minor y ofrece reemplazo y aviso; un
problema de seguridad o corrección grave puede exigir otra política documentada.

Esta entrega no depreca APIs. Añade de forma compatible un loader versionado,
resultado detallado, helper de entrada, CLI y catálogo físico 1.1.0. Ese conjunto
de superficies nuevas y útiles —no el hardening de release por sí solo— justifica
la versión 4.1.0. Si cualquiera exige romper la proyección 4.0.0, deja de ser
alcance de esta minor.

## 4. Catálogos físicos útiles y realmente versionados

### 4.1. Carga explícita de versiones

Proponemos ampliar `load_reference_catalog` con un argumento keyword-only
`version`. Las llamadas actuales sin versión seguirán seleccionando exactamente
el catálogo 1.0.0; no pasarán a significar «el más reciente».

Ejemplo de API propuesta:

```python
catalog = load_reference_catalog("physical-printing", version="1.1.0")
```

Conservamos `REFERENCE_CATALOGS` como inventario de nombres. Añadimos
`ReferenceCatalogInfo`, una estructura inmutable con nombre, namespace, versión
y SHA-256, y `list_reference_catalogs() -> tuple[ReferenceCatalogInfo, ...]`.
La consulta devuelve todas las versiones ordenadas por namespace, nombre y
versión, sin consultar servicios externos.
El registro interno relacionará nombres/versiones conocidos con recursos;
no interpolará rutas arbitrarias aportadas por el usuario.

Los ficheros 1.0.0 y sus hashes permanecen intactos. La nueva versión vivirá en
un recurso separado, empaquetado junto a los anteriores. Versiones o nombres
desconocidos se rechazan explícitamente; no se busca una versión parecida.
`CatalogStore` podrá contener ambas versiones y resolverá siempre identidad
y SHA-256. No migrará automáticamente snapshots ni requisitos.

### 4.2. Ampliación de `physical-printing`

Mantenemos `printing.surface` y las cinco propiedades actuales. Proponemos
incorporar a 1.1.0 las siguientes propiedades, todas no nulas cuando se informen:

| Propiedad | Tipo | Significado |
| --- | --- | --- |
| `max_loaded_mass` | Cantidad, masa | Masa total máxima cargada en la configuración; incluye útil, objetos y elementos de sujeción declarados, no el peso de la máquina. |
| `max_object_width` | Cantidad, longitud | Anchura máxima admitida del objeto o montaje, en el eje X de esa configuración. |
| `max_object_length` | Cantidad, longitud | Longitud máxima admitida del objeto o montaje, en el eje Y de esa configuración. |
| `print_mode_id` | String | Identificador del modo seleccionado dentro de la configuración; no nombre universal del fabricante. |
| `resolution_x` | Cantidad, resolución | Resolución del modo seleccionado en X. |
| `resolution_y` | Cantidad, resolución | Resolución del mismo modo seleccionado en Y. |

En la documentación de 1.1.0 aclaramos que `max_width` y `max_height` son las
dimensiones imprimibles X/Y y `max_thickness` el límite Z. Conservamos los
nombres existentes; no introducimos aliases que escondan un cambio de significado.
Los ejes deben corresponderse con la declaración del productor, no con una
rotación inferida por CXP.

No hacemos obligatorias todas las propiedades en cada snapshot. Una propiedad
no informada solo produce `indeterminate` si un requisito la necesita.
No inventamos valores predeterminados, ceros, infinitos ni canales de tinta.
El esquema genérico valida tipos, no certifica que los límites sean físicamente
razonables. Esa comprobación corresponde al productor y a su validación de dominio.

### 4.3. Configuraciones, modos y combinaciones

Una declaración corresponde a una configuración concreta y coherente. Una
mesa con succión, otra sin ella, dos juegos de tinta o dos modos incompatibles
no se fusionan tomando máximos o uniendo conjuntos. Cada variante se declara
y evalúa por separado, con su revisión de configuración correspondiente.

`resolution_x` y `resolution_y` describen el par seleccionado, no dos máximos
independientes que el consumidor pueda combinar. Si solo conocemos una cifra
comercial de resolución máxima, no la convertimos en un modo acreditado.
No añadimos ahora un lenguaje de dependencias entre modos ni un buscador de
configuraciones. El consumidor selecciona candidatos y solicita evaluaciones.

Para el ejemplo pedagógico usamos una mesa genérica con dos configuraciones:
capacidad de carga de 8 kg y de 4 kg. Un requisito de capacidad mínima de 5 kg
produce compatible e incompatible respectivamente. La suma de útil, piezas y
elementos cargados debe calcularla el consumidor según la definición física
del productor; CXP no calcula pesos ni descuenta accesorios por su cuenta.

Como contraste de necesidad, Roland publica para la MO-240 objetos de hasta
640 × 488 mm, área imprimible de 610 × 458 mm y carga de 8 kg, reducida a 4 kg
con mesa de succión. Son límites distintos, no una geometría completa del útil.
[Especificaciones oficiales de Roland](https://www.rolanddg.eu/es-es/productos/impresoras/serie-versaobject-mo).

El manual también separa origen y área de impresión, incluyendo colocación
mediante coordenadas cuando se usa un elemento de sujeción. Esa información
justifica que Tórculo conserve la colocación geométrica como responsabilidad
propia; dos comprobaciones de anchura/longitud no bastan para acreditar el encaje.
[Configuración del área de impresión](https://downloadcenter.rolanddg.com/contents/manuals/MO-240_USE_EN/oyu1716517275862.html).

No incorporamos fichas oficiales de Roland ni de otros fabricantes a CXP.
Las referencias anteriores justifican el vocabulario; los ejemplos siguen
siendo sintéticos, sin prometer certificación de máquinas o seguridad física.

## 5. Evaluación detallada y ergonomía sin alterar el intercambio

### 5.1. Una API nueva, no otro evaluador

Proponemos `evaluate_requirements_detailed(...) -> EvaluationResult`, con los
mismos documentos y registro explícito que la función actual. El resultado
será una estructura tipada e inmutable con:

- `document`: el `cxp.evaluation` v1 convencional.
- `verdict`: uno de los tres estados existentes.
- `is_compatible`: exactamente `verdict == "compatible"`.
- `findings`: tupla de diagnósticos tipados, en el mismo orden de hojas.

Los findings conservarán ID, veredicto, código, rutas y mensaje del diagnóstico
documental; añadirán un motivo preciso y los operandos necesarios para explicarlo.
Ausencia de valor y valor explícito `null` se distinguirán mediante presencia
explícita, no mediante un `None` ambiguo. Los valores compuestos se expondrán
como estructuras inmutables; cualquier exportación mutable será una copia.

El motor de comparación será único. La API actual proyectará su resultado al
documento existente; la nueva expondrá además el detalle. No repetimos toda la
evaluación para explicar su resultado ni reconstruimos causas con otro conjunto
de reglas en la CLI. El detalle de una evaluación recibida de otro proceso no
se considera verificado: para acreditarlo hacen falta las entradas y reevaluar.

Las exportaciones documentales conservarán únicamente el contrato v1. No
insertamos los nuevos datos en `payload`, no reemplazamos `property_mismatch`
y no tratamos el objeto Python detallado como una nueva familia portable.

### 5.2. Motivos precisos y deterministas

| Condición | Motivo detallado propuesto |
| --- | --- |
| Valor menor que mínimo, o igual a un mínimo exclusivo | `below_minimum` / `minimum_excluded` |
| Valor mayor que máximo, o igual a un máximo exclusivo | `above_maximum` / `maximum_excluded` |
| Valor fuera de la cuadrícula definida por origen y paso | `step_mismatch` |
| Igualdad no satisfecha | `value_not_equal` |
| Ninguna alternativa de pertenencia coincide | `value_not_in_set` |
| Faltan elementos requeridos | `missing_set_elements` |
| Valor explícitamente nulo frente a requisito de rango | `null_not_comparable` |

Para el resto, reutilizamos las causas actuales de soporte, ausencia y contexto.
Conservamos la precedencia vigente: contexto no aplicable antes de comparar;
soporte y ejecución efectiva; discrepancia conocida de propiedad; operación
necesaria no informada; propiedad no informada. En rangos, mínimo, máximo y paso
se comprueban en ese orden. No cambiamos el veredicto al explicar mejor la causa.

El detalle conserva valores y unidades originales. La comparación usa valores
exactos; la presentación no puede redondear y aparentar una contradicción.
Los elementos faltantes de un conjunto se ordenan determinísticamente.
No incluimos documentos completos, datos ajenos a la condición ni secretos de
extensiones en la explicación; tampoco se registran automáticamente en logs.

El motivo describe la comparación, no la decisión industrial. Si una capacidad
de carga de 4 kg se compara con un mínimo requerido de 5 kg, el motivo es
`below_minimum`. Traducirlo a «el montaje pesa demasiado» pertenece a Tórculo.

### 5.3. Tres estados, también en las interfaces cómodas

No añadimos `unmet_requirements()` agrupando incompatibles e indeterminados.
Tampoco denominamos «bloqueos» a todas las hojas no compatibles. En `any`, una
alternativa satisfecha basta aunque otras fallen o carezcan de datos.

Los findings explican hojas; el veredicto global explica la composición.
Un filtro por estado debe llamarse y documentarse como tal. `is_compatible`
es una comodidad de lectura, no autorización para producir ni sustituto del
veredicto. No se redefine la verdad booleana del objeto resultado.

### 5.4. Coste e inmutabilidad

Reutilizamos datos locales deserializados dentro de una llamada cuando sea
posible. No alteramos las copias públicas de `Document`, no añadimos cachés
globales ni compartimos diccionarios mutables entre evaluaciones.
Las propiedades del resultado tipado no vuelven a decodificar el documento.

Medimos casos pequeños y próximos a los límites de documentos/requisitos.
La validación incluye memoria y tiempos comparativos con la base, sin umbrales
de microsegundos dependientes de una máquina ni promesas de velocidad sin medir.
Una regresión material sin explicación obliga a revisar el diseño antes del cierre.

## 6. Unidades cómodas en la entrada, estrictas en el documento

Proponemos un helper explícito `quantity_from_input(value, unit)` que recibe
una cadena decimal y una unidad. Para las unidades documentales existentes
conserva la unidad y devuelve un `Quantity` validado; para `cm` y `m`, convierte
exactamente a `mm` antes de construirlo.

No cambia el constructor `Quantity`, el lector documental, los esquemas ni el
hash de un documento ya admitido. `Quantity("1", "cm")` y un documento con
unidad `cm` siguen siendo inválidos; el nuevo helper produce `10 mm`.

No aceptamos floats, coma decimal, notación científica, texto libre, aliases
por mayúsculas ni unidades desconocidas. No introducimos otra gramática.
Reutilizamos validación decimal y límites existentes, incluyendo el tamaño
del resultado tras convertir. Conservamos la exactitud independientemente del
contexto global de `Decimal`, sin multiplicaciones que redondeen silenciosamente.

La magnitud genérica sigue admitiendo los valores que admite el contrato;
no añadimos una prohibición global de negativos porque ciertos límites físicos
no deban ser negativos. Esa regla pertenece a su dominio.

Se aplaza admitir `cm`/`m` directamente en el intercambio. Solo merecerá otra
versión documental si una integración necesita preservar esas unidades en
origen y destino; la comodidad de escribirlas en una UI no exige ese cambio.

## 7. CLI pequeña, estricta y utilizable en automatizaciones

### 7.1. Comandos propuestos

```bash
cxp validate snapshot.json --type cxp.snapshot
cxp validate snapshot.json --type cxp.snapshot --catalog catalog.json
cxp evaluate --catalog catalog.json --snapshot snapshot.json \
  --requirements requirements.json --context context.json
cxp evaluate --catalog catalog.json --snapshot snapshot.json \
  --requirements requirements.json --context context.json --explain
cxp schema document
cxp schema operation org.cxp:document-result:1
cxp catalog list
cxp catalog show physical-printing --version 1.1.0
```

`--type` será obligatorio al validar. No hay selección permisiva de parser ni
fallback a documentos heredados. `--catalog` puede repetirse y construye un
registro local explícito; las referencias no autorizan descarga alguna.

- `validate` comprueba estructura e invariantes intrínsecas de la familia
  indicada. Con catálogos y un snapshot o requisitos, comprueba también
  referencias, propiedades y operaciones mediante `CatalogStore`.
- El alcance de la validación aparece siempre en el resultado: una validación
  documental correcta no acredita resolución de catálogo, compatibilidad,
  corrección de una evaluación recibida ni plausibilidad física.
- `--catalog` para otras familias se rechaza como opción no aplicable, sin
  fingir que ha añadido comprobaciones. Verificar una evaluación recibida
  contra todas sus entradas queda fuera de estos comandos iniciales.
- `evaluate` utiliza exactamente el evaluador público y exige contexto como
  fichero. No toma la hora actual ni adivina configuración.
- `--explain` usa el resultado detallado, pero conserva la misma salida
  documental y código de retorno; la explicación legible va a stderr.
- `schema document` emite el esquema completo de intercambio que distribuye el
  paquete; `schema operation` reutiliza `operation_schema`, sin reconstruir
  `$defs` ni cambiar sus identificadores.
- `catalog list` emite un inventario JSON determinista de nombres, versiones,
  identidades y hashes. `catalog show` escribe los bytes canónicos del recurso
  exacto; omitir versión conserva el mismo default que la API Python.

La entrada inicial son ficheros locales explícitos. No añadimos URLs, globbing,
descubrimiento recursivo, stdin múltiple ni un directorio vigilado.
Leemos con el límite documental más un byte para detectar exceso sin cargar
un fichero arbitrariamente grande. Reutilizamos los límites y errores del lector.

### 7.2. Salidas y errores

`evaluate` escribe solo el documento canónico y un salto de línea en stdout,
también cuando el resultado es incompatible o indeterminado. No mezcla logs,
avisos ni explicaciones con ese JSON.

`validate` escribe un recibo JSON de la herramienta con versión de formato 1,
estado `valid`, familia, versión documental, hash y alcance
`document` o `catalog`. Se documentan y prueban sus campos exactos; no se
presenta como una nueva familia del protocolo CXP.

Los errores van a stderr, con categoría, códigos/rutas disponibles y sin
documento de evaluación ficticio en stdout. Un error esperado no imprime un
traceback; un fallo inesperado no se convierte en incompatibilidad.
`--diagnostics text|json` controla esa presentación; el modo JSON tiene una
envolvente estable con versión propia. No mezcla texto humano con JSON ni
expone automáticamente documentos completos o extensiones recibidas.

| Código de salida | Significado |
| --- | --- |
| 0 | Validación correcta en el alcance indicado, o evaluación compatible. |
| 1 | Evaluación incompatible. |
| 2 | Uso incorrecto o dependencias opcionales necesarias ausentes. |
| 3 | Evaluación indeterminada. |
| 4 | Documento inválido, error semántico o referencia de catálogo no resoluble. |
| 5 | Familia, versión o extensión crítica no soportada. |
| 6 | Error de lectura o escritura de entrada/salida. |
| 70 | Fallo interno inesperado, distinto de un resultado funcional. |

Los scripts consumidores decidirán si detenerse ante 1 o 3; la CLI no cambia
su significado para simular una política de autorización.

### 7.3. Instalación y punto de entrada

La CLI se distribuye con CXP y usa `argparse`; no añade un framework de comandos.
El entrypoint estará en un módulo ligero fuera de `cxp.exchange`, con imports
de intercambio diferidos. Así `cxp --help` y `cxp --version` funcionarán en la
instalación base, sin cargar dependencias opcionales.

Los comandos que necesiten intercambio indicarán cómo instalar `cxp[exchange]`
si falta. Solo se interceptan dependencias opcionales realmente ausentes; un
import interno roto no se oculta como instrucción de instalación.
No añadimos otro paquete o extra `cli` para el mismo conjunto de dependencias.

Los comandos de descubrimiento no necesitan `exchange` cuando solo muestran
versión y ayuda. Consultar esquemas o catálogos sí necesita el extra mientras
su carga dependa de los validadores; no duplicamos un segundo lector de recursos
para evitar esa dependencia. La implementación podrá eliminar esa necesidad
solo si reutiliza bytes empaquetados sin bifurcar validación ni semántica.

## 8. Ejemplos y documentación que enseñen el recorrido real

Añadimos `examples/document_exchange.py`, autocontenido y comentado, que muestre:

1. Carga de una versión exacta del catálogo y construcción del registro.
2. Declaración de sujeto, configuración, procedencia y capacidades.
3. Requisitos de un trabajo sin cálculos geométricos ni control de equipos.
4. Contexto explícito y evaluación.
5. Los tres veredictos: cumple, incumple y falta información.
6. Resultado documental, hashes y lectura cómoda del resultado detallado.
7. Un caso `any` con alternativa no satisfecha y resultado global compatible.

No depende de Tórculo, equipos, red, rutas del mantenedor ni de los vectores
como fuente de sus datos. Los casos se construirán explícitamente y tendrán
resultados esperados revisados desde el contrato.

Conservamos `python -m cxp.exchange.examples` y su comportamiento anterior.
Añadimos al módulo o a otro recurso empaquetado una entrada separada para el
ejemplo pedagógico, de forma que pueda ejecutarse también desde el wheel.
El script de `examples/` será una entrada delgada, sin duplicar la demostración.

La guía de integración incorporará el recorrido Python y los comandos CLI,
la diferencia entre validez y compatibilidad, los códigos de salida, unidades
de entrada frente a unidades documentales y los límites del diagnóstico.
Los ejemplos de CLI usarán ficheros reproducibles proporcionados por el ejemplo;
su generación requerirá un destino explícito y no sobrescribirá ficheros existentes.

## 9. Calidad y cadena de publicación

### 9.1. Candidatas recuperables e inmutables

La construcción completa su trabajo en un directorio temporal y solo promociona
wheel, sdist y manifiesto como una unidad. Un error no puede dejar una mezcla de
artefacto nuevo y manifiesto anterior.

Si `dist/<versión>` contiene una fuente distinta, el constructor falla sin
reemplazar nada. Una candidata no publicada solo puede sustituirse mediante una
opción explícita que compruebe primero el target exacto. Si existe evidencia
`published_verified`, la única salida es incrementar la versión: no hay override.
No consultamos PyPI silenciosamente para decidir esto; la evidencia local y el
proceso de publicación son autoridades explícitas y una comprobación remota es
un gate separado.

La construcción de desarrollo puede identificar un árbol sucio, pero la
evidencia de release exige árbol Git limpio, commit fijado y huella de fuente
coincidente. Antes del upload se comprueba que la etiqueta solicitada apunta a
ese commit. Construir, etiquetar y publicar siguen siendo autorizaciones distintas.

### 9.2. Tres instalaciones y dependencias reales

Cada wheel y sdist se prueba en entornos nuevos con tres alcances:

1. paquete base, sin dependencias de intercambio;
2. `cxp[exchange]`, sin instalar herramientas de desarrollo;
3. entorno de tests, usado para ejecutar la suite contra el artefacto instalado.

En los dos primeros ejecutamos `python -m pip check`, imports y recursos propios
del alcance. La matriz prueba conjuntamente los mínimos declarados de `msgspec`,
`jsonschema`, `referencing` y `rfc8785`, y otra resolución con las últimas
versiones permitidas. No afirmamos que probar cada mínimo por separado cubra la
combinación que realmente resolverá un usuario.

Cada informe recoge desde el propio entorno limpio Python, plataforma, CXP,
dependencias transitivas, licencias y resultado de `pip check`. El manifiesto
de construcción registra además versiones del backend, `build`, `wheel`,
`setuptools` y Twine. La cadena de construcción/release usa constraints o un
lock revisado y versionado; los rangos de runtime siguen en `pyproject.toml` y
no se sustituyen por el lock de desarrollo.

### 9.3. Portabilidad proporcionada al riesgo

Linux conserva la matriz completa de tres versiones de Python, políticas de
dependencias, wheel y sdist. macOS y Windows ejecutan al menos instalación base
y `exchange`, `pip check`, imports, lectura de recursos, ejemplo y CLI con rutas
Unicode/con espacios, separación stdout/stderr y códigos de salida.

Al ser un wheel `py3-none-any`, no multiplicamos toda la matriz sin una garantía
diferente. Un fallo específico de sistema operativo amplía sus casos; pasar los
smoke no certifica cualquier shell, terminal o distribución de Python.

### 9.4. Propiedades, vectores y fuzzing acotado

Añadimos tests generativos con límites y semilla reproducible para comprobar:

- normalización idempotente y bytes/hash idénticos tras releer;
- comparación exacta y simétrica de cantidades equivalentes;
- conversión cm/m a mm sin depender del contexto decimal;
- tablas trivaluadas de árboles `all` y `any`;
- coherencia entre resultado detallado y documento 4.0.0;
- aislamiento ante mutaciones de entradas y exportaciones;
- rechazo acotado de profundidad, número de nodos, cadenas y enteros límite.

Los ejemplos minimizados de cualquier fallo se convierten en regresiones
deterministas. Estas pruebas no generan resultados esperados desde el evaluador
ni reemplazan los vectores portables revisados de manera independiente. La
dependencia generativa es solo de desarrollo y no entra en wheel/sdist runtime.

### 9.5. Publicación y seguridad del repositorio

Preparamos un workflow separado de publicación que consume exactamente los
artefactos ya construidos y acreditados; nunca los reconstruye. Se activa por
la etiqueta esperada, usa un environment protegido con aprobación y concede
solo `contents: read` e `id-token: write` al job que publica.

Preferimos Trusted Publishing de PyPI mediante OIDC, sin token duradero, y
adjuntamos attestations a cada wheel/sdist. Una attestation acredita origen e
integridad respecto de esa identidad, no calidad ni ausencia de vulnerabilidades.
La comprobación posterior descarga desde PyPI, compara hashes y repite el smoke.

Las acciones reutilizadas de GitHub Actions se fijan por SHA completo y se
anota la versión humana que corresponde. Añadimos revisión de cambios de
dependencias y una política de
actualización; ninguna actualización se fusiona automáticamente sin los gates.
`SECURITY.md` documenta canal privado, versiones soportadas y expectativas de
respuesta, sin prometer plazos que el mantenedor no pueda sostener.

La metadata de PyPI añade URLs bien conocidas para documentación y changelog.
No añadimos badges de seguridad o conformidad que no estén respaldados por un
gate. Un SBOM podría publicarse como evidencia adicional más adelante, pero no
es condición para esta minor porque la evidencia ya registra dependencias y
licencias exactas de cada entorno probado.

## 10. Reutilización y contención del alcance

| Pieza | Garantía / mecanismo actual | Disposición | Valor diferencial o motivo |
| --- | --- | --- | --- |
| `Document` | Validación, bytes propios y copias aisladas. | `reuse` | No se pierde seguridad para ahorrar un acceso a `payload`. |
| `CatalogStore` | Resolución exacta e inmutable por identidad/hash. | `reuse` | Ya admite catálogos personalizados y múltiples versiones distintas. |
| Loader de referencia | Un recurso por nombre. | `justify` | Selección explícita y coexistencia de versiones sin cambiar defaults. |
| Catálogo físico ampliado | Masa, resolución y longitud ya existen como tipos. | `derive` | Cubre carga, objeto y modo sin tocar el lenguaje genérico. |
| Comparador y evaluación detallada | Veredicto correcto con causa genérica. | `consolidate` | Una sola lógica produce documento estable y detalle explicable. |
| Resultado tipado | Se puede consultar un payload una vez. | `justify` | Acceso tipado, inmutable y sin deserialización repetida para integradores. |
| Entrada en cm/m | Conversión exacta manual a mm. | `derive` | Helper pequeño y explícito evita conversiones inconsistentes. |
| CLI | Las APIs ya validan y evalúan. | `derive` | Acceso desde automatizaciones sin reimplementar reglas. |
| Ejemplo pedagógico | Vectores portables y ejemplos legacy. | `justify` | Enseña autoría de documentos; no sustituye conformidad. |
| CI y verificación de artefactos | Gates completos con algunas rutas fijadas a 4.0.0. | `consolidate` | Una candidata identificada evita acreditar artefactos de otra entrega. |
| Descubrimiento de recursos | Schemas, loader y funciones de consulta ya existen. | `derive` | La CLI los hace utilizables fuera de Python sin definir otra semántica. |
| Política de estabilidad | Changelog y migraciones describen entregas aisladas. | `justify` | Permite adoptar 4.1 con expectativas explícitas y acota futuras rupturas. |
| Instalaciones limpias | Se prueba base y luego un entorno `dev`. | `consolidate` | Separar `exchange` acredita las dependencias que realmente pide el usuario. |
| Evidencia de dependencias | Informes parciales y licencias del agregador. | `consolidate` | Cada entorno identifica exactamente la resolución que ha probado. |
| Tests generativos | Vectores y casos manuales protegen ejemplos conocidos. | `justify` | Exploran invariantes combinatorios sin inventar la semántica esperada. |
| Publicación manual con credencial | Upload autorizado y comprobación posterior ya están separados. | `derive` | OIDC y attestations reducen credenciales duraderas sin cambiar esa separación. |
| Helpers de incumplimiento global | Filtrar hojas no interpreta correctamente `any`. | `remove` | Evita presentar desconocimiento o alternativas como bloqueos. |
| Nueva especificación de unidades | El adaptador de entrada resuelve la necesidad inmediata. | `remove` | Se aplaza; no añade garantía necesaria para esta entrega. |
| Motor de modos, drivers y geometría | Productor y consumidor conocen el dominio. | `remove` | No pertenecen a CXP ni son necesarios para declarar capacidades. |

## 11. Fases y criterios de aceptación

Las fases siguientes definieron el orden de implementación. F0–F4 están
materializadas y F5 conserva gates remotos pendientes, como detalla la sección
14. La existencia de este documento por sí sola no acredita ninguna fase: cada
una necesita sus pruebas y no pospone todos los negativos al cierre de release.

### F0. Aprobar contrato y fijar compatibilidad

- Aprobar esta propuesta local y registrar el alcance autorizado.
- Fijar las API nuevas, tipos, motivos, recibo CLI y tabla de errores en la
  documentación de cada superficie antes de escribir comportamiento productivo.
- Publicar la política de estabilidad y clasificar las superficies existentes
  sin marcar como internas APIs que ya se documentaron para consumidores.
- Añadir fixtures de compatibilidad con procedencia en la 4.0.0 exacta:
  documentos, hashes, diagnósticos, catálogos, defaults y APIs públicas.
- Separar fixtures históricas de vectores nuevos, sin regenerar las primeras
  desde la implementación que se pretende verificar.

Cierre: decisiones públicas documentadas, fixtures atribuibles a 4.0.0 y
ausencia de cambios al contrato v1. Especificar campos no autoriza cambiar
las decisiones de frontera de este plan.

### F1. Versionado de recursos y catálogo físico

- Loader con selección de versión y consulta de versiones disponibles.
- Catálogo físico 1.1.0 y documentación semántica de propiedades.
- Pruebas de versiones coexistentes, hash incorrecto, selección desconocida,
  propiedad omitida, configuraciones distintas y modos de resolución coherentes.
- Ninguna regla nueva específica de impresión en el evaluador genérico.

Cierre: llamadas antiguas devuelven los mismos bytes; el catálogo nuevo se
evalúa usando el lenguaje v1, también desde instalaciones limpias.

### F2. Motor compartido, detalle y API tipada

- Resultado detallado optativo, motivos precisos y estructuras inmutables.
- Reutilización interna de datos sin cambiar exports de `Document`.
- Pruebas de precedencia, valores falsy, `null`, ausencia, unidades equivalentes,
  pasos, límites exclusivos, conjuntos y árboles `all`/`any`.
- Tests generativos de invariantes y conversión de contraejemplos en regresiones.
- Comparativa de tiempos y memoria en escenarios representativos.

Cierre: la API actual conserva sus bytes de referencia; las razones nuevas
son correctas y deterministas; detalle y resultado no pueden divergir.

### F3. Entrada de unidades y ejemplo completo

- Helper explícito con conversiones exactas cm/m a mm y límites de entrada/salida.
- Ejemplo independiente con resultados esperados y exportación optativa de
  ficheros de demostración a un directorio explícito.
- Rechazo de entradas mal formadas sin ampliar lo aceptado por documentos v1.

Cierre: un integrador puede producir los tres veredictos sin adaptar el código
de tests, configurar una máquina ni clonar otro proyecto.

### F4. CLI e integración documentada

- Entry point, ayuda, versión, validate, evaluate, schema, catalog y explicación
  optativa, derivados de las APIs y recursos existentes.
- Pruebas de procesos reales: stdout/stderr separados, salidas exactas,
  diagnósticos texto/JSON, códigos de retorno, lectura acotada y errores de ficheros.
- Pruebas sin extra, con extra y desde wheel/sdist; ejecución sin checkout.
- Guía y ejemplos de automatización que distingan indeterminado de incompatible.

Cierre: CLI y API dan el mismo documento para las mismas entradas, incluido
con `--explain`; ayuda y versión no necesitan dependencias de intercambio.

### F5. Candidata, artefactos y cierre

- Ajustar CI para derivar directorios y evidencias de la versión candidata;
  reutilizar la lógica de release existente, no crear otro resolutor de versión.
- Promocionar candidatos de forma atómica, impedir sobrescrituras silenciosas
  y exigir árbol limpio/commit fijado al generar evidencia de release.
- Actualizar la versión y las referencias de documentación operativa al preparar
  la candidata; conservar las referencias históricas y fixtures de 4.0.0.
- Ejecutar gates de fuente y matriz de artefactos en Python 3.12/3.13/3.14 con
  dependencias mínimas y actuales permitidas, separando base, `exchange` y dev.
- Ejecutar `pip check`, registrar dependencias/licencias desde cada entorno y
  smoke de instalación/CLI en Linux, macOS y Windows.
- Ampliar verificaciones de recursos: ambos catálogos, entrypoint, ejemplo
  pedagógico, schemas, vectores y marcadores de tipado.
- Actualizar guías, inventario de APIs y un changelog coherente de la entrega.
- Refrescar evidencia de consumidores conocidos y documentar límites externos.
- Fijar acciones por SHA, añadir política de seguridad y preparar Trusted
  Publishing con attestations, sin reconstruir la candidata aprobada.

Cierre técnico: candidata exacta reproducible, matriz verde, compatibilidad
demostrada y documentación alineada. Una evidencia anterior a una modificación
del contenido empaquetado no acredita la candidata nueva.

La publicación sigue el [procedimiento propio](../release.md), con autorización
separada sobre candidata y destino. No se reconstruyen artefactos entre sus
gates y el upload. La vuelta atrás conserva artefactos/documentos anteriores;
no sobrescribe releases ni convierte referencias 1.1.0 a 1.0.0 silenciosamente.

Orden recomendado: F0 → F1 → F2 → F3 → F4 → F5. El ejemplo mínimo puede
prepararse tras F1 y enriquecerse tras F2; no requiere abrir otro proyecto.

## 12. Matriz de aceptación transversal

| Caso | Resultado exigido |
| --- | --- |
| Llamada antigua al loader sin versión | Catálogo 1.0.0 e idéntico hash. |
| Dos versiones del catálogo en el registro | Cada referencia resuelve exactamente la solicitada. |
| Nombre/version/hash desconocido | Rechazo sin red, fallback ni sustitución. |
| Trabajo de 5 kg ante configuración de 8 kg / 4 kg | Compatible / incompatible, sin cálculo físico dentro de CXP. |
| Carga necesaria no informada | Indeterminado, no cero ni capacidad infinita. |
| Útil mayor que área imprimible pero menor que límite de objeto | Restricciones distintas; nunca se declara acreditada su colocación geométrica. |
| Dos modos con pares de resolución distintos | Evaluaciones separadas; no se forma un tercer par tomando máximos. |
| Incumplimiento de mínimo, máximo, exclusión o paso | Motivo preciso; `property_mismatch` documental preservado. |
| `any` con alternativa compatible y otra incompatible/desconocida | Veredicto global compatible, sin etiquetar todo finding como bloqueo. |
| `0`, `False`, cadena vacía, conjunto vacío o `null` admitidos | No se confunden con propiedad ausente; se conserva su semántica por tipo. |
| Contexto caducado o revisión de configuración distinta | Indeterminado antes de usar sus datos para diagnosticar límites. |
| Inputs originales o exportaciones modificadas por el caller | No cambian documentos ni resultados previamente construidos. |
| `1 cm`, `1 m` a través del helper | Cantidades exactas de 10 mm y 1000 mm. |
| `cm`/`m` enviados directamente como documento v1 | Rechazo igual que en 4.0.0. |
| Conversión con Decimal global de poca precisión | Sin pérdida de exactitud; exceso de límites rechazado. |
| JSON duplicado, profundo, grande o extensión crítica desconocida | Rechazo acotado, sin evaluación parcial. |
| `validate` sin catálogo | Éxito solo documental, alcance explícito. |
| CLI evaluate normal / con explicación | Misma salida CXP, mismo retorno; explicación solo en stderr. |
| CLI schema/catalog | Recurso exacto y catálogo versionado recuperables sin imports del consumidor ni red. |
| Diagnósticos CLI JSON | Envolvente estable y parseable, sin texto mezclado ni documentos completos innecesarios. |
| CLI incompatible / indeterminada | Retornos distintos y documento funcional presente en stdout. |
| Base sin `exchange` | Imports legacy, ayuda y versión funcionan; uso de intercambio informa cómo instalarlo. |
| Instalación únicamente con `exchange` | Import, recursos y `pip check` pasan sin depender del extra `dev`. |
| Mínimos conjuntos / últimas permitidas | Ambas resoluciones pasan desde wheel y sdist; informes recogen lo instalado. |
| Wheel y sdist limpios | Recursos y comportamiento completos, sin rutas al checkout ni hermanos. |
| CI sobre nueva candidata | No toma `dist/4.0.0` ni evidencia antigua por una ruta fija. |
| Candidata distinta bajo la misma versión | Rechazo sin reemplazar artefactos, manifiesto ni evidencia anterior. |
| Intento de reconstruir una versión publicada | Rechazo no anulable; exige incrementar versión. |
| Release desde árbol sucio o tag distinto | Evidencia/publicación rechazada antes del upload. |
| macOS/Windows con rutas Unicode y espacios | Instalación, recursos y CLI smoke pasan con códigos/salidas correctos. |
| Publicación autorizada | Mismos hashes acreditados, identidad OIDC y attestation por artefacto. |

## 13. Documentación, evidencias y exclusiones

Este plan es el owner de alcance y secuencia. En la implementación:

- `docs/catalogs/exchange-reference.md` poseerá el vocabulario y la selección
  de versiones; no se duplicará su definición en ejemplos o README.
- `docs/protocol/exchange-integration.md` explicará APIs y ejemplos; una guía
  propia de CLI documentará sus comandos, recibo y errores.
- La semántica del detalle se documentará por separado del intercambio v1,
  enlazando su relación y los motivos que preservan la proyección existente.
- Una guía de estabilidad delimitará APIs, schemas, catálogos, CLI y política
  de deprecación; `SECURITY.md` tendrá un owner operativo distinto.
- `docs/protocol/exchange-v1.md` conservará el contrato vigente, aclarando
  únicamente relaciones sin añadir unidades ni campos nuevos.
- README e índice son entradas breves; CHANGELOG describe la funcionalidad
  implementada y no presenta este plan como sustituto de la entrega.
- Los planes y evidencias de 4.0.0 conservarán su significado histórico.

Los gates existentes son `python scripts/check.py`, construcción de candidata,
verificación de artefactos y agregación de evidencia. Actualmente no hay un
validador documental o RFC autónomo configurado; se revisarán enlaces y
coherencia de los documentos, sin invocar infraestructura de otro ecosistema.

No forman parte de 4.1.0: nuevos SDKs, servicio HTTP, interfaz gráfica,
telemetría adicional, seguridad criptográfica, directorio público de catálogos,
descubrimiento de dispositivos, lenguaje de reglas arbitrario, solucionador
de modos, cálculo geométrico, control de máquinas o otro sistema de licencias.

Persistir/intercambiar el detalle enriquecido entre lenguajes, admitir unidades
nuevas en documentos o añadir relaciones entre configuraciones podrá justificar
otra propuesta. Se conserva como estudio futuro, no como requisito oculto
para cerrar esta entrega.

## 14. Resultado de implementación

F0–F4 están materializadas en 4.1.0: API versionada de catálogos, catálogo
físico 1.1.0, evaluación detallada sobre el mismo motor, helper exacto de entrada,
tutorial, CLI y contratos públicos de estabilidad y diagnósticos. El documento
`cxp.evaluation` v1, el evaluador 1.0.0, los catálogos 1.0.0 y el default del
loader se conservan.

F5 está implementada como tooling, pero su evidencia final no puede declararse
en un árbol sin commit: la candidata no sobrescribe versiones, la verificación
separa base/exchange/dev, comprueba todos los mínimos directos y la última
resolución, registra licencias desde cada entorno y añade smoke en macOS/Windows.
La publicación manual consume esa misma candidata mediante OIDC y attestations;
no se ejecuta ni queda acreditada por este cambio local.

La búsqueda de endurecimiento añadió tres medidas con garantía observable que no
alteran el dominio: acciones de CI fijadas a SHA completo, revisión/actualización
de dependencias y `SECURITY.md`. No se incorporaron Scorecard, SBOM ni un formato
de explicación portable: pueden aportar valor después, pero no son condición
para la semántica ni para publicar esta minor y ampliarían innecesariamente su
superficie.

## 15. Fuentes del análisis

- [Configuración y extras](../../pyproject.toml).
- [Documentos y copias aisladas](../../src/cxp/exchange/documents.py).
- [Magnitudes exactas](../../src/cxp/exchange/quantities.py).
- [Resolución y validación de catálogos](../../src/cxp/exchange/registry.py).
- [Loader de referencia](../../src/cxp/exchange/reference.py).
- [Catálogo físico actual](../../src/cxp/exchange/catalogs/physical-printing.json).
- [Evaluación y precedencias](../../src/cxp/exchange/evaluation.py).
- [Ejemplos ejecutables actuales](../../src/cxp/exchange/examples.py).
- [Vectores portables](../../src/cxp/exchange/vectors/exchange-v1.json).
- [Pruebas de intercambio](../../tests/test_exchange.py).
- [Pruebas de vectores](../../tests/test_exchange_vectors.py).
- [CI](../../.github/workflows/ci.yml).
- [Verificación de artefactos](../../scripts/verify_artifacts.py).
- [Contribución autónoma](../../CONTRIBUTING.md).

Referencias externas que justifican los gates, no la semántica de CXP:

- [Trusted Publishing de PyPI](https://docs.pypi.org/trusted-publishers/):
  credenciales OIDC breves en lugar de tokens duraderos.
- [Attestations de PyPI](https://docs.pypi.org/attestations/): vinculación de
  cada distribución a una identidad y digest de publicación.
- [Uso seguro de GitHub Actions](https://docs.github.com/en/actions/reference/security/secure-use):
  pin por SHA completo como referencia inmutable.
- [`pip check`](https://pip.pypa.io/en/stable/cli/pip_check/): comprobación de
  compatibilidad de las dependencias instaladas.
- [Hypothesis](https://hypothesis.readthedocs.io/en/latest/): generación de
  casos y reducción de contraejemplos para propiedades.
- [Estructuración y bundling de JSON Schema](https://json-schema.org/understanding-json-schema/structuring):
  uso de `$id`, `$defs` y recursos autocontenidos. CXP ya distribuye esquemas
  con identificador; la CLI debe exportarlos, no reescribirlos.
- [URLs conocidas de metadata Python](https://packaging.python.org/en/latest/specifications/well-known-project-urls/):
  etiquetas interoperables para documentación y changelog.
