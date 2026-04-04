from pytest import raises

from cxp import (
    MONGODB_CATALOG,
    Capability,
    CapabilityDescriptor,
    CapabilityMatrix,
    ComponentCapabilitySnapshot,
    ComponentIdentity,
    TelemetryMetric,
    TelemetrySnapshot,
    collect_provider_capability_snapshot,
    collect_provider_telemetry,
    negotiate_with_provider,
    negotiate_with_provider_catalog,
    stream_provider_telemetry,
)


def test_negotiate_with_provider_accepts_known_capabilities(
    mongo_request_factory,
    sync_mongo_provider_factory,
) -> None:
    request = mongo_request_factory(
        required_capabilities=("read",),
    )

    response = negotiate_with_provider(
        request,
        sync_mongo_provider_factory(("read", "write")),
    )

    assert response.status == "accepted"
    assert response.provider_identity.provider == "mongoeco2"


def test_negotiate_with_provider_rejects_missing_capabilities(
    mongo_request_factory,
    sync_mongo_provider_factory,
) -> None:
    request = mongo_request_factory(
        required_capabilities=("transactions",),
    )

    response = negotiate_with_provider(
        request,
        sync_mongo_provider_factory(("read", "write")),
    )

    assert response.status == "rejected"
    assert response.reason is not None
    assert response.missing_required_capabilities == ("transactions",)


def test_negotiate_with_provider_rejects_unsupported_protocol_version(
    mongo_request_factory,
    sync_mongo_provider_factory,
) -> None:
    request = mongo_request_factory(
        required_capabilities=("read",),
        protocol_version=2,
    )

    response = negotiate_with_provider(
        request,
        sync_mongo_provider_factory(
            ("read", "write"),
            supported_protocol_versions=(1,),
        ),
    )

    assert response.status == "rejected"
    assert response.reason is not None
    assert "Unsupported protocol version" in response.reason


def test_negotiate_with_provider_rejects_interface_mismatch(
    mongo_request_factory,
    sync_mongo_provider_factory,
) -> None:
    request = mongo_request_factory(
        interface="execution/engine",
        required_capabilities=("read",),
    )

    response = negotiate_with_provider(
        request,
        sync_mongo_provider_factory(("read", "write")),
    )

    assert response.status == "rejected"
    assert response.reason is not None
    assert "Interface mismatch" in response.reason


def test_negotiate_with_provider_returns_degraded_for_missing_optional_capabilities(
    mongo_request_factory,
    sync_mongo_provider_factory,
) -> None:
    request = mongo_request_factory(
        required_capabilities=("read",),
        optional_capabilities=("transactions",),
    )

    response = negotiate_with_provider(
        request,
        sync_mongo_provider_factory(("read", "write")),
    )

    assert response.status == "degraded"
    assert response.reason is not None
    assert "Missing optional capabilities" in response.reason
    assert response.missing_optional_capabilities == ("transactions",)


def test_negotiate_with_provider_catalog_rejects_unknown_capabilities(
    mongo_request_factory,
) -> None:
    class UnknownCapabilityProvider:
        def cxp_identity(self) -> ComponentIdentity:
            return ComponentIdentity(
                interface="database/mongodb",
                provider="mongoeco2",
                version="3.0.0",
            )

        def cxp_capabilities(self) -> CapabilityMatrix:
            return CapabilityMatrix(
                capabilities=(
                    Capability(name="read"),
                    Capability(name="custom_x"),
                ),
            )

    request = mongo_request_factory(required_capabilities=("read",))
    response = negotiate_with_provider_catalog(
        request,
        UnknownCapabilityProvider(),
        MONGODB_CATALOG,
    )

    assert response.status == "rejected"
    assert response.reason is not None
    assert "Unknown capabilities: custom_x" in response.reason


def test_negotiate_with_provider_catalog_preserves_degraded_reason_when_valid(
    mongo_request_factory,
    sync_mongo_provider_factory,
) -> None:
    request = mongo_request_factory(
        required_capabilities=("read",),
        optional_capabilities=("transactions",),
    )

    response = negotiate_with_provider_catalog(
        request,
        sync_mongo_provider_factory(("read", "write")),
        MONGODB_CATALOG,
    )

    assert response.status == "degraded"
    assert response.reason is not None
    assert "Missing optional capabilities" in response.reason


def test_negotiate_with_provider_catalog_preserves_missing_optional_on_reject(
    mongo_request_factory,
) -> None:
    class UnknownAndDegradedProvider:
        def cxp_identity(self) -> ComponentIdentity:
            return ComponentIdentity(
                interface="database/mongodb",
                provider="mongoeco2",
                version="3.0.0",
            )

        def cxp_capabilities(self) -> CapabilityMatrix:
            return CapabilityMatrix(
                capabilities=(
                    Capability(name="read"),
                    Capability(name="custom_x"),
                ),
            )

    request = mongo_request_factory(
        required_capabilities=("read",),
        optional_capabilities=("transactions",),
    )

    response = negotiate_with_provider_catalog(
        request,
        UnknownAndDegradedProvider(),
        MONGODB_CATALOG,
    )

    assert response.status == "rejected"
    assert response.reason is not None
    assert "Missing optional capabilities" in response.reason
    assert "Unknown capabilities: custom_x" in response.reason
    assert response.missing_optional_capabilities == ("transactions",)


def test_collect_provider_telemetry_accepts_matching_provider_id(
    sync_telemetry_provider_factory,
) -> None:
    snapshot = collect_provider_telemetry(
        sync_telemetry_provider_factory(
            TelemetrySnapshot(
                provider_id="mongoeco2",
                metrics=(TelemetryMetric(name="ops", value=3),),
                is_heartbeat=True,
            ),
        ),
    )

    assert snapshot is not None
    assert snapshot.provider_id == "mongoeco2"


def test_collect_provider_telemetry_rejects_mismatched_provider_id(
    sync_telemetry_provider_factory,
) -> None:
    with raises(ValueError, match="provider_id does not match"):
        collect_provider_telemetry(
            sync_telemetry_provider_factory(
                TelemetrySnapshot(provider_id="other-provider"),
            ),
        )


def test_stream_provider_telemetry_yields_validated_snapshots(
    sync_telemetry_stream_provider,
) -> None:
    snapshots = tuple(stream_provider_telemetry(sync_telemetry_stream_provider))

    assert len(snapshots) == 2
    assert snapshots[1].metrics[0].name == "ops"


def test_collect_provider_capability_snapshot_injects_missing_identity(
    sync_snapshot_provider_factory,
    supported_run_descriptor_snapshot,
) -> None:
    snapshot = collect_provider_capability_snapshot(
        sync_snapshot_provider_factory(supported_run_descriptor_snapshot),
    )

    assert snapshot.identity is not None
    assert snapshot.identity.interface == "execution/engine"
    assert snapshot.identity.provider == "pytest"


def test_collect_provider_capability_snapshot_rejects_identity_mismatch(
    sync_snapshot_provider_factory,
) -> None:
    with raises(ValueError, match="identity does not match provider identity"):
        collect_provider_capability_snapshot(
            sync_snapshot_provider_factory(
                ComponentCapabilitySnapshot(
                    component_name="pytest",
                    identity=ComponentIdentity(
                        interface="database/mongodb",
                        provider="mongoeco2",
                        version="3.0.0",
                    ),
                    capabilities=(
                        CapabilityDescriptor(name="run", level="supported"),
                    ),
                ),
            ),
        )
