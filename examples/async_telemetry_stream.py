import asyncio
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from cxp import (
    ComponentIdentity,
    TelemetryContext,
    TelemetrySnapshot,
    stream_provider_telemetry_async,
)


class AsyncMongoTelemetryStreamProvider:
    async def cxp_identity(self) -> ComponentIdentity:
        return ComponentIdentity(
            interface="database/mongodb",
            provider="example-mongodb",
            version="3.0.0",
        )

    def cxp_telemetry_provider_id(self) -> str:
        return "example-mongodb"

    async def cxp_telemetry_stream(self):
        context = TelemetryContext(trace_id="stream-example")
        yield TelemetrySnapshot(
            provider_id="example-mongodb",
            events=(context.create_event("command_started"),),
        )
        yield TelemetrySnapshot(
            provider_id="example-mongodb",
            spans=(
                context.create_span(
                    "mongo.find",
                    start_time=1.0,
                    end_time=1.15,
                ),
            ),
        )


async def main() -> None:
    provider = AsyncMongoTelemetryStreamProvider()

    async for snapshot in stream_provider_telemetry_async(provider):
        print(snapshot)


asyncio.run(main())
