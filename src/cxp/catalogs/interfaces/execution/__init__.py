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
        description="Catálogo canónico para engines de ejecución tipada.",
        capabilities=(
            CatalogCapability(
                name=EXECUTION_ENGINE_RUN,
                description="Ejecución materializada con reporting.",
                operations=(
                    CatalogOperation(
                        name="run",
                        result_type="run.result",
                        description="Ejecuta un plan o selección materializada.",
                    ),
                ),
            ),
            CatalogCapability(
                name=EXECUTION_ENGINE_PLANNING,
                description="Planificación y explicación previas a la ejecución.",
                operations=(
                    CatalogOperation(
                        name="plan.analyze",
                        result_type="plan.analyzed",
                        description="Analiza la intención ejecutable.",
                    ),
                    CatalogOperation(
                        name="plan.explain",
                        result_type="plan.explained",
                        description="Explica decisiones de planificación.",
                    ),
                    CatalogOperation(
                        name="plan.simulate",
                        result_type="plan.simulated",
                        description="Simula la ejecución sin materializarla.",
                    ),
                ),
            ),
            CatalogCapability(
                name=EXECUTION_ENGINE_DRAFT_VALIDATION,
                description="Validación de contenido en memoria o borrador.",
                operations=(
                    CatalogOperation(
                        name="draft.validate",
                        result_type="draft.validated",
                        description="Valida contenido sin persistencia.",
                    ),
                ),
            ),
            CatalogCapability(
                name=EXECUTION_ENGINE_LIVE_EXECUTION_OBSERVABILITY,
                description="Seguimiento vivo de ejecución en curso.",
                operations=(
                    CatalogOperation(
                        name="execution.subscribe",
                        result_type="execution.subscribe",
                        description="Abre suscripción viva a la ejecución.",
                    ),
                    CatalogOperation(
                        name="execution.live_status",
                        result_type="execution.live_status",
                        description="Consulta el estado vivo agregado.",
                    ),
                    CatalogOperation(
                        name="execution.live_tail",
                        result_type="execution.live_tail",
                        description="Recupera cola viva de eventos recientes.",
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
                description="Engine capaz de planificar y ejecutar.",
            ),
            ConformanceTier(
                name="advanced",
                required_capabilities=(
                    EXECUTION_ENGINE_RUN,
                    EXECUTION_ENGINE_PLANNING,
                    EXECUTION_ENGINE_DRAFT_VALIDATION,
                    EXECUTION_ENGINE_LIVE_EXECUTION_OBSERVABILITY,
                ),
                description="Engine con validación y observabilidad en vivo.",
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
