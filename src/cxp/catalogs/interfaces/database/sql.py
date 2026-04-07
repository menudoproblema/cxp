from __future__ import annotations

import msgspec

from cxp.catalogs.base import (
    CapabilityCatalog,
    CatalogCapability,
    CatalogOperation,
    ConformanceTier,
    register_catalog,
)
from cxp.catalogs.interfaces.database.family import DATABASE_INTERFACE

SQL_DATABASE_INTERFACE = "database/sql"

SQL_DIALECT = "dialect"
SQL_DDL = "ddl"
SQL_TRANSACTIONS = "transactions"
SQL_MIGRATIONS = "migrations"
SQL_POOLING = "pooling"

SQL_OP_BEGIN = "sql.begin"
SQL_OP_COMMIT = "sql.commit"
SQL_OP_ROLLBACK = "sql.rollback"
SQL_OP_MIGRATE = "sql.migrate"
SQL_OP_DDL_EXECUTE = "sql.ddl_execute"


class SqlDialectMetadata(msgspec.Struct, frozen=True):
    engine_name: str
    engine_version: str
    supports_json: bool = False


class SqlTransactionMetadata(msgspec.Struct, frozen=True):
    default_isolation_level: str
    supported_isolation_levels: tuple[str, ...]


class SqlPoolingMetadata(msgspec.Struct, frozen=True):
    min_connections: int = 0
    max_connections: int = 0


SQL_DATABASE_CATALOG = register_catalog(
    CapabilityCatalog(
        interface=SQL_DATABASE_INTERFACE,
        satisfies_interfaces=(DATABASE_INTERFACE,),
        description="Canonical catalog for relational SQL databases.",
        capabilities=(
            CatalogCapability(
                name=SQL_DIALECT,
                description="Engine dialect and feature support.",
                metadata_schema=SqlDialectMetadata,
            ),
            CatalogCapability(
                name=SQL_TRANSACTIONS,
                description="Atomic multi-operation transactions.",
                metadata_schema=SqlTransactionMetadata,
                operations=(
                    CatalogOperation(
                        name=SQL_OP_BEGIN,
                        result_type="sql.transaction",
                        description="Start a new transaction.",
                    ),
                    CatalogOperation(name=SQL_OP_COMMIT, result_type="none"),
                    CatalogOperation(name=SQL_OP_ROLLBACK, result_type="none"),
                ),
            ),
            CatalogCapability(
                name=SQL_DDL,
                description="Schema definition operations.",
                operations=(
                    CatalogOperation(
                        name=SQL_OP_DDL_EXECUTE,
                        result_type="sql.schema_report",
                    ),
                ),
            ),
            CatalogCapability(
                name=SQL_MIGRATIONS,
                description="Execution of ordered schema migrations.",
                operations=(
                    CatalogOperation(
                        name=SQL_OP_MIGRATE,
                        result_type="sql.migration_report",
                    ),
                ),
            ),
            CatalogCapability(
                name=SQL_POOLING,
                description="Connection pool management metadata.",
                metadata_schema=SqlPoolingMetadata,
            ),
        ),
        tiers=(
            ConformanceTier(
                name="core",
                required_capabilities=(SQL_DIALECT, SQL_TRANSACTIONS),
                description="Basic transactional SQL provider.",
            ),
        ),
    ),
    replace=True,
)

__all__ = (
    "SQL_DATABASE_CATALOG",
    "SQL_DATABASE_INTERFACE",
    "SQL_DDL",
    "SQL_DIALECT",
    "SQL_MIGRATIONS",
    "SQL_POOLING",
    "SQL_TRANSACTIONS",
)
