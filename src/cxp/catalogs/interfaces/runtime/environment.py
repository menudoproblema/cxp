from __future__ import annotations

import msgspec

from cxp.catalogs.base import (
    CapabilityCatalog,
    CatalogCapability,
    CatalogOperation,
    ConformanceTier,
    register_catalog,
)
from cxp.catalogs.common import (
    CXP_RESOURCE_NAME,
    CXP_RESOURCE_KIND,
)
from cxp.catalogs.results import (
    SecretValue,
    ResourceReport,
)

RUNTIME_ENVIRONMENT_INTERFACE = "runtime/environment"

# Capability Names
RUNTIME_SECRETS = "secrets"
RUNTIME_CONFIG = "configuration"
RUNTIME_RESOURCES = "resources"

# Operation Names (Standardized: RUNTIME_OP_{ACTION})
RUNTIME_OP_READ_SECRET = "runtime.secret_read"
RUNTIME_OP_READ_CONFIG = "runtime.config_read"
RUNTIME_OP_RESOURCE_STATS = "runtime.resource_stats"

class ConfigMetadata(msgspec.Struct, frozen=True):
    sources: tuple[str, ...]

RUNTIME_ENVIRONMENT_CATALOG = register_catalog(
    CapabilityCatalog(
        interface=RUNTIME_ENVIRONMENT_INTERFACE,
        description="Canonical catalog for execution environments.",
        capabilities=(
            CatalogCapability(
                name=RUNTIME_SECRETS,
                description="Secure access to sensitive environment data.",
                operations=(
                    CatalogOperation(
                        name=RUNTIME_OP_READ_SECRET,
                        result_type="runtime.secret_value",
                        result_schema=SecretValue,
                        description="Read a secure secret value.",
                    ),
                ),
            ),
            CatalogCapability(
                name=RUNTIME_CONFIG,
                description="Standard environment configuration.",
                metadata_schema=ConfigMetadata,
                operations=(
                    CatalogOperation(
                        name=RUNTIME_OP_READ_CONFIG,
                        result_type="runtime.config_value",
                    ),
                ),
            ),
            CatalogCapability(
                name=RUNTIME_RESOURCES,
                description="Monitoring of system resources.",
                operations=(
                    CatalogOperation(
                        name=RUNTIME_OP_RESOURCE_STATS,
                        result_type="runtime.resource_report",
                        result_schema=ResourceReport,
                    ),
                ),
            ),
        ),
        tiers=(
            ConformanceTier(
                name="core",
                required_capabilities=(RUNTIME_CONFIG,),
                description="Basic observable environment.",
            ),
        ),
    ),
    replace=True,
)

__all__ = (
    "RUNTIME_ENVIRONMENT_CATALOG",
    "RUNTIME_ENVIRONMENT_INTERFACE",
    "RUNTIME_SECRETS",
    "RUNTIME_CONFIG",
    "RUNTIME_RESOURCES",
)
