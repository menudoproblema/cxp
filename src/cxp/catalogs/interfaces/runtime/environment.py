from __future__ import annotations

import msgspec

from cxp.catalogs.base import (
    CapabilityCatalog,
    CatalogCapability,
    CatalogOperation,
    ConformanceTier,
    register_catalog,
)
from cxp.catalogs.results import (
    ActionResult,
    ResourceReport,
    RuntimeHealthReport,
    SecretValue,
)

RUNTIME_ENVIRONMENT_INTERFACE = "runtime/environment"

# Capability Names
RUNTIME_SECRETS = "secrets"
RUNTIME_CONFIG = "configuration"
RUNTIME_RESOURCES = "resources"
RUNTIME_HEALTH = "health"
RUNTIME_LIFECYCLE = "lifecycle"

# Operation Names (Standardized: RUNTIME_OP_{ACTION})
RUNTIME_OP_READ_SECRET = "runtime.secret_read"
RUNTIME_OP_READ_CONFIG = "runtime.config_read"
RUNTIME_OP_RESOURCE_STATS = "runtime.resource_stats"
RUNTIME_OP_HEALTH_CHECK = "runtime.health_check"
RUNTIME_OP_RELOAD = "runtime.reload"

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
            CatalogCapability(
                name=RUNTIME_HEALTH,
                description="Readiness and health inspection for the runtime.",
                operations=(
                    CatalogOperation(
                        name=RUNTIME_OP_HEALTH_CHECK,
                        result_type="runtime.health_report",
                        result_schema=RuntimeHealthReport,
                    ),
                ),
            ),
            CatalogCapability(
                name=RUNTIME_LIFECYCLE,
                description="Lifecycle control for managed runtimes.",
                operations=(
                    CatalogOperation(
                        name=RUNTIME_OP_RELOAD,
                        result_type="action.result",
                        result_schema=ActionResult,
                    ),
                ),
            ),
        ),
        tiers=(
            ConformanceTier(
                name="core",
                required_capabilities=(RUNTIME_CONFIG, RUNTIME_HEALTH),
                description="Basic observable environment.",
            ),
            ConformanceTier(
                name="managed",
                required_capabilities=(
                    RUNTIME_CONFIG,
                    RUNTIME_HEALTH,
                    RUNTIME_LIFECYCLE,
                ),
                description="Environment with readiness checks and reload control.",
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
    "RUNTIME_HEALTH",
    "RUNTIME_LIFECYCLE",
    "RUNTIME_OP_HEALTH_CHECK",
    "RUNTIME_OP_RELOAD",
)
