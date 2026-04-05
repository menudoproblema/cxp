# Protocolo de Capacidades

## Capability
En CXP, una capability es una unidad funcional con nombre publicada por un provider.

Cada capability tiene dos dimensiones:

- `name`: el identificador canónico usado durante la negociación.
- `metadata`: detalle técnico opcional aportado por el provider. En runtime se trata como un valor opaco para no romper serialización con `msgspec`, pero el uso esperado es un `dict` simple o una estructura tipada que luego se convierta con `get_metadata()`.

## Capability Matrix
`CapabilityMatrix` es el inventario completo ofrecido por un provider durante el handshake.

La API actual incluye dos helpers útiles:

- `Capability.get_metadata(struct_type)`: convierte la metadata al tipo pedido usando `msgspec.convert`.
- `CapabilityMatrix.from_names(names)`: crea una matriz rápida a partir de nombres simples.

```python
from cxp import Capability, CapabilityMatrix

matrix = CapabilityMatrix.from_names(["read", "write"])

capability = Capability(
    name="read",
    metadata={"max_pool_size": 20},
)
```

## Superficie de Negociación vs Superficie de Descripción
`Capability` y `CapabilityMatrix` forman la superficie mínima de negociación del protocolo.

Su función es responder a la pregunta: "¿qué capabilities ofrece este provider para esta interfaz?".

Cuando un integrador necesita un modelo más rico, CXP ofrece una capa opcional de descriptores:

- `CapabilityDescriptor`
- `ComponentCapabilitySnapshot`
- `ComponentDependencyRule`

Esa capa no sustituye al handshake ni amplía `CapabilityMatrix`. Sirve para describir:

- nivel de soporte de cada capability;
- operaciones tipadas asociadas;
- atributos y metadata opcional;
- relaciones declarativas entre componentes.

La negociación sigue usando únicamente `CapabilityMatrix`.

Durante el handshake, CXP distingue tres estados:

- `accepted`: se cumplen las required capabilities.
- `degraded`: se cumplen las required, pero faltan capabilities marcadas como `optional_capabilities`.
- `rejected`: falla la versión de protocolo, la interfaz o alguna required capability.

`HandshakeResponse` también expone campos estructurados para no depender del parseo de `reason`:

- `missing_required_capabilities`
- `missing_optional_capabilities`

El request también debe ser coherente: una misma capability no puede aparecer a la vez en `required_capabilities` y `optional_capabilities`.

Si un integrador necesita persistir o diagnosticar un estado más rico del componente, debe usar la superficie de snapshots de capacidades documentada en `protocol/descriptors.md`, no ampliar el handshake.

Cuando ambos lados negocian interfaces pertenecientes a catálogos registrados,
el handshake también puede aceptar interfaces concretas que satisfacen una
familia abstracta. Por ejemplo, un provider `application/asgi` puede aceptar
un request para `application/http`.

## Relación con los Catálogos
El protocolo solo transporta capabilities. No define por sí mismo el significado de cada nombre de capability.

Ese significado pertenece a catálogos como `database/mongodb` o `transport/http`. Un catálogo define qué nombres son canónicos para una interfaz dada, qué tiers de conformidad implican y, cuando haga falta, qué esquema de metadata espera cada capability.

La misma autoridad semántica del catálogo puede reutilizarse sobre la capa rica:

- `validate_capability_descriptors(...)`
- `validate_component_snapshot(...)`
- `is_component_snapshot_compliant(...)`

Y sobre la propia `CapabilityMatrix`:

- `validate_capability_matrix(...)`
- `invalid_capability_metadata(...)`
- `is_capability_matrix_compliant(...)`

De ese modo un orquestador puede validar descriptores ricos sin convertir el catálogo en parte del handshake.

Si el integrador quiere que el handshake quede validado automáticamente contra el catálogo canónico de la interfaz, también puede usar:

- `negotiate_with_provider_catalog(...)`
- `negotiate_with_async_provider_catalog(...)`

Esos helpers ejecutan el handshake mínimo y luego validan la `CapabilityMatrix` resultante contra el catálogo, incluyendo metadata y tiers cuando aplique.
