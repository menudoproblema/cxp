# Changelog

## 4.1.0 — 2026-09-04

- Added explicit reference-catalog version selection and deterministic discovery
  metadata while preserving every unversioned loader call on catalog 1.0.0.
- Added `physical-printing` 1.1.0 with loaded-mass, object-envelope, configured
  print-mode and paired-resolution properties; machine geometry and control stay
  outside CXP.
- Added immutable typed evaluation details with precise comparison reasons and
  operands. The existing evaluator still returns byte-identical
  `cxp.evaluation` v1 documents from the same single engine.
- Added exact `cm` and `m` input conversion to document-valid `mm` quantities
  without accepting new units in document specification v1.
- Added the dependency-light `cxp` CLI for validation, evaluation, schemas and
  catalog inspection, including stable JSON diagnostics and distinct exit codes
  for incompatible and indeterminate outcomes.
- Added a synthetic physical-exchange tutorial, public stability/deprecation and
  security policies, and property-based tests for exact quantities,
  canonicalization and evaluator projection.
- Hardened release handling with non-overwriting recoverable candidates,
  isolated base/exchange/dev installations, all direct runtime dependency
  boundaries, `pip check`, environment-local license evidence and macOS/Windows
  wheel smoke tests.
- Pinned GitHub Actions by immutable commit, added dependency review and update
  automation, and prepared a manual protected Trusted Publishing flow that
  uploads only previously accredited artifacts, produces PyPI attestations and
  verifies the published hashes and clean installation.
- Corrected the MongoDB profile example link found by the release documentation
  integrity pass and made local-link validation a source gate.

## 4.0.0 — 2026-09-03

- Added independent JSON Schema 2020-12 document contracts, bounded strict JSON
  readers, duplicate-key detection, critical-extension rejection, RFC 8785
  canonicalization and SHA-256 input references under `cxp.exchange`.
- Added immutable local catalog stores, owned snapshots and deterministic
  compatible/incompatible/indeterminate evaluation with explicit context,
  effective-support policy, comparisons, sets, logical groups and exact ranges.
- Added exact decimal-string quantities, rational unit conversion, opt-in
  protocol v2 format agreements and explicit readers without legacy fallback.
- Added five independently versioned reference catalogs, operation payload
  schemas, conservative legacy-idempotency conversion and portable examples.
- Tightened legacy validation for dict/Struct parity, duplicate identities,
  invalid catalog definitions, binding/result conflicts and composed contracts.
  Detailed diagnostics supplement existing boolean facades and result fields.
- Corrected Web Push `send` result_type from `push.result` to its parent
  `notification.result`; the result schema remains `PushResult`.
- Preserved legacy handshake v1, imports, providers, global catalog facades,
  profile construction and noop behavior; documented observable validation
  changes and the permissive old-reader limitation in the migration guide.
- Added baseline API/wire fixtures, a second JSON Schema engine for conformance
  tests, standalone checks/CI and clean wheel/sdist verification for Python
  3.12–3.14. The base package requires only msgspec>=0.20.0,<1. The optional
  exchange extra declares jsonschema>=4.23,<5, referencing>=0.35,<1 and
  rfc8785>=0.1.4,<1; shipped `py.typed` explicitly.
- Corrected retry guidance: a transient error does not authorize repeating a
  non-idempotent operation. No drivers, jobs, retries or publishing are executed.
- Closed rc1 review findings: deterministic tar/gzip packaging verified by two
  consecutive builds, isolated base/extra installation tests, per-instance
  caching only for immutable catalog definitions, and mandatory formatting.
- Extended portable vectors with negotiation, agreement rejection, exclusive
  bounds and negative-origin/step cases. Added precise requirement diagnostics
  and consistent unsafe-integer errors for raw JSON and Python mappings.
- Agreements now check the actual document version, not a hard-coded version 1.

## 3.1.0

- Added a richer `cosecha/instrumentation` contract with bootstrap metadata validation for strategy, runtime slots, and activation triggers.
- Added the composable instrumentation profile and its public exports so orchestration layers can negotiate strict composition requirements explicitly.
- Added the `instrumentation.activate` operation plus public constants for declared bootstrap strategies and runtime slots.
- Clarified the architecture distinction between tier-level capability presence and profile-level strict validation for Cosecha instrumentation negotiation.

## 3.0.0

- Stabilized the core handshake contract around `ComponentIdentity`, `CapabilityMatrix`, and protocol-version negotiation.
- Introduced abstract interface-family support in catalogs via `abstract` and `satisfies_interfaces`.
- Established richer catalog metadata with optional `input_schema`, `result_schema`, idempotency flags, and suggested timeouts.
- Standardized shared telemetry vocabulary, units, and operational statuses in `common.py`.
- Introduced structured error reporting via `CxpError` as an optional semantic envelope for catalogs that adopt it.
- Added a comprehensive suite of first-party catalogs organized in six logical layers:
    - **Computing**: `execution/plan-run` (base for all async tasks), `runtime/environment` (secrets/resources), `application/asgi` and `application/wsgi`.
    - **Persistence**: `database/sql`, `database/mongodb` (satisfying `database/common`), `storage/blob` (with versioning), and `cache/key-value`.
    - **Communications**: `transport/http`, `transport/http-family`, `transport/websocket`, `messaging/event-bus` (NATS/JetStream), and `notification/common` (WebPush, Mobile Push).
    - **Queueing**: `queue/task-engine` for background processing.
    - **Experience & Media**: `browser/automation` (Playwright with LocalStorage support) and `media/video-streaming` (HLS/DASH/Transcoding).
    - **Industrial**: `printing/manager` for Label (Zebra/ZPL) and Production (Konica Minolta) printing with physical finishing support.
- Added a Compliance Bridge API for catalog-aware negotiation reports without changing the core handshake shape.
- Added contextual telemetry propagation in `TelemetryContext` for `cxp.request.id`, `cxp.session.id`, `cxp.operation.id`, and `cxp.parent.operation.id`.
- Added rich component descriptors with `CapabilityDescriptor`, `ComponentCapabilitySnapshot`, and `ComponentDependencyRule`.
- Added sync and async provider helpers for capability negotiation, telemetry collection, and streaming.
- Added runnable high-fidelity examples and comprehensive documentation for all interface catalogs.
