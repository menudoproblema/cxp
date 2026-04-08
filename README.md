# CXP: Capability Exchange Protocol

![Version](https://img.shields.io/badge/version-3.0.0-blue)
![Python](https://img.shields.io/badge/python-3.12+-green)
[![CI](https://github.com/menudoproblema/cxp/actions/workflows/ci.yml/badge.svg)](https://github.com/menudoproblema/cxp/actions/workflows/ci.yml)

**CXP** is a semantic interoperability protocol for software components. It allows libraries, runtimes, and services to publish their capabilities and telemetry through a small shared contract.

## Why CXP?
Modern components are often black boxes. CXP gives them two explicit surfaces:

- **Capabilities**: So an orchestrator can understand what a component *can* do.
- **Telemetry**: So an orchestrator can observe what is happening at *runtime*.

CXP acts as a semantic bridge, allowing tools like AI agents, test runners, or orchestrators to operate against a shared contract instead of provider-specific assumptions.

## Design Goals
- **Small Core**: Keep the protocol surface narrow and stable.
- **High Fidelity**: Support expressive catalogs with metadata schemas, shared DTOs, and structured telemetry vocabularies.
- **Data-Oriented**: Exchange typed data using `msgspec` for high performance.
- **Omnichannel**: From cloud runtimes (ASGI/SQL) to industrial hardware (Zebra/Konica).

## Installation
```bash
pip install cxp
```

## Catalog Layers
CXP includes a growing suite of first-party catalogs organized in six logical layers:

Each layer exposes a family catalog (the abstract contract) plus one or more concrete catalogs that satisfy it.

1. **Computing**: `execution/plan-run`, `runtime/environment` (secrets/resources), and the `application/http` family with concrete `application/asgi`, `application/wsgi`, and `application/http-framework` catalogs.
2. **Persistence**: `database/sql`, `database/mongodb` (both satisfying `database/common`), `storage/blob`, `cache/key-value`.
3. **Communications**: `transport/http` (with the `transport/http-family` umbrella and `transport/websocket` sibling), `messaging/event-bus` (concrete: `messaging/nats`), and `notification/common` (concrete: `notification/web-push`, `notification/mobile-push`).
4. **Queueing**: `queue/task-engine` for background processing.
5. **Experience & Media**: `browser/automation` (concrete: `browser/playwright`), `media/video-streaming` (HLS/DASH).
6. **Industrial**: `printing/manager` (concrete: `printing/label` for Zebra/ZPL, `printing/production` for Konica Minolta).

For the full list of registered interfaces and operations, see [docs/catalogs/index.md](docs/catalogs/index.md).

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
catalog = get_catalog("database/sql")
assert catalog is not None

# Build the orchestrator request
request = HandshakeRequest(
    client_identity=ComponentIdentity(
        interface="database/sql",
        provider="my-orchestrator",
        version="1.0.0",
    ),
    required_capabilities=("transactions",),
)

# Negotiate with a provider
# response = negotiate_with_provider_catalog(request, my_sql_provider, catalog)
```

## Key Features
### 1. Structured Error Reporting (`CxpError`)
Shared machine-readable error envelopes for catalogs that opt into the semantic layer.
```python
if response.error and response.error.retryable:
    # Orchestrator can decide to retry automatically
    await retry_operation()
```

### 2. High-Fidelity Results
Many first-party operations return structured data defined in `results.py` (for example `HttpResponse`, `DbCursor`, `AsyncWorkReport`).

### 3. Bidirectional Validation
Catalogs can define `input_schema` and `result_schema` for operations when the domain benefits from explicit request/response contracts.

## Documentation
See [docs/index.md](docs/index.md) for the full documentation set:
- [Protocol Overview](docs/protocol/descriptors.md)
- [Structured Errors](docs/protocol/errors.md)
- [Interface Catalogs](docs/catalogs/index.md)

## License
MIT
