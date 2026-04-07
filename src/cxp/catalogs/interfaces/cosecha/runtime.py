from __future__ import annotations

import msgspec

from cxp.catalogs.base import (
    CapabilityCatalog,
    CapabilityProfile,
    CapabilityRequirement,
    CatalogCapability,
    CatalogOperation,
    ConformanceTier,
    register_catalog,
)

COSECHA_RUNTIME_INTERFACE = "cosecha/runtime"

COSECHA_RUNTIME_INJECTED_EXECUTION_PLANS = "injected_execution_plans"
COSECHA_RUNTIME_ISOLATED_PROCESSES = "isolated_processes"
COSECHA_RUNTIME_PERSISTENT_WORKERS = "persistent_workers"
COSECHA_RUNTIME_RUN_SCOPED_RESOURCES = "run_scoped_resources"
COSECHA_RUNTIME_WORKER_SCOPED_RESOURCES = "worker_scoped_resources"
COSECHA_RUNTIME_LIVE_EXECUTION_OBSERVABILITY = (
    "live_execution_observability"
)

COSECHA_RUNTIME_RUN = "run"
COSECHA_RUNTIME_EXECUTION_SUBSCRIBE = "execution.subscribe"
COSECHA_RUNTIME_EXECUTION_LIVE_STATUS = "execution.live_status"
COSECHA_RUNTIME_EXECUTION_LIVE_TAIL = "execution.live_tail"

COSECHA_RUNTIME_LOCAL_TIER = "local"
COSECHA_RUNTIME_PROCESS_TIER = "process"
COSECHA_RUNTIME_OBSERVABLE_TIER = "observable"

COSECHA_RUNTIME_LOCAL_PROFILE_NAME = "cosecha-runtime-local"
COSECHA_RUNTIME_PROCESS_PROFILE_NAME = "cosecha-runtime-process"
COSECHA_RUNTIME_OBSERVABLE_PROFILE_NAME = "cosecha-runtime-observable"


class ResourceScopeMetadata(msgspec.Struct, frozen=True):
    supported_scopes: tuple[str, ...] = ()
    effective_scope: str | None = None
    materialization: str | None = None


class ProcessIsolationMetadata(msgspec.Struct, frozen=True):
    isolation_unit: str | None = None


class LiveExecutionMetadata(msgspec.Struct, frozen=True):
    delivery_mode: str
    granularity: str
    read_only: bool = True
    live_source: str = "live_projection"
    live_channels: tuple[str, ...] = ()
    running_test_limit: int | None = None
    worker_limit: int | None = None
    resource_limit: int | None = None
    event_tail_limit: int | None = None


COSECHA_RUNTIME_CATALOG = register_catalog(
    CapabilityCatalog(
        interface=COSECHA_RUNTIME_INTERFACE,
        description=(
            "Canonical catalog for Cosecha runtime providers with execution, "
            "resource scope, isolation and live observability semantics."
        ),
        capabilities=(
            CatalogCapability(
                name=COSECHA_RUNTIME_INJECTED_EXECUTION_PLANS,
                description="Execute pre-built plans produced by the core scheduler.",
                operations=(
                    CatalogOperation(
                        name=COSECHA_RUNTIME_RUN,
                        result_type="run.result",
                    ),
                ),
            ),
            CatalogCapability(
                name=COSECHA_RUNTIME_ISOLATED_PROCESSES,
                description="Run work in isolated worker processes.",
                metadata_schema=ProcessIsolationMetadata,
            ),
            CatalogCapability(
                name=COSECHA_RUNTIME_PERSISTENT_WORKERS,
                description="Retain workers across multiple execution nodes.",
            ),
            CatalogCapability(
                name=COSECHA_RUNTIME_RUN_SCOPED_RESOURCES,
                description="Materialize run-scoped resources for runtime execution.",
                metadata_schema=ResourceScopeMetadata,
            ),
            CatalogCapability(
                name=COSECHA_RUNTIME_WORKER_SCOPED_RESOURCES,
                description="Materialize worker or test scoped resources.",
                metadata_schema=ResourceScopeMetadata,
            ),
            CatalogCapability(
                name=COSECHA_RUNTIME_LIVE_EXECUTION_OBSERVABILITY,
                description="Expose a volatile live execution projection for the active session.",
                metadata_schema=LiveExecutionMetadata,
                operations=(
                    CatalogOperation(
                        name=COSECHA_RUNTIME_EXECUTION_SUBSCRIBE,
                        result_type="execution.subscribe",
                    ),
                    CatalogOperation(
                        name=COSECHA_RUNTIME_EXECUTION_LIVE_STATUS,
                        result_type="execution.live_status",
                    ),
                    CatalogOperation(
                        name=COSECHA_RUNTIME_EXECUTION_LIVE_TAIL,
                        result_type="execution.live_tail",
                    ),
                ),
            ),
        ),
        tiers=(
            ConformanceTier(
                name=COSECHA_RUNTIME_LOCAL_TIER,
                required_capabilities=(
                    COSECHA_RUNTIME_INJECTED_EXECUTION_PLANS,
                    COSECHA_RUNTIME_RUN_SCOPED_RESOURCES,
                ),
                description="Single-process local runtime.",
            ),
            ConformanceTier(
                name=COSECHA_RUNTIME_PROCESS_TIER,
                required_capabilities=(
                    COSECHA_RUNTIME_INJECTED_EXECUTION_PLANS,
                    COSECHA_RUNTIME_ISOLATED_PROCESSES,
                    COSECHA_RUNTIME_PERSISTENT_WORKERS,
                    COSECHA_RUNTIME_RUN_SCOPED_RESOURCES,
                    COSECHA_RUNTIME_WORKER_SCOPED_RESOURCES,
                ),
                description="Process-based runtime with persistent workers.",
            ),
            ConformanceTier(
                name=COSECHA_RUNTIME_OBSERVABLE_TIER,
                required_capabilities=(
                    COSECHA_RUNTIME_INJECTED_EXECUTION_PLANS,
                    COSECHA_RUNTIME_RUN_SCOPED_RESOURCES,
                    COSECHA_RUNTIME_LIVE_EXECUTION_OBSERVABILITY,
                ),
                description="Runtime with explicit live execution observability.",
            ),
        ),
    )
)

COSECHA_RUNTIME_LOCAL_PROFILE = CapabilityProfile(
    name=COSECHA_RUNTIME_LOCAL_PROFILE_NAME,
    interface=COSECHA_RUNTIME_INTERFACE,
    requirements=(
        CapabilityRequirement(
            capability_name=COSECHA_RUNTIME_INJECTED_EXECUTION_PLANS,
            required_operations=(COSECHA_RUNTIME_RUN,),
        ),
        CapabilityRequirement(
            capability_name=COSECHA_RUNTIME_RUN_SCOPED_RESOURCES,
            required_metadata_keys=("supported_scopes",),
        ),
    ),
    description="Local runtime execution profile.",
)

COSECHA_RUNTIME_PROCESS_PROFILE = CapabilityProfile(
    name=COSECHA_RUNTIME_PROCESS_PROFILE_NAME,
    interface=COSECHA_RUNTIME_INTERFACE,
    requirements=(
        CapabilityRequirement(
            capability_name=COSECHA_RUNTIME_ISOLATED_PROCESSES,
            required_metadata_keys=("isolation_unit",),
        ),
        CapabilityRequirement(
            capability_name=COSECHA_RUNTIME_WORKER_SCOPED_RESOURCES,
            required_metadata_keys=("supported_scopes",),
        ),
    ),
    description="Process runtime profile.",
)

COSECHA_RUNTIME_OBSERVABLE_PROFILE = CapabilityProfile(
    name=COSECHA_RUNTIME_OBSERVABLE_PROFILE_NAME,
    interface=COSECHA_RUNTIME_INTERFACE,
    requirements=(
        CapabilityRequirement(
            capability_name=COSECHA_RUNTIME_LIVE_EXECUTION_OBSERVABILITY,
            required_operations=(
                COSECHA_RUNTIME_EXECUTION_SUBSCRIBE,
                COSECHA_RUNTIME_EXECUTION_LIVE_STATUS,
                COSECHA_RUNTIME_EXECUTION_LIVE_TAIL,
            ),
            required_metadata_keys=(
                "delivery_mode",
                "granularity",
                "live_channels",
            ),
        ),
    ),
    description="Observable runtime profile.",
)

__all__ = (
    "COSECHA_RUNTIME_CATALOG",
    "COSECHA_RUNTIME_EXECUTION_LIVE_STATUS",
    "COSECHA_RUNTIME_EXECUTION_LIVE_TAIL",
    "COSECHA_RUNTIME_EXECUTION_SUBSCRIBE",
    "COSECHA_RUNTIME_INJECTED_EXECUTION_PLANS",
    "COSECHA_RUNTIME_INTERFACE",
    "COSECHA_RUNTIME_ISOLATED_PROCESSES",
    "COSECHA_RUNTIME_LIVE_EXECUTION_OBSERVABILITY",
    "COSECHA_RUNTIME_LOCAL_PROFILE",
    "COSECHA_RUNTIME_LOCAL_PROFILE_NAME",
    "COSECHA_RUNTIME_LOCAL_TIER",
    "COSECHA_RUNTIME_OBSERVABLE_PROFILE",
    "COSECHA_RUNTIME_OBSERVABLE_PROFILE_NAME",
    "COSECHA_RUNTIME_OBSERVABLE_TIER",
    "COSECHA_RUNTIME_PERSISTENT_WORKERS",
    "COSECHA_RUNTIME_PROCESS_PROFILE",
    "COSECHA_RUNTIME_PROCESS_PROFILE_NAME",
    "COSECHA_RUNTIME_PROCESS_TIER",
    "COSECHA_RUNTIME_RUN",
    "COSECHA_RUNTIME_RUN_SCOPED_RESOURCES",
    "COSECHA_RUNTIME_WORKER_SCOPED_RESOURCES",
    "LiveExecutionMetadata",
    "ProcessIsolationMetadata",
    "ResourceScopeMetadata",
)
