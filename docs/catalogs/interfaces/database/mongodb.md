# Catalogo de MongoDB

> Estado actual: catalogo provisional. El vocabulario ya es util para interoperabilidad, pero sigue siendo revisable si cambian los consumidores reales.

## Interfaz
Este catalogo define el vocabulario canonico de capabilities para la interfaz `database/mongodb`.

## Capabilities Canonicas
- `read`: lectura documental y de conjuntos mediante `find`, `find_one`, `count_documents`, `estimated_document_count` y `distinct`.
- `write`: escritura documental mediante `insert_one`, `insert_many`, `update_one`, `update_many`, `replace_one`, `delete_one`, `delete_many` y `bulk_write`.
- `aggregation`: soporte para `aggregate`.
- `transactions`: sesiones y transacciones con `start_session` y `with_transaction`.
- `change_streams`: observacion reactiva mediante `watch`.
- `search`: pipelines de agregacion que comienzan con `$search`.
- `vector_search`: pipelines de agregacion que comienzan con `$vectorSearch`.
- `collation`: reglas de comparacion y ordenacion por collation.
- `persistence`: persistencia material mas alla del proceso.
- `topology_discovery`: descripcion de topologia y estado operativo del cluster.

## Tiers de Conformidad
### Core
- `read`
- `write`
- `aggregation`

`core` es el minimo interoperable. Los tiers superiores lo extienden y no lo sustituyen.

### Search
- `read`
- `write`
- `aggregation`
- `search`
- `vector_search`

`search` exige `aggregation` porque ambas capabilities se expresan como pipelines `aggregate` con stages iniciales especializados.

### Platform
- `read`
- `write`
- `aggregation`
- `transactions`
- `change_streams`
- `collation`
- `persistence`
- `topology_discovery`

`platform` modela un runtime MongoDB operativo y por eso tambien incluye la base `core`.

## Metadata Esperada
Las capabilities enriquecidas validan metadata estructurada:

- `aggregation`: `supportedStages` y, opcionalmente, `supportedExpressionOperators`, `supportedGroupAccumulators` y `supportedWindowAccumulators`.
- `search`: `operators` y `aggregateStage="$search"`.
- `vector_search`: `similarities` y `aggregateStage="$vectorSearch"`.
- `collation`: objetos `backend` y `capabilities`.
- `persistence`: `persistent` y `storageEngine`.
- `topology_discovery`: `topologyType`, `serverCount` y `sdam`.

## Telemetria Canonica
La telemetria de `database/mongodb` se declara por capability y no se limita a
una unica señal generica compartida.

Las reglas practicas son estas:

- `read` y `write` comparten `db.client.operation`, `db.client.operation.duration`
  y `db.client.operation.completed`.
- `aggregation` usa señales propias: `db.client.aggregate`,
  `db.client.aggregate.duration` y `db.client.aggregate.completed`.
- `search` usa señales propias: `db.client.search`,
  `db.client.search.duration` y `db.client.search.completed`.
- `vector_search` usa señales propias: `db.client.vector_search`,
  `db.client.vector_search.duration` y `db.client.vector_search.completed`.
- `transactions`, `change_streams`, `collation`, `persistence` y
  `topology_discovery` declaran eventos o spans especificos del dominio.

Los campos comunes minimos para operaciones documentales son:

- `db.system.name`
- `db.operation.name`
- `db.namespace.name`
- `db.operation.outcome`

Y las capabilities especializadas exigen campos extra:

- `aggregation`: `db.pipeline.stage.count`
- `search`: `db.pipeline.stage.name` y `db.search.operator`
- `vector_search`: `db.pipeline.stage.name` y `db.vector_search.similarity`
- `change_streams`: `db.change.operation_type`
- `collation`: `db.collation.locale`
- `persistence`: `db.persistence.storage_engine` y `db.persistence.persistent`
- `topology_discovery`: `db.topology.type` y `db.topology.server.count`

## Perfiles Reutilizables
- `mongodb-core`: exige las operaciones completas de `read`, `write` y `aggregation`.
- `mongodb-search`: extiende `mongodb-core` y exige `search` y `vector_search`.
- `mongodb-platform`: extiende `mongodb-core` y exige `transactions`, `change_streams`, `collation`, `persistence` y `topology_discovery`.
- `mongodb-aggregate-rich`: perfil puntual para tests que necesitan metadata rica de agregacion.

## Regla de Nombres
Los providers deben usar estos nombres exactos cuando quieran una negociacion interoperable a traves de `database/mongodb`.

## Procedencia
Este vocabulario toma como referencia:

- la superficie publica interoperable de runtimes MongoDB-like que exponen la
  interfaz `database/mongodb`;
- la introspeccion publica que Mongoeco y otros providers pueden proyectar en
  change streams, search, vector search, collation, persistence y SDAM.
