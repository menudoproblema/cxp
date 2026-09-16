# Capacidades industriales declarativas

Este documento fija el vocabulario de posicionamiento, identificación y
acabado del intercambio v1. Son catálogos para snapshots, requisitos y
evaluaciones reproducibles. No son controladores, un plan de producción ni una
certificación de una instalación; todos los ejemplos son sintéticos.

## Selección y compatibilidad

| Catálogo | Versión nueva | Versión por omisión | Selección explícita |
| --- | --- | --- | --- |
| `positioning` | 1.0.0 | 1.0.0 | `load_reference_catalog("positioning")` |
| `identification` | 1.0.0 | 1.0.0 | `load_reference_catalog("identification")` |
| `finishing` | 1.1.0 | 1.0.0 | `load_reference_catalog("finishing", version="1.1.0")` |
| `document-processing` | 1.1.0 | 1.0.0 | `load_reference_catalog("document-processing", version="1.1.0")` |

Las versiones 1.0.0 publicadas no cambian. Una llamada sin `version` no escoge
la versión más reciente. La identidad, la versión y el hash se incluyen en el
snapshot y en los requisitos, de modo que el consumidor debe seleccionar antes
el catálogo y la configuración que quiere evaluar.

## Posicionamiento y registro

| Capacidad | Declara | No declara |
| --- | --- | --- |
| `positioning.physical_referencing` | Tipo de referencia física, contacto/útil y alcance de pieza, hoja, panel o segmento. | Cámara, medida óptica, transformación o compensación. |
| `positioning.feature_detection` | Marcas, bordes, esquinas o fiduciales detectables; método de adquisición, perfil y límites declarados. | Estimar una transformación o aplicarla. |
| `positioning.transformation_estimation` | Modelo, alcance global/local, referencias mínimas y, si se declara completo, límite de error. | Movimiento o éxito de un registro físico. |
| `positioning.compensation_application` | Fuente, modelo y alcance de una compensación de coordenadas. | Detección, estimación o éxito físico. |

Una referencia física como `registration_pin` se declara separada de un método
de adquisición como `camera_image`; OPOS y CCD no son valores alternativos de
una clasificación de CXP. Los perfiles de marca son identificadores estables
del productor, nunca imágenes ni recetas serializadas.

**Posicionamiento** sitúa un objeto respecto de referencias. **Registro
geométrico** estima la relación entre sistemas de coordenadas. **Calibración**
establece una relación metrológica de un sistema de medida y queda fuera del
catálogo. La convención de coordenadas —origen, ejes, orientación y unidad— es
contrato del consumidor: CXP no la calcula ni presupone una común.

`max_position_error` solo significa algo junto con `error_metric` y
`error_conditions_id` en un snapshot de configuración concreta. No es
resolución, repetibilidad ni incertidumbre. El esquema v1 comprueba los tipos,
pero no exige que aparezcan las tres propiedades, no cierra el vocabulario de
la métrica ni comprueba plausibilidad física. Ese contrato cruzado corresponde
al productor del snapshot o a una evolución explícita del protocolo.

## Identificación

`identification` es independiente de `positioning`:

| Capacidad | Propiedad | Límite deliberado |
| --- | --- | --- |
| `identification.symbol_generation` | `symbologies`, `content_profiles`, módulo y zona silenciosa | Generar no implica leer ni verificar. |
| `identification.symbol_reading` | `symbologies`, `content_profiles`, módulo y zona silenciosa | Leer correctamente no certifica calidad. |
| `identification.quality_verification` | `symbologies`, `quality_methods`, `content_profiles`, módulo y zona silenciosa | Declara método, no resultado o certificado. |

El vocabulario inicial de portadores es `qr_code` y `data_matrix`, referidos a
ISO/IEC 18004 e ISO/IEC 16022. `gs1_element_string` y
`gs1_digital_link_uri` son perfiles de contenido distintos: se pueden
declarar, pero CXP no concluye que todo QR/Data Matrix sea GS1 ni interpreta
Application Identifiers. No hay lectura/generación de imágenes, búsqueda de
ficheros ni disparo automático a partir de un código.

`content_profiles`, `min_module_width`, `max_module_width` y
`minimum_quiet_zone_modules` se declaran dentro de la capacidad funcional que
los aplica. Así, una configuración puede generar un perfil o un módulo que no
lee, o verificar con límites distintos, sin que el evaluador combine esas
declaraciones. Los límites físicos no son una capacidad global ni habilitan
otra función por inferencia.

## Acabado y documentos

`finishing` 1.1.0 conserva `finishing.folding` y `finishing.binding` y añade
`finishing.through_cut`, `finishing.kiss_cut`, `finishing.creasing` y
`finishing.perforation`. La capacidad nombra el proceso; `tool_type` describe
la clase de herramienta y `configured_tool_id` identifica su selección local.
No crean una base universal de herramientas. Los límites de material y de
dimensiones pertenecen a esa combinación concreta de proceso, herramienta y
configuración; no son máximos fusionables.

Estos catálogos físicos no publican operaciones. Declarar una capacidad física
no publica por ello un endpoint invocable. El contrato existente de envío y
observación sigue siendo la única superficie para una solicitud y un resultado
declarado.

`document-processing` 1.1.0 conserva 1.0.0 y separa `document.acceptance`,
`document.feature_recognition`, `document.feature_preservation` y
`document.production_interpretation`. Perfiles, Processing Steps y separaciones
técnicas se pueden declarar como características, pero aceptar un PDF no prueba
que su acabado se reconozca, preserve o interprete; interpretar tampoco otorga
capacidad física. CXP no crea un RIP ni procesa documentos.

## Configuraciones y evaluación

Cada snapshot representa una configuración coherente. Un consumidor selecciona
externamente, por ejemplo, `wide-tool` o `narrow-tool`, publica una revisión
por configuración y evalúa cada candidato de forma independiente. Nunca une
anchuras, herramientas o propiedades de dos snapshots. No existe una evaluación
multicatálogo: que `positioning` y `finishing` resulten compatibles por separado
no acredita un proceso completo.

Capacidad, disponibilidad, configuración, evidencia/procedencia y resultado de
ejecución son dimensiones distintas. Los requisitos de detección, compensación
y corte conservan `require_effective: true`; `accepted_noop` no satisface esos
efectos. `unsupported` es incompatible y un dato no publicado es
`indeterminate`. El contexto debe coincidir en sujeto, configuración y política
temporal.

## Matriz de correspondencias

La matriz es trazabilidad conceptual. «Exacta» solo significa que el nombre
coincide con el alcance limitado de la propiedad; no declara conformidad de
CXP, un catálogo o una instalación con la fuente.

| Concepto CXP | Fuente, edición y apartado | Correspondencia | Diferencia o garantía no cubierta |
| --- | --- | --- | --- |
| Procesos de acabado | [PWG 5100.1 IPP Finishings 2.1](https://ftp.pwg.org/pub/pwg/candidates/cs-ippfinishings21-20170217-5100.1.pdf), §1 y vocabulario Finishings | Parcial | IPP modela atributos de impresión; CXP no envía trabajos ni perfila un dispositivo IPP. |
| Proceso, recurso y configuración | [JDF 1.8](https://www.cip4.org/files/cip4/documents/JDF%20Specification%201.8%20www.pdf), introducción y modelo de proceso/recurso | Parcial | JDF describe workflow; CXP solo declara capacidad evaluable. |
| Relación con JDF | [XJDF 2.2](https://www.cip4.org/files/cip4/documents/XJDF%20Specification%202.2.pdf), §1.3.7 | Sin equivalente | CXP no es JDF/XJDF ni intercambia tickets o XJMF. |
| Processing Steps PDF | [ISO 19593-1:2018](https://www.iso.org/standard/65428.html), §1 | Parcial | Se declara reconocimiento, preservación o interpretación; no se analiza PDF. |
| Uso público de Processing Steps | [GWG Packaging](https://gwg.org/packaging/), apartado Processing Steps | Parcial | La documentación y ejemplos GWG no se incorporan ni se ejecutan; CXP solo describe la capacidad declarada. |
| Modelo de visión | [OPC UA Machine Vision](https://reference.opcfoundation.org/specs/OPC-40100-1/full), §1 y §13 | Parcial | No hay OPC UA, estado de máquina, receta ni resultado de visión. |
| Funciones de cámara | [GenICam SFNC 2.8](https://www.emva.org/wp-content/uploads/GenICam_SFNC_v2_8.pdf), categorías de características | Parcial | No se adoptan nodos SFNC ni un SDK de cámara. |
| QR Code | ISO/IEC 18004, edición aplicable, cláusulas de simbología | Exacta para el nombre | CXP no codifica, renderiza ni verifica QR. |
| Data Matrix | ISO/IEC 16022, edición aplicable, cláusulas de simbología | Exacta para el nombre | CXP no codifica, renderiza ni verifica Data Matrix. |
| GS1 y calidad de símbolo | [GS1 General Specifications 25.0](https://ref.gs1.org/standards/genspecs/25.0.0/?v=1), §5 | Parcial | Perfil, portador y método de calidad permanecen separados. |
| Error y condiciones metrológicas | [VIM JCGM 200](https://jcgm.bipm.org/vim/en/2.23.html), §2.23, §2.24 y §2.34 | Parcial | Solo se admite una cota con métrica/condiciones; no hay modelo de incertidumbre. |
| Unidades futuras | [UCUM](https://ucum.org/), UCUM Specification | Sin equivalente | V1 no admite UCUM libre, conversiones implícitas ni unidades improvisadas. |
| Círculos, esquinas y bordes | [Sinajet MCC](https://www.sinajet.net/CCDSinajetMcc.html), Position | Parcial | Inspira categorías; no verifica una instalación Sinajet. |
| Marcas y compensación | [Summa OPOS](https://www.summa.com/media/lccbhxat/opos20_en.pdf), introducción y §2 | Parcial | Ilustra fases separadas; OPOS no es un tipo de cámara CXP. |
| Registro OCC/ICC | [Zünd OCC](https://www.zund.com/en/cutting-systems/registration-methods/over-cutter-camera), descripción | Parcial | No acredita una cámara ni calcula registro. |
| Calibración/alineación | [LightBurn Camera Alignment](https://docs.lightburnsoftware.com/latest/Reference/Cameras/Alignment/), preparación y métodos | Parcial | CXP no ejecuta asistentes de calibración. |
| Fiduciales no impresos | [OpenPnP Fiducial Locator](https://github.com/openpnp/openpnp/wiki/Fiducial-Locator), Operating Principle | Parcial | Justifica ejemplo PCB; no implementa visión ni movimiento. |

No se copiaron especificaciones ni fixtures de terceros. Las fuentes justifican
vocabulario y límites de alcance, no una conformidad completa.

## Decisiones y garantías diferenciales

| Concepto | Requisito protegido | Mecanismo considerado | Decisión | Garantía diferencial |
| --- | --- | --- | --- | --- |
| Referencia física | No atribuir cámara a un útil. | `string_set` y capacidades. | Reutilizar + introducir catálogo. | Se puede exigir un útil sin afirmar detección. |
| Detección | No confundir detectar con registrar. | Soporte existente. | Introducir capacidad. | `accepted_noop` no satisface detección efectiva. |
| Transformación | Declarar modelos sin solver. | Conjunto, entero y cantidad. | Componer. | Modelo/alcance/error sin matrices. |
| Compensación | No inferir aplicación desde estimación. | Capacidad/soporte. | Introducir capacidad. | Se exige explícitamente cuando el efecto importa. |
| Identificación | No mezclar portador, contenido, límites y función. | Catálogos y conjuntos. | Introducir capacidades. | QR/Data Matrix sin inferir GS1, lectura o certificado. |
| Procesos de acabado | No agrupar operaciones físicas. | `finishing` 1.0.0. | Ampliar 1.1.0. | Cada proceso se evalúa sin operación invocable. |
| Herramienta/configuración | No combinar máximos. | String y revisión de snapshot. | Reutilizar. | Identificador local ligado a una configuración. |
| Procesamiento documental | No inferir semántica desde aceptación. | `document-processing` 1.0.0. | Ampliar 1.1.0. | Reconocer/preservar/interpretar separados. |
| Magnitud de error | No confundirla con resolución o incertidumbre. | Cantidad de longitud. | Reutilizar con límite documental. | Cota solo con métrica/condiciones declaradas. |
| Unidades | No ampliar v1 silenciosamente. | Unidades actuales. | Excluir evolución. | UCUM requiere una decisión/versionado futuro. |

## Guía para Tórculo

1. Seleccionar fuera de CXP una configuración coherente; no componer máximos
   de modos distintos.
2. Cargar explícitamente `finishing` o `document-processing` 1.1.0 cuando los
   necesite y conservar el hash en sus documentos.
3. Publicar snapshots separados para posicionamiento, identificación, acabado
   y procesamiento documental; evaluar un catálogo por llamada.
4. Exigir soporte efectivo para detección, compensación y corte, y conservar
   `indeterminate` cuando falten datos.
5. Mantener en Tórculo geometría, herramientas, PDF, evidencia de producción y
   autorización de ejecución: una compatibilidad CXP no las reemplaza.
