from __future__ import annotations

from cxp.catalogs.base import (
    CapabilityTelemetry,
    CapabilityCatalog,
    CapabilityProfile,
    CapabilityRequirement,
    CatalogCapability,
    CatalogOperation,
    ConformanceTier,
    TelemetryEventSpec,
    TelemetryFieldRequirement,
    TelemetryMetricSpec,
    TelemetrySpanSpec,
    register_catalog,
)

PLAN_RUN_EXECUTION_INTERFACE = "execution/plan-run"

PLAN_RUN_EXECUTION_RUN = "run"
PLAN_RUN_EXECUTION_PLANNING = "planning"
PLAN_RUN_EXECUTION_INPUT_VALIDATION = "input_validation"
PLAN_RUN_EXECUTION_EXECUTION_STATUS = "execution_status"
PLAN_RUN_EXECUTION_EXECUTION_STREAM = "execution_stream"
PLAN_RUN_OP_STATUS = "execution.status"
PLAN_RUN_OP_CANCEL = "execution.cancel"

PLAN_RUN_EXECUTION_CORE_PROFILE_NAME = "plan-run-core"
PLAN_RUN_EXECUTION_PLANNED_PROFILE_NAME = "plan-run-planned"
PLAN_RUN_EXECUTION_ADVANCED_PROFILE_NAME = "plan-run-advanced"

PLAN_RUN_EXECUTION_CATALOG = register_catalog(
    CapabilityCatalog(
        interface=PLAN_RUN_EXECUTION_INTERFACE,
        satisfies_interfaces=("execution/engine",),
        description=(
            "Canonical catalog for engines that plan and execute typed runs,"
            " with optional pre-run validation and execution observability."
        ),
        capabilities=(
            CatalogCapability(
                name=PLAN_RUN_EXECUTION_RUN,
                description="Materialized execution with reporting.",
                telemetry=CapabilityTelemetry(
                    spans=(
                        TelemetrySpanSpec(
                            name="engine.run.execute",
                            required_attributes=(
                                TelemetryFieldRequirement(name="engine.name"),
                                TelemetryFieldRequirement(name="run.mode"),
                            ),
                            description="Primary execution span for materialized runs.",
                        ),
                    ),
                    metrics=(
                        TelemetryMetricSpec(
                            name="engine.run.duration",
                            unit="s",
                            required_labels=(
                                TelemetryFieldRequirement(name="engine.name"),
                                TelemetryFieldRequirement(name="run.outcome"),
                            ),
                            description="Execution duration metric.",
                        ),
                    ),
                    events=(
                        TelemetryEventSpec(
                            event_type="engine.run.started",
                            required_payload_keys=(
                                TelemetryFieldRequirement(name="engine.name"),
                                TelemetryFieldRequirement(name="run.mode"),
                            ),
                        ),
                        TelemetryEventSpec(
                            event_type="engine.run.finished",
                            required_payload_keys=(
                                TelemetryFieldRequirement(name="engine.name"),
                                TelemetryFieldRequirement(name="run.outcome"),
                            ),
                        ),
                    ),
                ),
                operations=(
                    CatalogOperation(
                        name="run",
                        result_type="run.result",
                        description="Execute a plan or materialized selection.",
                    ),
                ),
            ),
            CatalogCapability(
                name=PLAN_RUN_EXECUTION_PLANNING,
                description="Planning and explanation before execution.",
                telemetry=CapabilityTelemetry(
                    spans=(
                        TelemetrySpanSpec(
                            name="engine.plan.analyze",
                            required_attributes=(
                                TelemetryFieldRequirement(name="engine.name"),
                            ),
                        ),
                        TelemetrySpanSpec(
                            name="engine.plan.explain",
                            required_attributes=(
                                TelemetryFieldRequirement(name="engine.name"),
                            ),
                        ),
                        TelemetrySpanSpec(
                            name="engine.plan.simulate",
                            required_attributes=(
                                TelemetryFieldRequirement(name="engine.name"),
                            ),
                        ),
                    ),
                    metrics=(
                        TelemetryMetricSpec(
                            name="engine.plan.duration",
                            unit="s",
                            required_labels=(
                                TelemetryFieldRequirement(name="engine.name"),
                                TelemetryFieldRequirement(name="plan.operation"),
                            ),
                        ),
                    ),
                    events=(
                        TelemetryEventSpec(
                            event_type="engine.plan.completed",
                            required_payload_keys=(
                                TelemetryFieldRequirement(name="engine.name"),
                                TelemetryFieldRequirement(name="plan.operation"),
                            ),
                        ),
                    ),
                ),
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
                name=PLAN_RUN_EXECUTION_INPUT_VALIDATION,
                description="Validation of input or draft content before execution.",
                telemetry=CapabilityTelemetry(
                    spans=(
                        TelemetrySpanSpec(
                            name="engine.input.validate",
                            required_attributes=(
                                TelemetryFieldRequirement(name="engine.name"),
                            ),
                        ),
                    ),
                    metrics=(
                        TelemetryMetricSpec(
                            name="engine.input.validation.duration",
                            unit="s",
                            required_labels=(
                                TelemetryFieldRequirement(name="engine.name"),
                                TelemetryFieldRequirement(name="validation.outcome"),
                            ),
                        ),
                    ),
                    events=(
                        TelemetryEventSpec(
                            event_type="engine.input.validation.failed",
                            severity="error",
                            required_payload_keys=(
                                TelemetryFieldRequirement(name="engine.name"),
                                TelemetryFieldRequirement(name="error.code"),
                            ),
                        ),
                    ),
                ),
                operations=(
                    CatalogOperation(
                        name="input.validate",
                        result_type="input.validated",
                        description="Validate execution input without persistence.",
                    ),
                ),
            ),
            CatalogCapability(
                name=PLAN_RUN_EXECUTION_EXECUTION_STATUS,
                description="Status inspection for in-progress or recent executions.",
                telemetry=CapabilityTelemetry(
                    spans=(
                        TelemetrySpanSpec(
                            name="engine.execution.status.read",
                            required_attributes=(
                                TelemetryFieldRequirement(name="engine.name"),
                            ),
                        ),
                    ),
                    metrics=(
                        TelemetryMetricSpec(
                            name="engine.execution.active_runs",
                            required_labels=(
                                TelemetryFieldRequirement(name="engine.name"),
                            ),
                        ),
                    ),
                    events=(
                        TelemetryEventSpec(
                            event_type="engine.execution.status.updated",
                            required_payload_keys=(
                                TelemetryFieldRequirement(name="engine.name"),
                                TelemetryFieldRequirement(name="execution.status"),
                            ),
                        ),
                    ),
                ),
                operations=(
                    CatalogOperation(
                        name=PLAN_RUN_OP_STATUS,
                        result_type="execution.status",
                        description="Read aggregate execution status.",
                    ),
                    CatalogOperation(
                        name=PLAN_RUN_OP_CANCEL,
                        result_type="execution.cancelled",
                        description="Request cancellation of an in-progress execution.",
                    ),
                ),
            ),
            CatalogCapability(
                name=PLAN_RUN_EXECUTION_EXECUTION_STREAM,
                description="Streaming access to in-progress execution activity.",
                telemetry=CapabilityTelemetry(
                    spans=(
                        TelemetrySpanSpec(
                            name="engine.execution.subscribe",
                            required_attributes=(
                                TelemetryFieldRequirement(name="engine.name"),
                            ),
                        ),
                    ),
                ),
                operations=(
                    CatalogOperation(
                        name="execution.subscribe",
                        result_type="execution.subscription",
                        description="Open a live execution subscription.",
                    ),
                    CatalogOperation(
                        name="execution.tail",
                        result_type="execution.tail",
                        description="Read a tail of recent execution activity.",
                    ),
                ),
            ),
        ),
        tiers=(
            ConformanceTier(
                name="core",
                required_capabilities=(PLAN_RUN_EXECUTION_RUN,),
                description="Engine capable of materialized execution.",
            ),
            ConformanceTier(
                name="planned",
                required_capabilities=(
                    PLAN_RUN_EXECUTION_RUN,
                    PLAN_RUN_EXECUTION_PLANNING,
                ),
                description="Engine capable of planning and execution.",
            ),
            ConformanceTier(
                name="advanced",
                required_capabilities=(
                    PLAN_RUN_EXECUTION_RUN,
                    PLAN_RUN_EXECUTION_PLANNING,
                    PLAN_RUN_EXECUTION_INPUT_VALIDATION,
                    PLAN_RUN_EXECUTION_EXECUTION_STATUS,
                    PLAN_RUN_EXECUTION_EXECUTION_STREAM,
                ),
                description="Engine with validation, status inspection, and streaming.",
            ),
        ),
    )
)

PLAN_RUN_EXECUTION_CORE_PROFILE = CapabilityProfile(
    name=PLAN_RUN_EXECUTION_CORE_PROFILE_NAME,
    interface=PLAN_RUN_EXECUTION_INTERFACE,
    description="Reusable profile for engines that can execute materialized runs.",
    requirements=(
        CapabilityRequirement(
            capability_name=PLAN_RUN_EXECUTION_RUN,
            required_operations=("run",),
        ),
    ),
)

PLAN_RUN_EXECUTION_PLANNED_PROFILE = CapabilityProfile(
    name=PLAN_RUN_EXECUTION_PLANNED_PROFILE_NAME,
    interface=PLAN_RUN_EXECUTION_INTERFACE,
    description="Reusable profile for engines that can plan before executing.",
    requirements=(
        *PLAN_RUN_EXECUTION_CORE_PROFILE.requirements,
        CapabilityRequirement(
            capability_name=PLAN_RUN_EXECUTION_PLANNING,
            required_operations=("plan.analyze", "plan.explain", "plan.simulate"),
        ),
    ),
)

PLAN_RUN_EXECUTION_ADVANCED_PROFILE = CapabilityProfile(
    name=PLAN_RUN_EXECUTION_ADVANCED_PROFILE_NAME,
    interface=PLAN_RUN_EXECUTION_INTERFACE,
    description=(
        "Reusable profile for engines with validation, status inspection, and "
        "execution streaming."
    ),
    requirements=(
        *PLAN_RUN_EXECUTION_PLANNED_PROFILE.requirements,
        CapabilityRequirement(
            capability_name=PLAN_RUN_EXECUTION_INPUT_VALIDATION,
            required_operations=("input.validate",),
        ),
        CapabilityRequirement(
            capability_name=PLAN_RUN_EXECUTION_EXECUTION_STATUS,
            required_operations=(PLAN_RUN_OP_STATUS, PLAN_RUN_OP_CANCEL),
        ),
        CapabilityRequirement(
            capability_name=PLAN_RUN_EXECUTION_EXECUTION_STREAM,
            required_operations=("execution.subscribe", "execution.tail"),
        ),
    ),
)

__all__ = (
    "PLAN_RUN_EXECUTION_ADVANCED_PROFILE",
    "PLAN_RUN_EXECUTION_ADVANCED_PROFILE_NAME",
    "PLAN_RUN_EXECUTION_CATALOG",
    "PLAN_RUN_EXECUTION_CORE_PROFILE",
    "PLAN_RUN_EXECUTION_CORE_PROFILE_NAME",
    "PLAN_RUN_EXECUTION_EXECUTION_STATUS",
    "PLAN_RUN_EXECUTION_EXECUTION_STREAM",
    "PLAN_RUN_EXECUTION_INPUT_VALIDATION",
    "PLAN_RUN_EXECUTION_INTERFACE",
    "PLAN_RUN_EXECUTION_PLANNED_PROFILE",
    "PLAN_RUN_EXECUTION_PLANNED_PROFILE_NAME",
    "PLAN_RUN_EXECUTION_PLANNING",
    "PLAN_RUN_EXECUTION_RUN",
    "PLAN_RUN_OP_CANCEL",
    "PLAN_RUN_OP_STATUS",
)
