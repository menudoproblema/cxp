# C4 conservation matrix (implementation ledger)

This ledger records the decision for each legacy guarantee before deleting code.
It does not certify migration. CXP 4.3.0 is published and verified from PyPI.
The current C4 branch combines the opt-in catalog v2 contract with the
deprecation window in a 4.4.0 release candidate. It is not a removal release;
the public retirement requires a later major.

| Legacy surface / guarantee | Real consumer or owner | Exact successor | Gate before removal |
| --- | --- | --- | --- |
| Capability identity, declared support, operations | Cosecha runner/planner; Mongoeco catalog exports | Owner catalog and snapshot v1, pinned by identity/version/SHA; `support` and operation requirements | Same positive/negative decisions for every consumed tier/profile |
| Profile `required_metadata_keys` | Mongoeco `compat/_catalog_export.py`; Cosecha profile validation | Per-capability `string_set` property of keys actually present, `contains_all` requirement; local owner validates value shape before snapshot | Missing key remains insufficient or negative according to the authored requirement, never filled by a default; catalog rejects unknown keys |
| Tiers and families | Cosecha component admission; Mongoeco profiles and `database/mongodb` interface family | Owner-authored named requirement documents with `all` of capability/operation/property leaves, each pinned to one catalog; a family relation is an explicit owner declaration, not a global registry lookup | Every old tier/profile requirement has an equivalent authored tree and independent oracle; no implicit ordering |
| `ActivationTrigger(kind, name)` | Cosecha `capabilities.py`, `flag_namespaces.py`, `instrumentation_planner.py` | Keep correlated pairs in Cosecha operational bootstrap metadata and its local validation. Remove the redundant legacy CXP metadata projection. If a real compatibility consumer emerges, add a typed portable pair-set to exchange first | Planner accepts/rejects each pair and preserves kind/name association; no flattening |
| Operation input/result schemas | Published generic legacy catalogs; no active Cosecha or Mongoeco runtime use found | Runtime payload validation belongs to the producer's operational contract. `result_type` remains the portable exchange operation identity. A consumer that compares schema compatibility needs a versioned portable contract before deletion | Inspect external consumers and retain equivalent operational validators wherever used |
| Metadata schemas for offered descriptors | Cosecha and Mongoeco legacy catalog validation | Owner validates data shape before emitting exchange snapshots; exchange evaluates only normalized reported properties | Invalid metadata cannot become a compatible snapshot |
| Handshake, descriptors, matrices, compliance evaluation | Cosecha runtime and Mongoeco public facade | One exchange `CatalogStore` + `evaluate_requirements` path; owner construction and lifecycle remain local | No runtime import or public fallback to old modules; negative/unknown cases preserved |
| Global catalog registry | Cosecha `runtime_interop.py`; CXP legacy imports | Exact explicit `CatalogStore` passed by the consumer | No environmental registration, import-by-ID or network resolution |
| Reserved runtime interface names and capability matrix checks | Cosecha manifest/profile validation for `application/*`, `database/*`, `execution/*`, `transport/*` | Explicit owner catalog references and requirements for actual runtime services; Cosecha keeps binding names, service graph, modes, readiness and lifecycle as operational state | Unknown reserved interface and unknown capability reject; abstract `execution/engine` cannot silently select a concrete catalog; exact catalog identity/version/SHA is supplied by the profile or its owner, never discovered from a global registry |
| Cosecha engine/runtime/instrumentation/reporter/plugin catalogs | CXP `catalogs/interfaces/cosecha`; Cosecha adapters and runner | Catalog JSON and requirement documents owned and versioned by Cosecha | Installed Cosecha artifact exports exact hashes and evaluates without Cosecha imports in evaluator process |
| MongoDB generic interface catalog | CXP `catalogs/interfaces/database/mongodb`; Mongoeco facade, compat and telemetry | Owner-authored Mongoeco exchange catalog and requirements. Mochuelo deployment catalog is separate | Installed Mongoeco artifact, compat outputs and explain/telemetry tests pass without legacy CXP modules |
| CXP telemetry classes | Mongoeco driver telemetry, Cosecha operational telemetry | Producer-owned telemetry contract; exchange is only compatibility | Existing telemetry outputs preserved and no CXP legacy runtime import |
| Exchange v1/v2 documents, canonical JSON, hashes, limits, catalog store and evaluator | Tórculo and future Mochuelo | Retain in CXP major; no second evaluator | Historical vectors and Tórculo functional tests remain green |

## Release and consumer order

1. CXP 4.3.0 is published with deprecation warnings. Keep its exact PyPI artifacts as the baseline for migration and historical conformance.
2. Migration releases of Cosecha and Mongoeco replace runtime uses of legacy CXP. Their current manifests keep `<5`; Tórculo already has `<5`.
3. Publish at least one subsequent minor retaining the deprecated public APIs, per `docs/stability.md`. The opt-in catalog v2 candidate is being prepared for this window.
4. After consumer artifacts pass installed tests and dependencies are coordinated, the removal major can delete legacy entrypoints and catalogs. Retain neutral validation code actually imported by exchange. Confirm absence in the wheel/sdist and recheck external consumers immediately before removal.

The repository census found Cosecha, Mongoeco and Tórculo in current accessible
checkouts. A public web code search returned no indexed matches; that result
cannot establish that no published external consumer exists.
The repeated local search also found historical `cosecha-framework.old` and
several worktrees of the same gdynamics/Cosecha repository. The old checkout
has extensive unrelated WIP and `cxp>=1.0.0`; it is preserved as evidence,
not treated as the current Cosecha migration target. This does not settle
external published consumers.

## Current preparation status (2026-09-26)

- CXP `ai/cxp-c4@481c757` merged catalog v2 and C4 deprecation preparation as
  `4.4.0.dev0`; its 12-cell artifact matrix passed. The subsequent stable
  4.4.0 candidate requires its own exact artifact evidence. This version keeps
  the legacy code and is not the removal major.
- Cosecha `ai/cosecha-c4@54d8aaf` has a clean merged source and Python 3.13
  wheel/sdist installations with CXP 4.3.0 from PyPI. All 38 pinned
  requirements and the local runtime verdicts pass in both installations.
  `cxp_adapters.py` remains packaged for the current public compatibility
  window; no C4 absence claim is made.
- Mongoeco `ai/mongoeco-catalog-v2@59ed7e9` has an owner catalog v2 candidate
  with source references and domains, pinned to CXP `4.4.0.dev0`; its wheel
  and sdist pass isolated installation checks. It has not been published.
- Before public removal, repeat the external consumer census, validate the
  installed absence of handshake/descriptors/registry/adapters and preserve
  the v1 historical artifacts outside the new package.

## Progress against this ledger

The entries below preserve earlier migration observations in chronological
order. Their candidate and lock statements describe those earlier revisions;
the current state is recorded above.

- Mongoeco branch `ai/mongoeco-c4` bounds its legacy dependency below 5 and
  packages an owner-authored MongoDB exchange catalog, three tier documents,
  five profile documents and a declared snapshot. Its runtime projection checks
  local typed metadata before reporting present keys and uses the one exchange
  `CatalogStore`. Tests cover missing values, incompatible explicit values,
  wrong operation types, source policy and exact hash. A wheel installed with
  CXP 4.3.0 can evaluate these documents without importing CXP legacy modules.
  Driver telemetry now uses Mongoeco-owned primitives and works from an
  installed wheel without `cxp.telemetry`. The old Mongoeco catalog facade,
  public reexports and compat exports still use legacy CXP objects.
- Cosecha branch `ai/cosecha-c4` bounds its legacy dependency below 5 and
  packages five owner catalogs, nineteen tiers and nineteen profiles. Source
  tests and an installed-wheel read validate the exact references. The
  instrumentation planner now uses exchange for tier/profile evaluation and
  validates correlated trigger pairs in Cosecha before projection. Its runner,
  runtime interop and other adapters still use legacy APIs; those must migrate
  before any removal major. The staged Cosecha worktree cannot commit while
  its unrelated RFC corpus hook rejects the available workset: historical
  `RFC-GDT-0003` content at the recorded revision has a different SHA-256 from
  the roadmap's candidate pin.
- CXP 4.3.0 now resolves package exports lazily: importing
  `cxp.exchange.core` does not load validator or legacy catalog modules. The
  final wheel/sdist candidate at `cd87211` passed the full twelve-cell release
  matrix. This is local evidence, not publication or a migration release.
- The final CXP wheel (`6b81ee9d31111ce2d74f9d1aca90cc12510d96c08b024fcab9f37120d33f0794`)
  passed 15 Tórculo PDF/planning exchange tests on its existing checkout. The
  one deselected test asserts the intentionally unchanged 4.2.0 lock; it is a
  release coordination check, not an exchange behavior failure. The Tórculo
  source worktree and lock were not edited.
- A Cosecha core wheel rebuilt after the instrumentation planner migration
  installed with the exact CXP 4.3.0 wheel into a fresh Python 3.13
  environment. Its five owner catalogs and the instrumentation summary tier
  load with the pinned content hashes, and that exchange-only import path does
  not load `cxp.catalogs`, `cxp.descriptors` or `cxp.handshake`. This smoke does
  not certify runner admission: that path still uses legacy adapters.
- With that core wheel reinstalled after dependency resolution, the real
  Cosecha coverage instrumenter produced a declared exchange snapshot and
  satisfied the `composable` tier (`a9dec37922d04815c313761e1874899436fb9227aa63f0d94e4c2d631436e65d`).
  Importing the instrumenter already loads CXP legacy catalogs through other
  Cosecha entrypoints; the exchange evaluation itself introduced no additional
  legacy imports. This is an integration pass for the planner's data path, not
  an absence-of-legacy gate for the whole consumer.
- The Cosecha lock still resolves CXP 4.1.0, because 4.3.0 is only a local
  candidate. Its source tests use the installed exact 4.3.0 wheel. The
  migration release must raise the dependency floor to the published exchange
  version and regenerate the portable lock before its full gate.
- The Cosecha runtime interface census identified a separate active legacy
  path: `runtime_interop.py` currently imports the global CXP registry and
  application, database, execution and transport catalogs to validate
  reserved interface names and capability matrices during manifest/profile
  checks. Replacing the component admission catalogs alone does not close C4.
  A profile must carry or resolve an exact owner-authored exchange catalog;
  the abstract execution interface's present implicit concrete lookup cannot
  remain as a fallback.
- Both migration-branch wheel manifests now require
  `cxp[exchange]>=4.3.0,<5`, matching their context-v2 code and excluding the
  removal major. Their checked-in locks still resolve older published CXP and
  must be refreshed after 4.3.0 publication. Cosecha's instrumentation
  projection rejects unknown metadata keys; Mongoeco's owner validator rejects
  unknown top-level keys and wrong top-level types across all ten capability
  metadata shapes. The latter does not turn nested operational metadata into
  portable exchange semantics.
- The rebuilt Mongoeco wheel and exact local CXP 4.3.0 wheel installed into a
  fresh Python 3.13 environment with resolved dependencies. Its declared
  `mongodb-core` evaluation was compatible at catalog SHA
  `2426ee7a7d9b4c06ab6d22b3eb9de2dcc16f2cd7b385efb618c7eb373c84dc5a`
  without loading `cxp.catalogs`. The rebuilt Cosecha core wheel installed
  with CXP 4.3.0 and evaluated the real coverage instrumenter as `composable`.
  These are installed exchange paths, not full consumer release gates.
- Cosecha runner instrumentation admission now builds the owner-validated
  declared snapshot and evaluates the summary tier with exchange/context v2.
  Its strict mode rejects an indeterminate requirement, and a focused runner,
  planner and catalog set passed 123 tests.
- Cosecha plugin runner admission now evaluates its declared owner snapshot
  against the core tier through the same exchange evaluator. A real telemetry
  plugin satisfies the telemetry sidecar tier; unknown sidecar capabilities
  reject. The runner, plugin and catalog focal set passed 82 tests. Reporter,
  runtime and engine runner admission now also use their owner validated
  declared snapshots and exchange context v2. Real Gherkin satisfies the
  integrated engine tier, while Pytest is indeterminate for that tier and
  compatible for core, knowledge and planning. Engine runner focal tests pass.
  The standalone `cxp_adapters.py` remains legacy and requires removal before
  the major.
- The Cosecha engine projection now rejects missing declared knowledge scopes
  instead of supplying a favorable default. Gherkin and Pytest declare their
  scopes explicitly; a negative omission test and their owner contract tests
  pass. A rebuilt installed core wheel (`aaede0f21d9a9a564b61ed49686f2c8098e81c7ce10d8319af6a446dc1d0321e`)
  evaluates the real local runtime as compatible against the pinned runtime
  tier and loads all five catalog hashes. Importing the operational runtime
  still loads `cxp.catalogs` and `cxp.descriptors` through legacy runtime
  interop at the time of this wheel build; a later source change removes that
  import and still needs a rebuilt installed-wheel gate.
- Mongoeco cursor `explain()` now reports the exact exchange catalog reference
  and profile verdicts from the single exchange evaluator using context v2.
  It no longer infers a minimal profile from a query path. Operation metadata
  stays in owner-authored data. The new Mongoeco wheel installed with the
  final CXP 4.3.0 wheel evaluates a vector-search explanation as compatible
  without loading `cxp.catalogs`, `cxp.descriptors`, `cxp.handshake` or
  `cxp.capabilities`. Its 209 focal cursor/exchange tests pass. The old public
  facade and `compat` exports remain active separately.
- Mongoeco's real mock/tooling gate now has a sixth pinned exchange profile,
  `mongodb-mock-safe`. It requires operation bindings and owner-validated
  metadata keys without flattening structured values. An omitted required key
  is incompatible in an independent negative test. The
  `compat.export_mock_safe_profile_catalog()` path now evaluates this same
  document with the exchange evaluator. Historical JSON and Markdown fixtures
  remain unchanged as evidence; tests compare their unaffected sections and
  assert the deliberate mock-safe projection delta. Its 259 focused compat,
  cursor and exchange tests pass.
- Cosecha now owns its manifest/runtime-profile interface-name vocabulary as
  an operational contract. The previous global CXP registry and its implicit
  abstract-to-concrete catalog lookup are gone from active runtime interop.
  Abstract `execution/engine` with capability claims rejects; concrete
  `execution/plan-run` validates. Reserved unknown names and capability names
  still reject. The focused runtime-profile, manifest and discovery set passes
  51 tests, and importing `cosecha.core.runtime` no longer loads any CXP
  legacy component module in the source environment. This operational
  vocabulary does not decide provider compatibility. Any such decision needs
  the exact catalog and requirements of the provider's owner; Cosecha's
  runtime service graph and readiness checks remain operational.
- A rebuilt Cosecha core wheel
  (`1f9e881d2eb27c1abbc1945458158149b8dc77210568a96ba2153425df274197`)
  installed with exact CXP 4.3.0 evaluates the real local runtime as
  compatible. Its manifest vocabulary rejects unknown
  `execution/plan-run` capability names, and that installed path loads none of
  `cxp.catalogs`, `cxp.descriptors`, `cxp.handshake` or `cxp.capabilities`.
  The expanded source focal set passes 197 tests. The old adapter module is
  still packaged, so full artifact absence remains open.
- The Cosecha `cxp_adapters` module and Mongoeco legacy root reexports now emit
  `DeprecationWarning` while their migration branches retain those APIs.
  Mongoeco's direct `cxp.capabilities` facade also warns. These are source
  preparations for consumer migration releases; the old files are not yet
  removed and no deprecation release has been published.
- The CXP C4 branch now emits a `DeprecationWarning` when a root export or
  direct module import of the legacy component protocol is resolved. Shared
  validation exports do not warn. The behavior is documented in the unreleased
  changelog and stability policy; all legacy APIs remain available. The
  branch's local `scripts/check.py` gate passed (506 tests). This is
  preparatory source code,
  not a published deprecation release or the required subsequent minor.
