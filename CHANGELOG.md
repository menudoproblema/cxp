# Changelog

## Unreleased

- Added abstract interface-family support in catalogs via `abstract` and `satisfies_interfaces`.
- Added first-party `application/wsgi` and `application/asgi` catalogs, and moved the previous high-level HTTP framework semantics to `application/http-framework`.
- Updated the handshake so a concrete interface can satisfy an abstract family interface only when both interfaces are backed by registered catalogs. For example, `application/asgi` can satisfy a request for `application/http`.
- Added capability-linked telemetry semantics and telemetry snapshot validation in catalogs, with first-party telemetry conventions for `execution/plan-run` and `database/mongodb`.
- Refined `database/mongodb` telemetry so `aggregation`, `search`, and `vector_search` use their own canonical signals instead of overloading the generic document-operation span, and added stage-specific required fields for search/vector telemetry.
- Split execution catalogs into an abstract `execution/engine` family and a concrete `execution/plan-run` contract.
- Kept the legacy `EXECUTION_ENGINE_*` symbols and `cxp.catalogs.interfaces.execution.engine` import path as compatibility aliases for the concrete `execution/plan-run` contract.
- In `execution/plan-run`, `core` now requires only `run`, `planned` captures run-plus-planning, `draft_validation` was renamed to `input_validation`, and live observability was split into `execution_status` and `execution_stream`.

## 1.0.0

- Stabilized the core handshake contract around `ComponentIdentity`, `CapabilityMatrix`, and protocol-version negotiation.
- Added first-party catalogs for `database/mongodb`, `transport/http`, `application/http`, and `execution/engine`.
- Added rich component descriptors with `CapabilityDescriptor`, `ComponentCapabilitySnapshot`, and `ComponentDependencyRule`.
- Added sync and async provider helpers for capability negotiation, capability snapshots, telemetry collection, and telemetry streaming.
- Added typed validation results for capability matrices and descriptor snapshots.
- Added bounded telemetry buffering with overflow policies and dropped-item accounting.
- Added catalog-aware negotiation helpers that validate handshake responses against canonical catalogs.
- Aligned documentation, examples, packaging metadata, and test coverage for the `1.0.0` release.
