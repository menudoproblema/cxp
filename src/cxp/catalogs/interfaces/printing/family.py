from __future__ import annotations

from cxp.catalogs.base import (
    CapabilityCatalog,
    CatalogCapability,
    CatalogOperation,
    ConformanceTier,
    register_catalog,
)
from cxp.catalogs.results import (
    ActionResult,
    PrinterStatus,
    PrintJobStatus,
)

PRINTING_INTERFACE = "printing/manager"

# Capability Names
PRINTING_JOB_SUBMISSION = "job_submission"
PRINTING_STATUS_MONITORING = "status_monitoring"
PRINTING_CONSUMABLES_TRACKING = "consumables_tracking"

# Operation Names
PRINT_OP_SUBMIT = "print.submit"
PRINT_OP_GET_JOB_STATUS = "print.job_status"
PRINT_OP_GET_PRINTER_STATUS = "print.printer_status"
PRINT_OP_CANCEL = "print.cancel"

PRINTING_CATALOG = register_catalog(
    CapabilityCatalog(
        interface=PRINTING_INTERFACE,
        abstract=True,
        description=(
            "Abstract base for all printing infrastructure, defining standardized "
            "job submission, tracking, and consumables management."
        ),
        capabilities=(
            CatalogCapability(
                name=PRINTING_JOB_SUBMISSION,
                description="Submission of print jobs (PDF, ZPL, PCL).",
                operations=(
                    CatalogOperation(
                        name=PRINT_OP_SUBMIT,
                        result_type="print.job_id",
                    ),
                    CatalogOperation(
                        name=PRINT_OP_CANCEL,
                        result_type="action.result",
                        result_schema=ActionResult,
                    ),
                ),
            ),
            CatalogCapability(
                name=PRINTING_STATUS_MONITORING,
                description="Real-time monitoring of job and hardware state.",
                operations=(
                    CatalogOperation(
                        name=PRINT_OP_GET_JOB_STATUS,
                        result_type="print.job_status",
                        result_schema=PrintJobStatus,
                    ),
                    CatalogOperation(
                        name=PRINT_OP_GET_PRINTER_STATUS,
                        result_type="print.printer_status",
                        result_schema=PrinterStatus,
                    ),
                ),
            ),
            CatalogCapability(
                name=PRINTING_CONSUMABLES_TRACKING,
                description="Monitoring of toner, paper, and hardware alerts.",
            ),
        ),
        tiers=(
            ConformanceTier(
                name="core",
                required_capabilities=(PRINTING_JOB_SUBMISSION, PRINTING_STATUS_MONITORING),
                description="Basic functional printer or print server.",
            ),
        ),
    ),
    replace=True,
)

__all__ = (
    "PRINTING_CATALOG",
    "PRINTING_INTERFACE",
)
