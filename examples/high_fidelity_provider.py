"""Ejemplo mínimo de un proveedor CXP con contratos enriquecidos."""

from cxp.catalogs.common import (
    STATUS_SUCCESS,
    STORAGE_OPERATION,
    UNIT_BYTES,
)
from cxp.catalogs.interfaces.database.sql import (
    SQL_DATABASE_INTERFACE,
    SQL_DIALECT,
    SQL_TRANSACTIONS,
)
from cxp.catalogs.interfaces.storage.blob import (
    BLOB_OBJECT_MANAGEMENT,
    BLOB_OP_GET_META,
    STORAGE_BLOB_INTERFACE,
)
from cxp.catalogs.results import BlobMetadata
from cxp.telemetry import TelemetryContext


PROVIDER_DESCRIPTOR = {
    "interfaces": (
        {
            "interface": SQL_DATABASE_INTERFACE,
            "capabilities": (
                {
                    "name": SQL_DIALECT,
                    "metadata": {
                        "engine_name": "PostgreSQL",
                        "engine_version": "15.4",
                        "supports_json": True,
                    },
                },
                {
                    "name": SQL_TRANSACTIONS,
                    "metadata": {
                        "default_isolation_level": "read committed",
                        "supported_isolation_levels": (
                            "read committed",
                            "repeatable read",
                            "serializable",
                        ),
                    },
                },
            ),
        },
        {
            "interface": STORAGE_BLOB_INTERFACE,
            "capabilities": (
                {
                    "name": BLOB_OBJECT_MANAGEMENT,
                },
            ),
        },
    ),
}


async def get_blob_metadata_operation(key: str) -> BlobMetadata:
    """Cumple con `blob.get_metadata` devolviendo el DTO canónico."""
    return BlobMetadata(
        key=key,
        size_bytes=1024 * 1024,
        content_type="video/mp4",
        etag="demo-etag",
    )


def emit_telemetry_example(resource_name: str, operation_name: str) -> None:
    """Emite una métrica con campos contextuales y labels canónicos."""
    context = TelemetryContext(
        trace_id="trace-demo",
        request_id="req-demo",
        session_id="sess-demo",
        operation_id="op-demo",
    )
    metric = context.create_metric(
        "storage.blob.io",
        1024 * 1024,
        unit=UNIT_BYTES,
        labels={
            "cxp.resource.name": resource_name,
            "cxp.operation.status": STATUS_SUCCESS,
            STORAGE_OPERATION.name: operation_name,
        },
    )
    print(f"Telemetría emitida: {metric}")


if __name__ == "__main__":
    import asyncio

    print("Proveedor iniciado con interfaces SQL y Storage.")
    print(f"Operación soportada: {BLOB_OP_GET_META}")
    print(asyncio.run(get_blob_metadata_operation("videos/video1.mp4")))
    emit_telemetry_example("blob-store-1", BLOB_OP_GET_META)
