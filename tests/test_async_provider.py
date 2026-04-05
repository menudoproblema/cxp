import asyncio

from pytest import raises

from cxp import (
    MONGODB_CATALOG,
    Capability,
    CapabilityDescriptor,
    CapabilityMatrix,
    ComponentCapabilitySnapshot,
    ComponentIdentity,
    TelemetrySnapshot,
    collect_provider_capability_snapshot_async,
    collect_provider_telemetry_async,
    negotiate_with_async_provider,
    negotiate_with_async_provider_catalog,
    stream_provider_telemetry_async,
)


def test_negotiate_with_async_provider_accepts_request(
    mongo_request_factory,
    async_mongo_provider_factory,
) -> None:
    request = mongo_request_factory(
        required_capabilities=("read",),
    )

    response = asyncio.run(
        negotiate_with_async_provider(
            request,
            async_mongo_provider_factory(("read", "write")),
        ),
    )

    assert response.status == "accepted"
    assert response.protocol_version == 1


def test_negotiate_with_async_provider_returns_degraded_for_missing_optional_capabilities(  # noqa: E501
    mongo_request_factory,
    async_mongo_provider_factory,
) -> None:
    request = mongo_request_factory(
        required_capabilities=("read",),
        optional_capabilities=("transactions",),
    )

    response = asyncio.run(
        negotiate_with_async_provider(
            request,
            async_mongo_provider_factory(("read", "write")),
        ),
    )

    assert response.status == "degraded"
    assert response.reason is not None
    assert "Missing optional capabilities" in response.reason
    assert response.missing_optional_capabilities == ("transactions",)


def test_negotiate_with_async_provider_catalog_rejects_unknown_capabilities(
    mongo_request_factory,
) -> None:
    class AsyncUnknownCapabilityProvider:
        async def cxp_identity(self) -> ComponentIdentity:
            return ComponentIdentity(
                interface="database/mongodb",
                provider="example-mongodb",
                version="3.0.0",
            )

        async def cxp_capabilities(self) -> CapabilityMatrix:
            return CapabilityMatrix(
                capabilities=(
                    Capability(name="read"),
                    Capability(name="custom_x"),
                ),
            )

    request = mongo_request_factory(required_capabilities=("read",))
    response = asyncio.run(
        negotiate_with_async_provider_catalog(
            request,
            AsyncUnknownCapabilityProvider(),
            MONGODB_CATALOG,
        )
    )

    assert response.status == "rejected"
    assert response.reason is not None
    assert "Unknown capabilities: custom_x" in response.reason


def test_collect_provider_telemetry_async_validates_provider_id(
    async_telemetry_provider_factory,
) -> None:
    with raises(ValueError, match="provider_id does not match"):
        asyncio.run(
            collect_provider_telemetry_async(
                async_telemetry_provider_factory(
                    TelemetrySnapshot(provider_id="other-provider"),
                ),
            ),
        )


def test_stream_provider_telemetry_async_yields_validated_snapshots(
    async_telemetry_stream_provider,
) -> None:
    async def _collect() -> tuple[TelemetrySnapshot, ...]:
        return tuple(
            [
                snapshot
                async for snapshot in stream_provider_telemetry_async(
                    async_telemetry_stream_provider,
                )
            ],
        )

    snapshots = asyncio.run(_collect())

    assert len(snapshots) == 2
    assert snapshots[1].status == "degraded"


def test_collect_provider_capability_snapshot_async_injects_missing_identity(
    async_snapshot_provider_factory,
) -> None:
    snapshot = asyncio.run(
        collect_provider_capability_snapshot_async(
            async_snapshot_provider_factory(
                ComponentCapabilitySnapshot(
                    component_name="gherkin",
                    capabilities=(
                        CapabilityDescriptor(name="planning", level="supported"),
                    ),
                ),
            ),
        ),
    )

    assert snapshot.identity is not None
    assert snapshot.identity.interface == "execution/engine"
    assert snapshot.identity.provider == "gherkin"


def test_collect_provider_capability_snapshot_async_rejects_identity_mismatch(
    async_snapshot_provider_factory,
) -> None:
    with raises(ValueError, match="identity does not match provider identity"):
        asyncio.run(
            collect_provider_capability_snapshot_async(
                async_snapshot_provider_factory(
                    ComponentCapabilitySnapshot(
                        component_name="gherkin",
                        identity=ComponentIdentity(
                            interface="database/mongodb",
                            provider="example-mongodb",
                            version="3.0.0",
                        ),
                        capabilities=(
                            CapabilityDescriptor(name="planning", level="supported"),
                        ),
                    ),
                ),
            ),
        )
