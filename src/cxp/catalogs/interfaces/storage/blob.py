from __future__ import annotations

import msgspec

from cxp.catalogs.base import (
    CapabilityCatalog,
    CatalogCapability,
    CatalogOperation,
    ConformanceTier,
    CapabilityTelemetry,
    TelemetryMetricSpec,
    register_catalog,
)
from cxp.catalogs.common import (
    CXP_RESOURCE_NAME,
    STORAGE_OPERATION,
    UNIT_BYTES,
)
from cxp.catalogs.results import (
    BlobMetadata,
)

STORAGE_BLOB_INTERFACE = "storage/blob"

# Capability Names
BLOB_OBJECT_MANAGEMENT = "object_management"
BLOB_VERSIONING = "versioning"

# Operation Names
BLOB_OP_UPLOAD = "blob.upload"
BLOB_OP_DELETE = "blob.delete"
BLOB_OP_GET_META = "blob.get_metadata"

_BLOB_TELEMETRY = CapabilityTelemetry(
    metrics=(
        TelemetryMetricSpec(
            name="storage.blob.io",
            unit=UNIT_BYTES,
            required_labels=(CXP_RESOURCE_NAME, STORAGE_OPERATION),
        ),
    ),
)

STORAGE_BLOB_CATALOG = register_catalog(
    CapabilityCatalog(
        interface=STORAGE_BLOB_INTERFACE,
        description="Canonical catalog for object storage providers (S3, GCS, etc).",
        capabilities=(
            CatalogCapability(
                name=BLOB_OBJECT_MANAGEMENT,
                description="Standard upload, delete and metadata management.",
                telemetry=_BLOB_TELEMETRY,
                operations=(
                    CatalogOperation(name=BLOB_OP_UPLOAD, result_type="none"),
                    CatalogOperation(name=BLOB_OP_DELETE, result_type="none"),
                    CatalogOperation(
                        name=BLOB_OP_GET_META,
                        result_type="blob.metadata",
                        result_schema=BlobMetadata,
                    ),
                ),
            ),
            CatalogCapability(
                name=BLOB_VERSIONING,
                description="Management of multiple versions for the same object.",
            ),
        ),
        tiers=(
            ConformanceTier(
                name="core",
                required_capabilities=(BLOB_OBJECT_MANAGEMENT,),
                description="Standard object storage.",
            ),
        ),
    ),
    replace=True,
)

__all__ = (
    "STORAGE_BLOB_CATALOG",
    "STORAGE_BLOB_INTERFACE",
)
