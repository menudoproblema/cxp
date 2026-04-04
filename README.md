# CXP: Capability Exchange Protocol

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.12+-green)

**CXP** is a semantic interoperability protocol for software components. It allows libraries, runtimes, and services to publish their capabilities and telemetry through a small shared contract.

## Why CXP?
Modern components are often black boxes. CXP gives them two explicit surfaces:

- capabilities, so an orchestrator can understand what a component can do;
- telemetry, so an orchestrator can observe what is happening at runtime.

That makes tools such as **Cosecha** or AI agents operate against a shared semantic contract instead of provider-specific assumptions.

## Design Goals
- **Small Core**: keep the protocol surface narrow and stable.
- **Data-Oriented**: exchange typed data, not framework-specific objects.
- **High-Performance**: use `msgspec` for compact structured contracts.
- **Agent-Ready**: support orchestration layers, MCP servers, and automation tooling.

## Installation
```bash
pip install cxp
```

## What CXP Includes
- A small handshake contract based on `ComponentIdentity`, `CapabilityMatrix`, and `HandshakeRequest`.
- Sync and async provider protocols for capabilities, telemetry, and capability snapshots.
- First-party catalogs for canonical interfaces such as `database/mongodb`, `transport/http`, `application/http`, and `execution/engine`.
- A richer descriptor layer for component snapshots, typed operations, and declarative dependencies.

## Quick Start
```python
from cxp import (
    Capability,
    CapabilityMatrix,
    ComponentIdentity,
    HandshakeRequest,
    get_catalog,
    negotiate_with_provider_catalog,
)

# Resolve the standard catalog for the interface
catalog = get_catalog("database/mongodb")
assert catalog is not None

# Build the orchestrator request
request = HandshakeRequest(
    client_identity=ComponentIdentity(
        interface="database/mongodb",
        provider="cosecha",
        version="1.0.0",
    ),
    required_capabilities=("read",),
)

class MongoProvider:
    def cxp_identity(self) -> ComponentIdentity:
        return ComponentIdentity(
            interface="database/mongodb",
            provider="mongoeco2",
            version="3.0.0",
        )

    def cxp_capabilities(self) -> CapabilityMatrix:
        return CapabilityMatrix(
            capabilities=(
                Capability(name="read"),
                Capability(name="write"),
            )
        )


response = negotiate_with_provider_catalog(request, MongoProvider(), catalog)

assert response.status == "accepted"
assert catalog.is_capability_matrix_compliant(response.offered_capabilities)
```

If a handshake is degraded or rejected because capabilities are missing, the response also exposes them structurally through:

- `missing_required_capabilities`
- `missing_optional_capabilities`

A capability must not appear in both `required_capabilities` and `optional_capabilities` in the same request.

## Practical Examples
### Sync provider
Use a sync provider when identity, capabilities, or telemetry can be produced without async I/O:

```python
from cxp import (
    Capability,
    CapabilityMatrix,
    ComponentIdentity,
    HandshakeRequest,
    TelemetryBuffer,
    TelemetryContext,
    negotiate_with_provider,
    collect_provider_telemetry,
)


class MongoProvider:
    def cxp_identity(self) -> ComponentIdentity:
        return ComponentIdentity(
            interface="database/mongodb",
            provider="mongoeco2",
            version="3.0.0",
        )

    def cxp_capabilities(self) -> CapabilityMatrix:
        return CapabilityMatrix(
            capabilities=(
                Capability(name="read"),
                Capability(name="write"),
            )
        )

    def cxp_telemetry_provider_id(self) -> str:
        return "mongoeco2"

    def cxp_telemetry_snapshot(self):
        context = TelemetryContext(trace_id="trace-1")
        buffer = TelemetryBuffer(provider_id="mongoeco2")
        buffer.record_event(context.create_event("command_succeeded"))
        buffer.record_metric("ops", 1)
        return buffer.flush()


provider = MongoProvider()
request = HandshakeRequest(
    client_identity=ComponentIdentity(
        interface="database/mongodb",
        provider="cosecha",
        version="1.0.0",
    ),
    required_capabilities=("read",),
    optional_capabilities=("transactions",),
)

response = negotiate_with_provider(request, provider)
telemetry = collect_provider_telemetry(provider)
```

### Async provider
Use an async provider when collecting capabilities or telemetry requires I/O:

```python
from cxp import (
    Capability,
    CapabilityMatrix,
    ComponentIdentity,
    HandshakeRequest,
    negotiate_with_async_provider,
)


class AsyncMongoProvider:
    async def cxp_identity(self) -> ComponentIdentity:
        return ComponentIdentity(
            interface="database/mongodb",
            provider="mongoeco2",
            version="3.0.0",
        )

    async def cxp_capabilities(self) -> CapabilityMatrix:
        return CapabilityMatrix(
            capabilities=(
                Capability(name="read"),
                Capability(name="write"),
            )
        )


request = HandshakeRequest(
    client_identity=ComponentIdentity(
        interface="database/mongodb",
        provider="cosecha",
        version="1.0.0",
    ),
    required_capabilities=("read",),
)

# response = await negotiate_with_async_provider(request, AsyncMongoProvider())
```

### Rich component snapshots
When a flat capability list is not enough, a provider can publish a `ComponentCapabilitySnapshot` with support levels and typed operations:

```python
from cxp import (
    CapabilityDescriptor,
    CapabilityOperationBinding,
    ComponentCapabilitySnapshot,
    ComponentIdentity,
)


snapshot = ComponentCapabilitySnapshot(
    component_name="gherkin",
    identity=ComponentIdentity(
        interface="execution/engine",
        provider="gherkin",
        version="1.0.0",
    ),
    capabilities=(
        CapabilityDescriptor(
            name="planning",
            level="supported",
            operations=(
                CapabilityOperationBinding(
                    operation_name="plan.analyze",
                    result_type="plan.analyzed",
                ),
                CapabilityOperationBinding(
                    operation_name="plan.explain",
                    result_type="plan.explained",
                ),
            ),
        ),
    ),
)

matrix = snapshot.as_negotiated_capability_matrix()
```

### Telemetry streams
Providers may publish telemetry continuously instead of only returning a single snapshot:

```python
from cxp import stream_provider_telemetry_async


async def consume(provider) -> None:
    async for snapshot in stream_provider_telemetry_async(provider):
        print(snapshot.status, len(snapshot.events), len(snapshot.metrics))
```

### Bounded telemetry buffers
If the provider may emit large bursts of telemetry, you can bound the buffer and choose an overflow policy:

```python
from cxp import TelemetryBuffer

buffer = TelemetryBuffer(
    provider_id="mongoeco2",
    max_items=1000,
    overflow_policy="drop_oldest",
)
```

`TelemetrySnapshot.dropped_items` reports how many items were discarded since the previous `flush()`.
If you keep the default `overflow_policy="raise"`, the buffer raises `TelemetryBufferOverflow`.

## Catalogs and Validation
Catalogs are the semantic authority for a given interface. They define canonical capability names, optional typed operations, and optional metadata schemas.

```python
from cxp import Capability, CapabilityMatrix, get_catalog

catalog = get_catalog("execution/engine")
assert catalog is not None

matrix = CapabilityMatrix(
    capabilities=(
        Capability(name="run"),
        Capability(name="planning"),
    )
)

validation = catalog.validate_capability_matrix(
    matrix,
    required_tier="core",
)

if not validation.is_valid():
    print(validation.messages())
```

For richer integrations, the same catalog can validate component snapshots with:

- `validate_component_snapshot(...)`
- `is_component_snapshot_compliant(...)`

## Repository Examples
The repository includes runnable examples:

- [`examples/sync_provider.py`](examples/sync_provider.py)
- [`examples/async_provider.py`](examples/async_provider.py)
- [`examples/async_telemetry_stream.py`](examples/async_telemetry_stream.py)
- [`examples/component_descriptors.py`](examples/component_descriptors.py)

You can run them directly from the repository root:

```bash
python examples/sync_provider.py
python examples/async_provider.py
python examples/async_telemetry_stream.py
python examples/component_descriptors.py
```

## Documentation
See [docs/index.md](docs/index.md) for the full documentation set:

- protocol overview and boundaries;
- integration guidance;
- capability, descriptor, and telemetry contracts;
- first-party catalogs and canonical interfaces.

## License
MIT
