# Catálogo de WSGI Application

> Estado actual: catálogo provisional. Modela el contrato interoperable de aplicaciones WSGI y podrá ajustarse según aparezcan consumers reales.

## Interfaz
Este catálogo define el vocabulario canónico de capabilities para `application/wsgi`.

## Capabilities Canónicas
- `http`: contrato HTTP síncrono WSGI con `request.environ.inspect`, `request.body.read`, `response.start`, `response.body.iterable` y `response.body.write`.
- `file_wrapper`: optimización opcional mediante `response.body.file_wrapper`.

## Tiers de Conformidad
### Core
- `http`

### Optimized
- `http`
- `file_wrapper`

## Metadata Esperada
- `http`: `specVersion`, `urlSchemes`, `mountAware`, `expectContinue`, `concurrencyHints`

## Perfiles Reutilizables
- `wsgi-core`: exige la surface completa de `http` y su metadata.
- `wsgi-file-optimized`: extiende `wsgi-core` y exige `file_wrapper`.

## Compatibilidad
`application/wsgi` satisface `application/http`.
