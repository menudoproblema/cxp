# Changelog

## Unreleased

- Added abstract interface-family support in catalogs via `abstract` and `satisfies_interfaces`.
- Added first-party `application/wsgi` and `application/asgi` catalogs, and moved the previous high-level HTTP framework semantics to `application/http-framework`.
- Updated the handshake so a concrete interface can satisfy an abstract family interface only when both interfaces are backed by registered catalogs. For example, `application/asgi` can satisfy a request for `application/http`.

## 1.0.0

- Stabilized the core handshake contract around `ComponentIdentity`, `CapabilityMatrix`, and protocol-version negotiation.
- Added first-party catalogs for `database/mongodb`, `transport/http`, `application/http`, and `execution/engine`.
- Added rich component descriptors with `CapabilityDescriptor`, `ComponentCapabilitySnapshot`, and `ComponentDependencyRule`.
- Added sync and async provider helpers for capability negotiation, capability snapshots, telemetry collection, and telemetry streaming.
- Added typed validation results for capability matrices and descriptor snapshots.
- Added bounded telemetry buffering with overflow policies and dropped-item accounting.
- Added catalog-aware negotiation helpers that validate handshake responses against canonical catalogs.
- Aligned documentation, examples, packaging metadata, and test coverage for the `1.0.0` release.
