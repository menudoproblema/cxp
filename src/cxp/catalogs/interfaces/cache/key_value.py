from __future__ import annotations

from cxp.catalogs.base import (
    CapabilityCatalog,
    CapabilityTelemetry,
    CatalogCapability,
    CatalogOperation,
    ConformanceTier,
    TelemetryMetricSpec,
    register_catalog,
)
from cxp.catalogs.common import (
    CACHE_HIT,
    CXP_RESOURCE_NAME,
    UNIT_SECONDS,
)
from cxp.catalogs.results import ActionResult, CacheValue

CACHE_KV_INTERFACE = "cache/key-value"

# Capability Names
CACHE_KV_READ_WRITE = "read_write"
CACHE_KV_EXPIRATION = "expiration"
CACHE_KV_COUNTERS = "counters"

# Operation Names
CACHE_OP_GET = "cache.get"
CACHE_OP_SET = "cache.set"
CACHE_OP_DEL = "cache.delete"
CACHE_OP_INCR = "cache.increment"

_CACHE_TELEMETRY = CapabilityTelemetry(
    metrics=(
        TelemetryMetricSpec(
            name="cache.operations.total",
            required_labels=(CXP_RESOURCE_NAME, CACHE_HIT),
        ),
        TelemetryMetricSpec(
            name="cache.latency",
            unit=UNIT_SECONDS,
            required_labels=(CXP_RESOURCE_NAME,),
        ),
    ),
)

CACHE_KV_CATALOG = register_catalog(
    CapabilityCatalog(
        interface=CACHE_KV_INTERFACE,
        description=(
            "Canonical catalog for key-value cache providers (Redis, Memcached)."
        ),
        capabilities=(
            CatalogCapability(
                name=CACHE_KV_READ_WRITE,
                description="Basic GET, SET and DELETE operations.",
                telemetry=_CACHE_TELEMETRY,
                operations=(
                    CatalogOperation(
                        name=CACHE_OP_GET,
                        result_type="cache.value",
                        result_schema=CacheValue,
                        description="Retrieve a value by its key.",
                    ),
                    CatalogOperation(
                        name=CACHE_OP_SET,
                        result_type="action.result",
                        result_schema=ActionResult,
                    ),
                    CatalogOperation(
                        name=CACHE_OP_DEL,
                        result_type="action.result",
                        result_schema=ActionResult,
                    ),
                ),
            ),
            CatalogCapability(
                name=CACHE_KV_EXPIRATION,
                description="Ability to set Time-To-Live (TTL) on keys.",
            ),
            CatalogCapability(
                name=CACHE_KV_COUNTERS,
                description="Atomic increment and decrement operations.",
                operations=(
                    CatalogOperation(name=CACHE_OP_INCR, result_type="cache.new_count"),
                ),
            ),
        ),
        tiers=(
            ConformanceTier(
                name="core",
                required_capabilities=(CACHE_KV_READ_WRITE,),
                description="Standard key-value cache.",
            ),
            ConformanceTier(
                name="ephemeral",
                required_capabilities=(CACHE_KV_READ_WRITE, CACHE_KV_EXPIRATION),
                description="Cache with support for volatile data.",
            ),
        ),
    ),
    replace=True,
)

__all__ = (
    "CACHE_KV_CATALOG",
    "CACHE_KV_INTERFACE",
)
