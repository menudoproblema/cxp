from __future__ import annotations

from cxp.catalogs.base import (
    CapabilityCatalog,
    CatalogCapability,
    CatalogOperation,
    ConformanceTier,
    register_catalog,
)
from cxp.catalogs.common import (
    DB_SYSTEM,
    DB_OPERATION,
    DB_NAMESPACE,
    CXP_OPERATION_STATUS,
)
from cxp.catalogs.results import (
    DbCursor,
    DbWriteResult,
)
from cxp.catalogs.inputs import DbQueryInput

DATABASE_INTERFACE = "database/common"

# Capability Names
DATABASE_CONNECTIVITY = "connectivity"
DATABASE_READ = "read"
DATABASE_WRITE = "write"
DATABASE_OBSERVABILITY = "observability"

# Operation Names
DATABASE_OP_CONNECT = "db.connect"
DATABASE_OP_EXECUTE = "db.execute"
DATABASE_OP_QUERY = "db.query"
DATABASE_OP_PING = "db.ping"

DATABASE_CATALOG = register_catalog(
    CapabilityCatalog(
        interface=DATABASE_INTERFACE,
        abstract=True,
        description=(
            "Abstract base for all data persistence providers, defining core "
            "concepts like connectivity, read/write operations, and observability."
        ),
        capabilities=(
            CatalogCapability(
                name=DATABASE_CONNECTIVITY,
                description="Managing connections and session state with the database provider.",
                operations=(
                    CatalogOperation(
                        name=DATABASE_OP_CONNECT,
                        result_type="db.connection",
                        idempotent=True, # Safety flag
                        timeout_seconds=5.0,
                    ),
                    CatalogOperation(
                        name=DATABASE_OP_PING,
                        result_type="db.pong",
                        idempotent=True,
                        timeout_seconds=2.0,
                    ),
                ),
            ),
            CatalogCapability(
                name=DATABASE_READ,
                description="Retrieving data without modifying provider state.",
                operations=(
                    CatalogOperation(
                        name=DATABASE_OP_QUERY,
                        input_schema=DbQueryInput, # Bidirectional fidelity
                        result_type="db.cursor",
                        result_schema=DbCursor,
                        idempotent=True,
                        description="Execute a query and return a result stream.",
                    ),
                ),
            ),
            CatalogCapability(
                name=DATABASE_WRITE,
                description="Modifying or inserting data into the provider.",
                operations=(
                    CatalogOperation(
                        name=DATABASE_OP_EXECUTE,
                        result_type="db.write_result",
                        result_schema=DbWriteResult,
                        idempotent=False, # Dangerous to retry blindly
                        timeout_seconds=30.0,
                    ),
                ),
            ),
        ),
        tiers=(
            ConformanceTier(
                name="core",
                required_capabilities=(DATABASE_CONNECTIVITY, DATABASE_READ),
            ),
        ),
    ),
    replace=True,
)

__all__ = (
    "DATABASE_CATALOG",
    "DATABASE_INTERFACE",
    "DATABASE_CONNECTIVITY",
    "DATABASE_READ",
    "DATABASE_WRITE",
)
