import asyncio
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from cxp import (
    Capability,
    CapabilityMatrix,
    ComponentIdentity,
    HandshakeRequest,
    TelemetryContext,
    TelemetryMetric,
    TelemetrySnapshot,
    collect_provider_telemetry_async,
    negotiate_with_async_provider,
)


class AsyncMongoProvider:
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
                Capability(name="write"),
            )
        )

    def cxp_telemetry_provider_id(self) -> str:
        return "example-mongodb"

    async def cxp_telemetry_snapshot(self) -> TelemetrySnapshot | None:
        context = TelemetryContext(trace_id="async-example")
        return TelemetrySnapshot(
            provider_id="example-mongodb",
            events=(context.create_event("command_succeeded"),),
            metrics=(TelemetryMetric(name="ops", value=3),),
            spans=(
                context.create_span(
                    "mongo.find",
                    start_time=1.0,
                    end_time=1.2,
                ),
            ),
            is_heartbeat=True,
        )


async def main() -> None:
    provider = AsyncMongoProvider()
    request = HandshakeRequest(
        client_identity=ComponentIdentity(
            interface="database/mongodb",
            provider="cosecha",
            version="1.0.0",
        ),
        required_capabilities=("read",),
    )

    response = await negotiate_with_async_provider(request, provider)
    snapshot = await collect_provider_telemetry_async(provider)

    print(response.status)
    print(snapshot)


asyncio.run(main())
