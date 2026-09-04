# Command-line interface

Install `cxp` for version/help and `cxp[exchange]` for document commands:

```bash
pip install 'cxp[exchange]>=4.1,<5'
cxp --version
```

The CLI reads explicit local files only. It does not fetch catalogs, discover
drivers, execute jobs or infer the current time.

## Commands

```bash
cxp validate snapshot.json --type cxp.snapshot
cxp validate snapshot.json --type cxp.snapshot --catalog catalog.json
cxp evaluate --catalog catalog.json --snapshot snapshot.json \
  --requirements requirements.json --context context.json
cxp evaluate --catalog catalog.json --snapshot snapshot.json \
  --requirements requirements.json --context context.json --explain
cxp schema document
cxp schema operation org.cxp:document-result:1
cxp catalog list
cxp catalog show physical-printing --version 1.1.0
```

`--catalog` may be repeated. `validate` reports scope `document` when it checks
only intrinsic document rules and `catalog` when it also resolves and validates
a snapshot or requirements document. A valid receipt is not a compatibility or
physical-safety decision.

`evaluate` always writes the canonical `cxp.evaluation` document to stdout,
including incompatible and indeterminate results. `--explain` writes leaf
findings to stderr. `--diagnostics json` makes expected errors and explanations
machine-readable without mixing them into the functional document.

## Exit codes

| Code | Meaning |
| --- | --- |
| 0 | Valid in the stated scope, or compatible evaluation |
| 1 | Incompatible evaluation |
| 2 | Invalid CLI usage or missing optional exchange dependencies |
| 3 | Indeterminate evaluation |
| 4 | Invalid document, semantic input or unresolved catalog |
| 5 | Unsupported family, version or critical extension |
| 6 | Input/output error |
| 70 | Unexpected internal error |

Automation should branch on 1 and 3 separately. Neither result authorizes a
retry or a production operation.
