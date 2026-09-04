# Integración del intercambio enriquecido

Instalamos `cxp[exchange]` y usamos `cxp.exchange` explícitamente. El paquete base
solo requiere msgspec y no importa ni instala los validadores del intercambio.
Si falta el extra, el import explica cómo instalarlo. La API heredada permanece
disponible; no se activa el protocolo nuevo cambiando una versión en su handshake.

## Documentos offline

```python
from cxp.exchange import (
    CatalogStore,
    evaluate_requirements_detailed,
    load_document,
    load_reference_catalog,
)

catalog = load_reference_catalog("physical-printing", version="1.1.0")
store = CatalogStore([catalog])
# Los tres argumentos son bytes recibidos por nuestra aplicación.
snapshot = load_document(snapshot_bytes, expected_type="cxp.snapshot")
requirements = load_document(requirements_bytes, expected_type="cxp.requirements")
context = load_document(context_bytes, expected_type="cxp.context")
result = evaluate_requirements_detailed(
    snapshot, requirements, context, catalogs=store
)
print(result.verdict, result.findings)
output_bytes = result.document.to_bytes()
```

Para producir datos propios usamos `Document(contenido, expected_type=...)` y
`catalog_reference(catalog)`. El contenido es JSON nativo; los esquemas están
disponibles mediante `document_schema()` y como recursos del paquete. No hay
que reproducir el modelo Python para implementar un lector en otro lenguaje.

`Document` valida estructura y semántica intrínseca. Los tipos de propiedades,
operaciones y referencias se comprueban con `CatalogStore.validate_snapshot`
y `validate_requirements`, o automáticamente al evaluar. Un JSON Schema
estructural correcto no basta para asegurar un documento evaluable.

El registro posee una tupla de documentos inmutables. Para cambiarlo construimos
otro; no se consulta el registro global heredado ni se descargan catálogos.
`payload` y `as_dict()` devuelven copias. `to_bytes()` devuelve bytes canónicos;
`sha256` identifica su contenido, no su firma ni la veracidad del proveedor.
`list_reference_catalogs()` permite descubrir todas las versiones empaquetadas.
Omitir versión en `load_reference_catalog()` conserva el catálogo 1.0.0; nunca
significa seleccionar automáticamente la versión más reciente.

`quantity_from_input("2.5", "cm")` devuelve exactamente `25 mm`. Es una ayuda
de entrada: `cm` y `m` siguen sin ser unidades válidas dentro del documento v1.

## Integración en vivo

1. El emisor crea un `cxp.exchange_request` con `protocol_version: 2` y todas
   las familias requeridas en `formats`, cada una con `spec_versions: [1]`.
2. El receptor usa `negotiate_exchange(request)` o implementa la misma semántica.
   Puede restringir sus familias soportadas; no anunciar formatos inexistentes.
3. Ambos comprueban la respuesta mediante `ExchangeAgreement(request, response)`.
4. `agreement.encode(document)` y `agreement.decode(bytes, expected_type=...)`
   impiden intercambiar una familia que no se negoció.

CXP no proporciona transporte, autenticación ni una confirmación remota de que
un receptor está usando el lector correcto. El adaptador debe aplicar el acuerdo
en ambos extremos. Un peer exclusivamente v1 no entra en este flujo; un rechazo
no autoriza convertir requisitos enriquecidos a nombres de capacidades.

## Interpretar el resultado

`compatible` solo expresa cumplimiento de requisitos declarados y entendidos en
el contexto solicitado. No reserva capacidad, comprueba consumibles ni autoriza
producir. Disponibilidad y conectividad son dimensiones separadas que el
consumidor puede usar para una decisión operativa posterior.

`incompatible` requiere un incumplimiento conocido. `indeterminate` informa falta
de datos o contexto no aplicable/caduco. Los documentos inválidos/no comprendidos
generan excepciones, no un cuarto veredicto ni una denegación encubierta.

Los findings conservan el orden de las hojas e incluyen las rutas de requisito
y snapshot; `inputs` fija las cuatro huellas. Para reproducir una decisión hay
que guardar esos documentos exactos y la versión semántica del evaluador.

El ejemplo de regresión sigue disponible en `python -m cxp.exchange.examples`.
El recorrido pedagógico, autocontenido y sin maquinaria se ejecuta con
`python -m cxp.exchange.tutorial` o `python examples/document_exchange.py`.
La [CLI](../cli.md) proyecta las mismas validaciones y evaluaciones para scripts.
