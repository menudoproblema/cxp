# Cierre local de versión y publicación

Son cuatro estados distintos: implementado, candidata local comprobada,
autorizada para publicar y publicada verificada. Los gates solo acreditan los
dos primeros. Un commit, tag o upload requiere autorización separada; publicar
la librería no implica desplegar consumidores.

## Evidencia reproducible

`scripts/check.py` ejecuta los gates del checkout. `scripts/build_candidate.py`
construye wheel y sdist, comprueba metadatos con Twine y genera
`dist/<version>/build-manifest.json` (ahora `dist/4.0.0`). El manifiesto identifica revisión base,
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

Los artefactos y evidencias de rc1 se conservan donde estaban. No se reutilizan
para acreditar 4.0.0 ni se sobrescriben al preparar la versión nueva.

`scripts/verify_artifacts.py` comprueba que fuente y artefactos siguen coincidiendo,
instala ambos en entornos nuevos, comprueba su origen y recursos, ejecuta toda la
suite y los ejemplos empaquetados. Primero comprueba la instalación base sin
dependencias de intercambio y el error claro al intentar usarlo; después instala
el extra para comprobar el contrato completo. Las pruebas se copian del sdist; no se copia
`src`. Se conserva un informe por Python 3.12/3.13/3.14 y política msgspec
`minimum` (0.20.0) / `latest` (la resolución actual menor que 1).

`scripts/release_evidence.py` exige los doce resultados (seis combinaciones por
dos artefactos) y rechaza evidencia stale o incompleta. Genera
`dist/4.0.0/release-evidence.json`; ese fichero contiene los hashes exactos de la
candidata realmente comprobada. Los informes son locales y no se incluyen en
el sdist para evitar ciclos de evidencia que se hashea a sí misma.

Modificar cualquier fuente después de la construcción obliga a reconstruir y
repetir los controles. La CI también prueba fuentes y artefactos en las seis
combinaciones. Un verde local no se presenta como un run remoto de GitHub.

## Licencias y límites

CXP conserva MIT. El código nuevo es propio; rfc8785 se usa como dependencia,
no como código copiado. La base depende de msgspec (BSD-3-Clause). El extra
`exchange` añade jsonschema (MIT), referencing (MIT) y rfc8785 (Apache-2.0).
Los esquemas, vectores y catálogos propios se
distribuyen bajo MIT. `py.typed` y LICENSE se comprueban en el wheel.
La evidencia conserva los metadatos de licencia de dependencias de runtime,
incluidas transitivas y las del extra probado; no sustituye una revisión jurídica cuando corresponda.
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

Tras una futura publicación autorizada se instalará desde el destino real en un
entorno limpio y se repetirán smoke y comprobaciones de recursos. Un upload
exitoso por sí solo no completa ese último estado.

## Autorización de 4.0.0

El mantenedor ha solicitado expresamente crear la etiqueta `v4.0.0`, recibir
los comandos de push y publicar en PyPI. Esto incluye el commit necesario para
que la etiqueta señale las fuentes de la entrega. No se ejecuta el push de Git
ni se modifican código, restricciones o locks de consumidores.

La comprobación previa identifica dos políticas distintas: Cosecha mantiene
`cxp~=3.1.0` y no adoptará esta major automáticamente; Mongoeco declara
`cxp>=3.0.0` y sí permite resolver 4.0.0. Antes del upload se comprueban sus
integraciones con el artefacto exacto, sin cambiar esas políticas ni presentar
las sondas como una migración o despliegue.

`dist/4.0.0/release-evidence.json` conserva exclusivamente la acreditación
técnica previa. La autorización y el resultado real de publicación se registran
en `dist/4.0.0/publication-evidence.json`, con el commit y tag, hashes de PyPI
y comprobaciones de instalación desde el índice. No se reconstruyen artefactos
entre su acreditación, el upload y la comprobación posterior.
