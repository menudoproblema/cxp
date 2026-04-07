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
    CXP_OPERATION_STATUS,
)
from cxp.catalogs.results import TaskStatus

QUEUE_INTERFACE = "queue/task-engine"

# Capability Names
QUEUE_TASK_SUBMISSION = "task_submission"
QUEUE_SCHEDULING = "scheduling"
QUEUE_MONITORING = "monitoring"

# Operation Names
QUEUE_OP_ENQUEUE = "queue.enqueue"
QUEUE_OP_GET_STATUS = "queue.status"
QUEUE_OP_CANCEL = "queue.cancel"

_QUEUE_TELEMETRY = CapabilityTelemetry(
    metrics=(
        TelemetryMetricSpec(
            name="queue.backlog.size",
            required_labels=(CXP_RESOURCE_NAME,),
            description="Number of pending tasks in the queue.",
        ),
        TelemetryMetricSpec(
            name="queue.tasks.processed",
            required_labels=(CXP_RESOURCE_NAME, CXP_OPERATION_STATUS),
        ),
    ),
)

QUEUE_CATALOG = register_catalog(
    CapabilityCatalog(
        interface=QUEUE_INTERFACE,
        description="Canonical catalog for task queues and background processing engines.",
        capabilities=(
            CatalogCapability(
                name=QUEUE_TASK_SUBMISSION,
                description="Standard submission of background tasks.",
                telemetry=_QUEUE_TELEMETRY,
                operations=(
                    CatalogOperation(
                        name=QUEUE_OP_ENQUEUE,
                        result_type="queue.task_id",
                        description="Enqueue a task for asynchronous execution.",
                    ),
                ),
            ),
            CatalogCapability(
                name=QUEUE_MONITORING,
                description="Real-time status tracking of background tasks.",
                operations=(
                    CatalogOperation(
                        name=QUEUE_OP_GET_STATUS,
                        result_type="queue.task_status",
                        result_schema=TaskStatus,
                        description="Query the current state of a task.",
                    ),
                ),
            ),
            CatalogCapability(
                name=QUEUE_SCHEDULING,
                description="Scheduling tasks for future execution (delayed tasks).",
            ),
        ),
        tiers=(
            ConformanceTier(
                name="basic-queue",
                required_capabilities=(QUEUE_TASK_SUBMISSION,),
                description="Standard task submission engine.",
            ),
            ConformanceTier(
                name="observable-queue",
                required_capabilities=(QUEUE_TASK_SUBMISSION, QUEUE_MONITORING),
                description="Engine with task status tracking.",
            ),
        ),
    ),
    replace=True,
)

__all__ = (
    "QUEUE_CATALOG",
    "QUEUE_INTERFACE",
)
