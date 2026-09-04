# Cierre local de versión y publicación

Son cuatro estados distintos: implementado, candidata local comprobada,
autorizada para publicar y publicada verificada. Los gates solo acreditan los
dos primeros. Un commit, tag o upload requiere autorización separada; publicar
la librería no implica desplegar consumidores.

## Evidencia reproducible

`scripts/check.py` ejecuta los gates del checkout. `scripts/build_candidate.py`
construye wheel y sdist, comprueba metadatos con Twine y genera
`dist/<version>/build-manifest.json` (para esta entrega, `dist/4.1.0`). El
manifiesto identifica revisión base,
huella del checkout (incluidos ficheros nuevos sin commit), epoch y SHA-256 de
cada artefacto. La huella excluye archivos ignorados por Git, como entornos,
cachés y `dist`; no se usa para afirmar que el árbol esté commiteado.

La construcción se realiza dos veces en directorios temporales independientes.
Normalizamos orden, propietarios, permisos e instantes de los miembros del tar
y la cabecera gzip, sin cambiar contenido ni fechas del checkout. Solo se
promueven los artefactos si coinciden byte a byte en ambas construcciones.
Se mantienen los hashes de los archivos exactos: no se sustituye esa garantía
por una comparación parcial del contenido extraído. La reproducibilidad se
comprueba con la misma cadena de herramientas; cambiar Python, herramientas o
dependencias exige volver a construir y validar.

Una candidata existente no se sobrescribe. El reemplazo explícito de una
candidata no publicada conserva el directorio anterior como backup recuperable;
una candidata registrada como publicada y verificada se rechaza siempre.

`scripts/verify_artifacts.py` comprueba que fuente y artefactos siguen
coincidiendo e instala ambos en tres entornos distintos: base, `exchange` y
`dev`. Ejecuta `pip check`, origen, recursos, CLI, tutorial y suite completa. Las
pruebas se copian del sdist; no se copia `src`. Se conserva un informe por Python
3.12/3.13/3.14 y política de dependencias `minimum` / `latest`. La primera fija
msgspec, jsonschema, referencing y rfc8785 en sus mínimos declarados; la segunda
resuelve la última combinación admitida.

`scripts/release_evidence.py` exige los doce resultados (seis combinaciones por
dos artefactos) y rechaza evidencia stale o incompleta. Genera
`dist/4.1.0/release-evidence.json`; ese fichero contiene los hashes exactos de la
candidata realmente comprobada. Los informes son locales y no se incluyen en
el sdist para evitar ciclos de evidencia que se hashea a sí misma.

Modificar cualquier fuente después de la construcción obliga a reconstruir y
repetir los controles. La CI construye una sola candidata, verifica esos mismos
bytes en las seis combinaciones Linux y ejecuta smoke del wheel en macOS y
Windows con rutas Unicode y espacios. Después reúne una única evidencia. Un
verde local no se presenta como un run remoto de GitHub.

## Licencias y límites

CXP conserva MIT. El código nuevo es propio; rfc8785 se usa como dependencia,
no como código copiado. La base depende de msgspec (BSD-3-Clause). El extra
`exchange` añade jsonschema (MIT), referencing (MIT) y rfc8785 (Apache-2.0).
Los esquemas, vectores y catálogos propios se
distribuyen bajo MIT. `py.typed` y LICENSE se comprueban en el wheel.
La evidencia conserva desde cada entorno aislado los metadatos de licencia de
dependencias de runtime, incluidas transitivas y las del extra probado; no
sustituye una revisión jurídica cuando corresponda.
Las herramientas de desarrollo no se empaquetan dentro del wheel de CXP.

Los catálogos están versionados, pero aún comparten una sola distribución.
La suite comprueba casos positivos, negativos y fronteras; no certifica
conformidad universal, soporte de maquinaria ni seguridad física.

## Puerta de publicación

Antes de publicar, el mantenedor debe identificar destino y autorizar los hashes
exactos. Además, cada owner de consumidores conocidos debe revisar:

- restricciones que excluyen 4.x o permiten majors sin límite;
- catálogos privados, overrides, decoders cerrados y bindings de Web Push;
- resolución de dependencias y pruebas de integración con la candidata;
- aislamiento de los canales legacy/nuevo y conservación de requisitos.

No se han cambiado ni acreditado esos consumidores desde esta tarea. La falta
de evidencia de integración es una condición explícita que impide publicar,
no una invitación a actualizar dependencias automáticamente.

La vuelta atrás usa los artefactos previos conocidos; no sobrescribe versiones
publicadas ni degrada documentos nuevos al formato viejo. Se conservan la
versión anterior, sus documentos y los hashes de la candidata.

La publicación se inicia manualmente indicando el run de CI y la versión. El job
protegido `pypi` comprueba commit y etiqueta, separa únicamente wheel y sdist ya
acreditados y usa Trusted Publishing mediante OIDC. No almacena un token largo
ni reconstruye código con permisos de publicación. PyPI genera attestations por
artefacto. Un job posterior contrasta hashes, descarga e instala desde PyPI y
genera `publication-evidence.json`; un upload exitoso por sí solo no completa el
estado publicado verificado.

Antes del primer uso, el mantenedor debe configurar en PyPI el Trusted Publisher
para el repositorio y `.github/workflows/publish.yml`, y proteger el environment
GitHub `pypi` con revisión manual. Es configuración externa comprobable, no una
garantía que este checkout pueda activar o afirmar por sí solo.

## Autorización de 4.0.0

El mantenedor ha solicitado expresamente crear la etiqueta `v4.0.0`, recibir
los comandos de push y publicar en PyPI. Esto incluye el commit necesario para
que la etiqueta señale las fuentes de la entrega. No se ejecuta el push de Git
ni se modifican código, restricciones o locks de consumidores.

En la comprobación previa a 4.0.0, Cosecha mantenía `cxp~=3.1.0` y
Mongoeco declaraba `cxp>=3.0.0`. Aquella evidencia conserva las políticas que
existían entonces. Tras la publicación, ambos consumidores se adaptaron y ahora
declaran `cxp>=4.0.0` sin límite superior. Esta situación vigente se vuelve a
comprobar antes de publicar 4.1.0; las sondas de integración no se presentan
como una migración ni como un despliegue.

`dist/4.0.0/release-evidence.json` conserva exclusivamente la acreditación
técnica previa. La autorización y el resultado real de publicación se registran
en `dist/4.0.0/publication-evidence.json`, con el commit y tag, hashes de PyPI
y comprobaciones de instalación desde el índice. No se reconstruyen artefactos
entre su acreditación, el upload y la comprobación posterior.
