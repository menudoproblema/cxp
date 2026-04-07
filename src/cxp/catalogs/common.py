from __future__ import annotations

from cxp.catalogs.base import TelemetryFieldRequirement

# --- Universal Telemetry Units ---
UNIT_SECONDS = "s"
UNIT_BYTES = "By"
UNIT_BITS_PER_SEC = "bps"
UNIT_PERCENT = "%"
UNIT_COUNT = "1"
UNIT_MILLISECONDS = "ms"

# --- Universal Operation Statuses ---
STATUS_PENDING = "pending"
STATUS_RUNNING = "running"
STATUS_SUCCESS = "success"
STATUS_FAILURE = "failure"
STATUS_PARTIAL = "partial"
STATUS_CANCELLED = "cancelled"

# --- Universal Identity Fields ---
CXP_RESOURCE_NAME = TelemetryFieldRequirement(
    name="cxp.resource.name",
    description="The canonical name of the resource (engine, database, provider)."
)
CXP_RESOURCE_KIND = TelemetryFieldRequirement(
    name="cxp.resource.kind",
    description="The category of the resource (e.g., 'mongodb', 'playwright', 'asgi')."
)
CACHE_HIT = TelemetryFieldRequirement(
    name="cache.hit",
    description="Whether the cache lookup produced a hit."
)
PUSH_OUTCOME = TelemetryFieldRequirement(
    name="push.outcome",
    description="The provider-specific delivery outcome for a push notification."
)
STORAGE_OPERATION = TelemetryFieldRequirement(
    name="storage.operation",
    description="The storage operation associated with the metric sample."
)

# --- Universal Operational Fields ---
CXP_REQUEST_ID = TelemetryFieldRequirement(
    name="cxp.request.id",
    description="A stable identifier for the request crossing domains."
)
CXP_SESSION_ID = TelemetryFieldRequirement(
    name="cxp.session.id",
    description="A stable identifier for the end-to-end session."
)
CXP_OPERATION_ID = TelemetryFieldRequirement(
    name="cxp.operation.id",
    description="A stable identifier for the current logical operation."
)
CXP_PARENT_OPERATION_ID = TelemetryFieldRequirement(
    name="cxp.parent.operation.id",
    description="The logical parent operation identifier, if any."
)
CXP_OPERATION_NAME = TelemetryFieldRequirement(
    name="cxp.operation.name",
    description="The name of the catalog operation being executed."
)
CXP_OPERATION_STATUS = TelemetryFieldRequirement(
    name="cxp.operation.status",
    description="The status of the operation (success, error, partial)."
)
CXP_ERROR_CODE = TelemetryFieldRequirement(
    name="cxp.error.code",
    description="A standardized error code if the operation failed."
)

# --- Universal Performance Fields ---
CXP_DURATION = TelemetryFieldRequirement(
    name="cxp.duration",
    description="The duration of the operation in seconds."
)
CXP_PAYLOAD_SIZE = TelemetryFieldRequirement(
    name="cxp.payload.size_bytes",
    description="The size of the data payload in bytes."
)

# --- Shared Domain Fields ---
DB_SYSTEM = TelemetryFieldRequirement(name="db.system.name")
DB_OPERATION = TelemetryFieldRequirement(name="db.operation.name")
DB_NAMESPACE = TelemetryFieldRequirement(name="db.namespace.name")

HTTP_METHOD = TelemetryFieldRequirement(name="http.method")
HTTP_STATUS = TelemetryFieldRequirement(name="http.status_code")
HTTP_URL = TelemetryFieldRequirement(name="http.url")
