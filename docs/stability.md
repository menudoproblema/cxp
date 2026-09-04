# Public stability and deprecation policy

CXP follows semantic versioning for the Python distribution. Stability is
defined per surface because package APIs, documents and reference catalogs have
different identities.

## Stable surfaces

- Symbols exported by `cxp` and `cxp.exchange` are public Python API.
- JSON document families are identified by `document_type` and `spec_version`.
- A catalog is identified by namespace, name, version and content hash.
- JSON emitted by CLI commands and declared with `format_version` is a public
  automation contract.
- CLI exit codes documented in the CLI guide are stable.

Help text, human diagnostics, private modules, undocumented script internals and
development dependencies are not public compatibility surfaces.

## Compatibility rules

A patch fixes behavior without adding a new public contract. A minor may add
optional APIs, commands, properties or an explicitly versioned catalog while
preserving existing calls and defaults. A major may remove or redefine a public
surface after migration guidance.

Reference catalog loaders never reinterpret an omitted version as “latest”. A
call that selected 1.0.0 continues selecting 1.0.0; adoption of 1.1.0 is
explicit. Documents remain bound to the catalog identity and SHA-256 they name.

Deprecations are documented in the changelog and emit `DeprecationWarning` when
that is practical. A deprecated Python or CLI surface remains available for at
least one subsequent minor release. Wire contracts and published catalog
versions are not silently rewritten; retirement requires a documented successor
and migration path.

## Evaluation details

`cxp.evaluation` remains the portable result. `EvaluationResult` and its typed
findings are a local Python explanation of the same evaluation call. They do not
add fields to document specification v1 and cannot be treated as verified after
being detached from their inputs.
