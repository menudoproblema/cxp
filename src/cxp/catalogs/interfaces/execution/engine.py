from __future__ import annotations

from cxp.catalogs.base import (
    CapabilityCatalog,
    CatalogCapability,
    CatalogOperation,
    ConformanceTier,
    register_catalog,
)

EXECUTION_ENGINE_INTERFACE = "execution/engine"

EXECUTION_ENGINE_RUN = "run"
EXECUTION_ENGINE_PLANNING = "planning"
EXECUTION_ENGINE_DRAFT_VALIDATION = "draft_validation"
EXECUTION_ENGINE_LIVE_EXECUTION_OBSERVABILITY = "live_execution_observability"

EXECUTION_ENGINE_CATALOG = register_catalog(
    CapabilityCatalog(
        interface=EXECUTION_ENGINE_INTERFACE,
        description="Canonical catalog for typed execution engines.",
        capabilities=(
            CatalogCapability(
                name=EXECUTION_ENGINE_RUN,
                description="Materialized execution with reporting.",
                operations=(
                    CatalogOperation(
                        name="run",
                        result_type="run.result",
                        description="Execute a plan or materialized selection.",
                    ),
                ),
            ),
            CatalogCapability(
                name=EXECUTION_ENGINE_PLANNING,
                description="Planning and explanation before execution.",
                operations=(
                    CatalogOperation(
                        name="plan.analyze",
                        result_type="plan.analyzed",
                        description="Analyze executable intent.",
                    ),
                    CatalogOperation(
                        name="plan.explain",
                        result_type="plan.explained",
                        description="Explain planning decisions.",
                    ),
                    CatalogOperation(
                        name="plan.simulate",
                        result_type="plan.simulated",
                        description="Simulate execution without materializing it.",
                    ),
                ),
            ),
            CatalogCapability(
                name=EXECUTION_ENGINE_DRAFT_VALIDATION,
                description="Validation of in-memory or draft content.",
                operations=(
                    CatalogOperation(
                        name="draft.validate",
                        result_type="draft.validated",
                        description="Validate content without persistence.",
                    ),
                ),
            ),
            CatalogCapability(
                name=EXECUTION_ENGINE_LIVE_EXECUTION_OBSERVABILITY,
                description="Live observability for in-progress execution.",
                operations=(
                    CatalogOperation(
                        name="execution.subscribe",
                        result_type="execution.subscribe",
                        description="Open a live execution subscription.",
                    ),
                    CatalogOperation(
                        name="execution.live_status",
                        result_type="execution.live_status",
                        description="Read aggregate live status.",
                    ),
                    CatalogOperation(
                        name="execution.live_tail",
                        result_type="execution.live_tail",
                        description="Read a live tail of recent events.",
                    ),
                ),
            ),
        ),
        tiers=(
            ConformanceTier(
                name="core",
                required_capabilities=(
                    EXECUTION_ENGINE_RUN,
                    EXECUTION_ENGINE_PLANNING,
                ),
                description="Engine capable of planning and execution.",
            ),
            ConformanceTier(
                name="advanced",
                required_capabilities=(
                    EXECUTION_ENGINE_RUN,
                    EXECUTION_ENGINE_PLANNING,
                    EXECUTION_ENGINE_DRAFT_VALIDATION,
                    EXECUTION_ENGINE_LIVE_EXECUTION_OBSERVABILITY,
                ),
                description="Engine with validation and live observability.",
            ),
        ),
    )
)

__all__ = (
    "EXECUTION_ENGINE_CATALOG",
    "EXECUTION_ENGINE_DRAFT_VALIDATION",
    "EXECUTION_ENGINE_INTERFACE",
    "EXECUTION_ENGINE_LIVE_EXECUTION_OBSERVABILITY",
    "EXECUTION_ENGINE_PLANNING",
    "EXECUTION_ENGINE_RUN",
)
