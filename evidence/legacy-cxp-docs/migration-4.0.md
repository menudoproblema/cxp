# Migración de 3.1 a 4.0

La entrega `4.0.0`, revisada desde rc1, es una major con APIs aditivas y
validación más estricta. Su publicación no actualiza ni autoriza por sí sola
el despliegue de aplicaciones consumidoras.

## Qué se conserva

El inventario `tests/fixtures/legacy-3.1-api.json` procede de la revisión
`6b5b555cbaf39c89cbe1ae0ca5955a88b049f8cf` (MIT): 57 superficies `__all__` y
102 definiciones Struct. Las pruebas verifican que no desaparecen exports ni
campos anteriores. Los vectores wire complementan ese inventario, sin prometer
que una muestra finita demuestra compatibilidad universal.

Se conservan handshake v1, clases de identidad/matrices/descriptores, enums,
providers sync/async, telemetría, registro global y fachadas `get_catalog` y
`register_catalog`. `CapabilityProfile` sigue validándose al construirse y
lanzando `ValueError` por catálogo no registrado o perfil inválido.
Los perfiles legacy siguen admitiendo noop conforme a sus reglas anteriores.

## Cambios observables y actuación necesaria

| Cambio | Actuación del consumidor |
| --- | --- |
| Metadata Struct se revalida igual que un diccionario. | Corregir objetos construidos o mutados con tipos/restricciones inválidos. |
| Duplicados de capacidades, operaciones dentro de una capacidad, atributos, tiers y requisitos se rechazan. | Asignar identidad única; no confiar en first-wins/last-wins. |
| Tiers con capacidades inexistentes, timeouts no positivos/no finitos y schemas inválidos se rechazan. | Revisar definiciones antes de registrarlas. |
| Binding contradice un result_type explícito del catálogo. | Corregir la declaración; una omisión legacy sigue sin inventar una contradicción. |
| Contratos compuestos/transitivos/diamante incompatibles se rechazan atómicamente. | Alinear schemas y tipos con los padres; no usar reemplazo para invalidar descendientes. |
| Los contratos metadata superpuestos de catálogos legacy usan la misma clase Struct. | Compartir la clase contractual; dos clases de forma parecida no acreditan el mismo contrato. |
| Resultados de validación añaden `diagnostics`. | Revisar decoders con campos cerrados y snapshots JSON exactos; los campos anteriores siguen disponibles. |
| Web Push cambia `send.result_type`: `push.result` → `notification.result`. | Actualizar bindings explícitos; `PushResult` no cambia. La corrección alinea el padre abstracto. |
| Se fija un mínimo de msgspec; el intercambio es opcional. | El paquete base solo necesita Python>=3.12 y msgspec>=0.20.0,<1. Para documentos instalar `cxp[exchange]`, que añade jsonschema>=4.23,<5, referencing>=0.35,<1 y rfc8785>=0.1.4,<1. |
| Los ejemplos usan el paquete instalado. | Instalar CXP o `pip install -e '.[dev]'` antes de ejecutarlos. |

Los mensajes antiguos se mantienen para sus casos originales; los nuevos
diagnósticos usan códigos/rutas. No se recomienda depender del texto completo
de las excepciones como protocolo.

La validación de definiciones se memoriza por instancia únicamente cuando el
árbol está compuesto por los tipos congelados propios y valores inmutables.
Contenedores mutables y subclases externas se revalidan; los metadatos de cada
snapshot siempre se revalidan. La caché no se serializa ni añade campos públicos.

Al pasar de rc1 a 4.0 se precisan diagnósticos: `step_requires_origin`,
`origin_requires_step` y `duplicate_set_value`, con rutas al campo concreto.
Un entero JSON inseguro da `unsafe_integer` antes de cualquier conversión a
float, igual que su representación entera en Python.

## Matriz de lectores

| Emisor | Receptor | Resultado |
| --- | --- | --- |
| DTO 3.1 | API legacy 4.0 | Formas y handshake conservados; valida con endurecimientos documentados. |
| DTO legacy 4.0 preservado | Decoder 3.1 equivalente | Wire de las formas congeladas conservado. Nuevos campos de diagnósticos requieren revisar decoders cerrados. |
| Documento v1 | Lector nuevo explícito/acuerdo v2 | Validación de familia, versión, forma, extensiones y referencias. |
| DTO legacy | Lector nuevo | Rechazo: no hay envolvente del intercambio. |
| Documento nuevo | Decoder legacy de snapshot/handshake | Rechazo por campos obligatorios ausentes en los casos probados. |
| Documento nuevo | Decoder legacy de matriz | Puede aceptarlo como matriz vacía. No es un canal seguro de transición. |
| Emisor exige v2 | Peer exclusivamente v1 | Rechazo de negociación; nunca eliminación silenciosa de requisitos. |

No se ha modificado 3.1 retroactivamente. La seguridad exige selección explícita
del formato en la integración, no simplemente añadir `spec_version` a un DTO.
No se proporciona downgrade automático ni adaptación universal de catálogos.

## Ruta de adopción y vuelta atrás

1. Mantener consumidores existentes fijados a su versión/familia probada.
2. Probar la candidata exacta y sus dependencias en cada consumidor; revisar
   la tabla de rupturas, catálogos privados y todos los bindings explícitos.
3. Incorporar el intercambio por un canal nuevo, con lector o acuerdo explícito.
4. Conservar snapshots y requisitos originales junto con sus huellas y contexto.

La vuelta atrás reinstala un artefacto conocido y vuelve al canal legacy. No
reescribe artefactos publicados ni reinterpreta documentos nuevos como antiguos.
Se conservan ambos formatos y los artefactos previos mientras exista esa necesidad.
Este cambio no modifica dependencias ni código de aplicaciones consumidoras.
