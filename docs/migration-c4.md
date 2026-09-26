# Migration from the retired component protocol

This guide applies to the future CXP removal major. It does not assign or
announce a published version. CXP 4.3.0 is the published deprecation release.
The verified 4.4.0 candidate must be published as the subsequent minor before
this public removal under [stability policy](stability.md).

## Replace the compatibility path

| Earlier API | Successor |
| --- | --- |
| `CapabilityCatalog` and global `get_catalog` | Producer-authored `cxp.catalog` documents, resolved by an explicit `CatalogStore` and exact identity/version/SHA-256 |
| `CapabilityMatrix`, `CapabilityDescriptor`, `ComponentCapabilitySnapshot` | Validated `cxp.snapshot` documents with explicit subject, configuration revision, time and homogeneous source |
| `CapabilityProfile`, conformance tiers and `is_component_snapshot_compliant` | Producer-authored, pinned `cxp.requirements` documents and `evaluate_requirements_detailed` |
| `HandshakeRequest`, `HandshakeResponse` and negotiation over legacy DTOs | `cxp.exchange_request` / `cxp.exchange_agreement` only for exchange format negotiation; no automatic v1 fallback |
| CXP telemetry classes and operation input/result schemas | Operational contracts of the producer; exchange operation bindings retain portable result-type identities |

The evaluator accepts only validated documents. For admission with context v2,
set nonempty `accepted_sources` explicitly. `declared`, `observed` and
`tested` have no implicit trust order. A source outside the accepted set yields
`indeterminate`; it is not a known incompatibility. The consumer verifies
evidence references and coverage. CXP does not fetch or authenticate reports.

## Conserve domain guarantees

Metadata key presence is expressed through an owner-validated
`metadata_keys` string set and a `contains_all` requirement. A missing
reported key is incompatible; an unreported key set is indeterminate. The
producer must validate metadata values locally before publishing that set.
Operation names and result types live in the exact owner catalog. A changed
capability needs a new catalog version and explicit adoption; it cannot be
introduced by a silent registry update.

Tiers and profiles become named requirement documents. There is no implicit
hierarchy or total order of multidimensional guarantees. Correlated
`ActivationTrigger(kind, name)` pairs remain in Cosecha's operational bootstrap
contract and local validation; their relationship is never flattened into an
ignored extension. Runtime payload schemas, readiness, lifecycle and
telemetry stay with their operational owners. A real cross-component schema
compatibility need would require a separate versioned portable contract.

Cosecha owns its engine, runtime, instrumentation, reporter and plugin exchange
catalogs and requirements. Mongoeco owns its generic MongoDB catalog and
requirements. Mochuelo's deployment guarantee catalog is separate and owned
by Mochuelo. Tórculo remains an exchange consumer and needs only artifact
conformance against the selected release.

## Historical evidence and release gate

The retired Python source, old API tests, catalog definitions and examples
remain byte for byte in `evidence/legacy-cxp-python-evidence.zip` in this
repository. They are not importable from the new wheel or installed sdist.
The old wire fixtures remain in `tests/fixtures`
to prove that exchange does not route old payloads to a permissive reader.

Before publication, verify both wheel and sdist, all supported Python and
dependency combinations, installed consumer artifacts, exact catalog hashes,
the absence of legacy modules, and the release sequence recorded in the
[conservation matrix](architecture/c4-conservation-matrix.md). Do not widen
consumer dependency bounds to this major until their migration artifacts pass.
