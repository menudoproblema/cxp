# CXP: Capability Exchange Protocol

CXP exchanges versioned JSON documents for capabilities, requirements,
observations and compatibility results. A catalog is selected by its exact
namespace, name, version and SHA-256. The evaluator returns `compatible`,
`incompatible` or `indeterminate` from validated inputs.

```bash
pip install 'cxp[exchange]'
cxp catalog list
python -m cxp.exchange.tutorial
```

```python
from cxp.exchange import Document, CatalogStore, evaluate_requirements_detailed

# The producer supplies its own catalog and snapshot documents. The consumer
# supplies its pinned requirements and an explicit context, including the
# accepted source kinds in context v2.
result = evaluate_requirements_detailed(
    snapshot,
    requirements,
    context,
    catalogs=CatalogStore((catalog,)),
)
print(result.verdict)
```

CXP validates and compares claims. It does not discover providers, download
catalogs, authenticate evidence, perform probes, create leases, manage a
lifecycle or select a runtime modality. Producers own catalog semantics and
operational contracts. Consumers own admission policy and evidence checks.

Catalog v2 adds explicit string domains and exact documentary sources at the
catalog, capability, property and operation levels. Catalog v1 remains readable;
adoption of v2 is explicit. See the [catalog v2 specification](docs/protocol/catalog-v2.md).

The component handshake, descriptors, global catalog registry, built-in
producer catalogs and telemetry protocol from earlier CXP releases were
retired in the removal major. Historical source, tests and examples are kept
under `evidence/` as non-installed evidence. See the
[migration guide](docs/migration-c4.md) and [C4 conservation matrix](docs/architecture/c4-conservation-matrix.md).

Read the [exchange specification](docs/protocol/exchange-v1.md),
[catalog v2](docs/protocol/catalog-v2.md),
[context v2](docs/protocol/context-v2.md),
[integration guide](docs/protocol/exchange-integration.md),
[CLI guide](docs/cli.md), and [reference catalogs](docs/catalogs/exchange-reference.md).

The package supports Python 3.12–3.14. See [CONTRIBUTING.md](CONTRIBUTING.md)
for local checks and candidate verification. Publication is a separate gate.
