# Changelog

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
