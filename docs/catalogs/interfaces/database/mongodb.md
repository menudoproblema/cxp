# Catálogo de MongoDB

> Estado actual: catálogo provisional. Sirve como vocabulario base para pruebas de interoperabilidad y podrá ajustarse cuando se cierre la integración real entre consumidores y providers.

## Interfaz
Este catálogo define el vocabulario canónico de capabilities para la interfaz `database/mongodb`.

## Tiers de Conformidad
### Núcleo
- `read`: operaciones básicas de consulta como `find` y `count`.
- `write`: operaciones de inserción, actualización y borrado.
- `aggregation`: soporte para el framework de agregación.

### Search
- `search`: soporte para búsquedas textuales de estilo `$search`.
- `vector_search`: hay disponible búsqueda por similitud semántica.

### Platform
- `transactions`: operaciones atómicas multi-documento.
- `change_streams`: observación de cambios en tiempo real.
- `collation`: comparación y ordenación sensibles a reglas de collation.
- `persistence`: los datos sobreviven a la vida del proceso.
- `topology_discovery`: el provider puede describir topología y salud de nodos.

## Regla de Nombres
Los providers deberían usar estos nombres exactos cuando quieran una negociación interoperable a través de la interfaz `database/mongodb`.

## Procedencia
Este vocabulario toma como referencia:

- la superficie de runtime que Cosecha trata como interoperable para `database/mongodb`;
- la introspección pública que Mongoeco2 ya expone en change streams, search/vector search, collation y SDAM.
