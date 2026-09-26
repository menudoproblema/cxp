# Compliance Bridge

## Propósito
El Compliance Bridge convierte una combinación de:

- `HandshakeResponse`
- `CapabilityMatrix`
- catálogo CXP
- tier opcional

en una decisión operativa estructurada para un orquestador.

Su objetivo no es ampliar el núcleo del protocolo. El handshake sigue
transportando identidad, versión y capabilities negociables. El bridge vive por
encima de ese contrato mínimo y reutiliza la validación ya existente del
catálogo actual.

## Qué Añade
La API pública expone:

- `CatalogComplianceReport`
- `NegotiatedCatalogDecision`
- `evaluate_capability_matrix_against_catalog(...)`
- `evaluate_handshake_response_against_catalog(...)`
- `negotiate_with_provider_catalog_report(...)`
- `negotiate_with_async_provider_catalog_report(...)`

`CatalogComplianceReport` resume:

- si el provider cumple o no (`compliant`);
- qué interfaz pedía el catálogo (`catalog_interface`);
- qué interfaz ofrece el provider (`offered_interface`);
- qué tier se exigía, si aplica (`required_tier`);
- un resumen corto (`reason`);
- el detalle completo (`messages`);
- y la validación estructurada original (`validation`).

## Diferencia Entre Helpers
Hay tres niveles distintos:

1. Handshake mínimo:
   - `negotiate_with_provider(...)`
   - `negotiate_with_async_provider(...)`
   - solo negocian protocolo, interfaz y capabilities pedidas por el cliente.

2. Helper estricto:
   - `negotiate_with_provider_catalog(...)`
   - `negotiate_with_async_provider_catalog(...)`
   - si el catálogo no se cumple, convierten la respuesta en `rejected`.

3. Helper de decisión:
   - `negotiate_with_provider_catalog_report(...)`
   - `negotiate_with_async_provider_catalog_report(...)`
   - preservan la respuesta del handshake y devuelven además un informe de
     cumplimiento para que el orquestador decida.

## Adaptación del Catálogo Actual
El bridge no redefine la semántica de `CapabilityCatalog`.

Reutiliza directamente:

- `catalog_satisfies_interface(...)`
- `validate_capability_matrix(...)`
- la jerarquía ya registrada entre catálogos abstractos y concretos

Cuando el catálogo pedido es abstracto pero el provider ofrece una interfaz
concreta registrada que satisface esa familia, el bridge valida la matrix contra
el catálogo concreto del provider. Eso permite tomar decisiones útiles en
runtime sin meter lógica paralela dentro del catálogo base.

## Ejemplo Síncrono
```python
from cxp import (
    MONGODB_CATALOG,
    HandshakeRequest,
    negotiate_with_provider_catalog_report,
)

decision = negotiate_with_provider_catalog_report(
    request=HandshakeRequest(
        client_identity=client_identity,
        required_capabilities=("read",),
    ),
    provider=provider,
    catalog=MONGODB_CATALOG,
    required_tier="core",
)

if decision.compliance.compliant:
    response = decision.response
else:
    print(decision.compliance.reason)
```

## Ejemplo Asíncrono
```python
from cxp import (
    MONGODB_CATALOG,
    HandshakeRequest,
    negotiate_with_async_provider_catalog_report,
)

decision = await negotiate_with_async_provider_catalog_report(
    request=HandshakeRequest(
        client_identity=client_identity,
        required_capabilities=("read",),
    ),
    provider=async_provider,
    catalog=MONGODB_CATALOG,
)

if not decision.compliance.compliant:
    for message in decision.compliance.messages:
        print(message)
```

## Lo Que No Hace
El Compliance Bridge v1 no:

- modifica `HandshakeResponse`;
- convierte `input_schema`, `result_schema`, `idempotent` o `timeout_seconds`
  en semántica global del protocolo;
- sustituye snapshots ricos o validación por perfiles;
- impone una nueva taxonomía universal de cumplimiento.

Es un pegamento operativo y explícito entre handshake y catálogos, no una
segunda arquitectura dentro de CXP.
