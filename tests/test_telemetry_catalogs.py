from pytest import raises

from cxp import (
    MONGODB_CATALOG,
    PLAN_RUN_EXECUTION_CATALOG,
    PLAYWRIGHT_BROWSER_CATALOG,
    CapabilityCatalog,
    CapabilityTelemetry,
    CatalogCapability,
    CatalogRegistry,
    TelemetryEvent,
    TelemetryEventSpec,
    TelemetryFieldRequirement,
    TelemetryMetric,
    TelemetryMetricSpec,
    TelemetrySnapshot,
    TelemetrySpan,
    TelemetrySpanSpec,
)


def _browser_payload(**payload: object) -> dict[str, object]:
    return {
        "cxp.resource.name": "playwright-provider",
        "cxp.resource.kind": "browser",
        **payload,
    }


def _mongodb_payload(**payload: object) -> dict[str, object]:
    return {
        "cxp.resource.name": "example-mongodb",
        "cxp.resource.kind": "database",
        **payload,
    }


def test_execution_engine_catalog_exposes_capability_telemetry() -> None:
    assert PLAN_RUN_EXECUTION_CATALOG.telemetry_span_names("run") == (
        "engine.run.execute",
    )
    assert PLAN_RUN_EXECUTION_CATALOG.telemetry_metric_names("planning") == (
        "engine.plan.duration",
    )
    assert PLAN_RUN_EXECUTION_CATALOG.telemetry_event_types("execution_status") == (
        "engine.execution.status.updated",
    )


def test_mongodb_catalog_exposes_capability_specific_telemetry_names() -> None:
    assert MONGODB_CATALOG.telemetry_span_names("aggregation") == (
        "db.client.aggregate",
    )
    assert MONGODB_CATALOG.telemetry_metric_names("search") == (
        "db.client.search.duration",
    )
    assert MONGODB_CATALOG.telemetry_event_types("vector_search") == (
        "db.client.vector_search.completed",
    )


def test_playwright_catalog_exposes_capability_specific_telemetry_names() -> None:
    assert PLAYWRIGHT_BROWSER_CATALOG.telemetry_span_names("browser_lifecycle") == (
        "browser.launch",
        "browser.close",
    )
    assert PLAYWRIGHT_BROWSER_CATALOG.telemetry_event_types("context_management") == (
        "browser.context.created",
        "browser.context.create_failed",
        "browser.context.closed",
    )
    assert PLAYWRIGHT_BROWSER_CATALOG.telemetry_span_names("page_navigation") == (
        "browser.page.navigate",
    )
    assert PLAYWRIGHT_BROWSER_CATALOG.telemetry_metric_names("dom_interaction") == (
        "browser.action.duration",
    )
    assert PLAYWRIGHT_BROWSER_CATALOG.telemetry_span_names("network_observation") == (
        "browser.request.observe",
        "browser.response.observe",
    )
    assert PLAYWRIGHT_BROWSER_CATALOG.telemetry_event_types("network_observation") == (
        "browser.request.observed",
        "browser.response.observed",
        "browser.request.failed",
        "browser.response.failed",
    )
    assert PLAYWRIGHT_BROWSER_CATALOG.telemetry_event_types("dialog_handling") == (
        "browser.dialog.opened",
        "browser.dialog.handled",
    )


def test_playwright_catalog_validates_lifecycle_and_context_telemetry() -> None:
    snapshot = TelemetrySnapshot(
        provider_id="playwright-provider",
        spans=(
            TelemetrySpan(
                trace_id="trace-1",
                span_id="launch-span",
                parent_span_id=None,
                name="browser.launch",
                start_time=1.0,
                end_time=1.4,
                    attributes={
                        **_browser_payload(
                            **{
                                "browser.engine": "playwright",
                                "browser.headless": True,
                            }
                        ),
                    },
            ),
            TelemetrySpan(
                trace_id="trace-1",
                span_id="context-span",
                parent_span_id=None,
                name="browser.context.create",
                start_time=1.4,
                end_time=1.6,
                    attributes={
                        **_browser_payload(**{"browser.engine": "playwright"}),
                    },
            ),
            TelemetrySpan(
                trace_id="trace-1",
                span_id="close-span",
                parent_span_id=None,
                name="browser.context.close",
                start_time=2.0,
                end_time=2.1,
                    attributes={
                        **_browser_payload(
                            **{
                                "browser.engine": "playwright",
                                "browser.context.id": "ctx-1",
                            }
                        ),
                    },
            ),
        ),
        metrics=(
            TelemetryMetric(
                name="browser.launch.duration",
                value=0.4,
                unit="s",
                    labels={
                        **_browser_payload(
                            **{
                                "browser.engine": "playwright",
                                "browser.headless": "true",
                                "browser.outcome": "success",
                            }
                        ),
                    },
            ),
            TelemetryMetric(
                name="browser.context.create.duration",
                value=0.2,
                unit="s",
                    labels={
                        **_browser_payload(
                            **{
                                "browser.engine": "playwright",
                                "browser.outcome": "success",
                            }
                        ),
                    },
            ),
            TelemetryMetric(
                name="browser.context.close.duration",
                value=0.1,
                unit="s",
                    labels={
                        **_browser_payload(
                            **{
                                "browser.engine": "playwright",
                                "browser.outcome": "success",
                            }
                        ),
                    },
            ),
        ),
        events=(
                TelemetryEvent(
                    event_type="browser.session.launched",
                    payload=_browser_payload(
                        **{
                            "browser.engine": "playwright",
                            "browser.headless": True,
                            "browser.outcome": "success",
                        }
                    ),
                ),
                TelemetryEvent(
                    event_type="browser.context.created",
                    payload=_browser_payload(
                        **{
                            "browser.engine": "playwright",
                            "browser.context.id": "ctx-1",
                            "browser.outcome": "success",
                        }
                    ),
                ),
                TelemetryEvent(
                    event_type="browser.context.closed",
                    payload=_browser_payload(
                        **{
                            "browser.engine": "playwright",
                            "browser.context.id": "ctx-1",
                            "browser.outcome": "success",
                        }
                    ),
                ),
            ),
        )

    assert PLAYWRIGHT_BROWSER_CATALOG.is_telemetry_snapshot_compliant(
        snapshot,
        ("browser_lifecycle", "context_management"),
    )


def test_playwright_catalog_reports_invalid_launch_failure_severity() -> None:
    snapshot = TelemetrySnapshot(
        provider_id="playwright-provider",
        events=(
            TelemetryEvent(
                event_type="browser.session.launch_failed",
                payload={
                    "browser.engine": "playwright",
                    "browser.headless": False,
                },
            ),
        ),
    )

    validation = PLAYWRIGHT_BROWSER_CATALOG.validate_telemetry_snapshot(
        snapshot,
        ("browser_lifecycle",),
    )

    assert validation.is_valid() is False
    assert validation.invalid_event_severities == (
        "browser.session.launch_failed: expected 'error', got 'info'",
    )


def test_playwright_catalog_validates_network_request_and_response_telemetry() -> None:
    snapshot = TelemetrySnapshot(
        provider_id="playwright-provider",
        spans=(
            TelemetrySpan(
                trace_id="trace-1",
                span_id="request-span",
                parent_span_id=None,
                name="browser.request.observe",
                start_time=1.0,
                end_time=1.2,
                    attributes={
                        **_browser_payload(
                            **{
                                "browser.engine": "playwright",
                                "browser.page.id": "page-1",
                                "browser.network.phase": "request",
                                "browser.request.url.host": "example.com",
                            }
                        ),
                    },
            ),
            TelemetrySpan(
                trace_id="trace-1",
                span_id="response-span",
                parent_span_id=None,
                name="browser.response.observe",
                start_time=1.2,
                end_time=1.5,
                    attributes={
                        **_browser_payload(
                            **{
                                "browser.engine": "playwright",
                                "browser.page.id": "page-1",
                                "browser.network.phase": "response",
                                "browser.request.url.host": "example.com",
                            }
                        ),
                    },
            ),
        ),
        metrics=(
            TelemetryMetric(
                name="browser.request.duration",
                value=0.2,
                unit="s",
                    labels={
                        **_browser_payload(
                            **{
                                "browser.engine": "playwright",
                                "browser.network.phase": "request",
                                "browser.outcome": "success",
                            }
                        ),
                    },
            ),
            TelemetryMetric(
                name="browser.response.duration",
                value=0.3,
                unit="s",
                    labels={
                        **_browser_payload(
                            **{
                                "browser.engine": "playwright",
                                "browser.network.phase": "response",
                                "browser.outcome": "success",
                            }
                        ),
                    },
            ),
        ),
        events=(
            TelemetryEvent(
                event_type="browser.request.observed",
                    payload=_browser_payload(
                        **{
                            "browser.engine": "playwright",
                            "browser.page.id": "page-1",
                            "browser.network.phase": "request",
                            "browser.request.url.host": "example.com",
                            "browser.outcome": "success",
                        }
                    ),
                ),
                TelemetryEvent(
                    event_type="browser.response.observed",
                    payload=_browser_payload(
                        **{
                            "browser.engine": "playwright",
                            "browser.page.id": "page-1",
                            "browser.network.phase": "response",
                            "browser.request.url.host": "example.com",
                            "browser.outcome": "success",
                        }
                    ),
                ),
            ),
        )

    assert PLAYWRIGHT_BROWSER_CATALOG.is_telemetry_snapshot_compliant(
        snapshot,
        ("network_observation",),
    )


def test_execution_engine_catalog_validates_telemetry_snapshot() -> None:
    snapshot = TelemetrySnapshot(
        provider_id="pytest-engine",
        spans=(
            TelemetrySpan(
                trace_id="trace-1",
                span_id="span-run",
                parent_span_id=None,
                name="engine.run.execute",
                start_time=1.0,
                end_time=2.0,
                attributes={
                    "engine.name": "pytest",
                    "run.mode": "live",
                },
            ),
            TelemetrySpan(
                trace_id="trace-1",
                span_id="span-plan",
                parent_span_id=None,
                name="engine.plan.analyze",
                start_time=2.0,
                end_time=2.2,
                attributes={"engine.name": "pytest"},
            ),
        ),
        metrics=(
            TelemetryMetric(
                name="engine.run.duration",
                value=1.0,
                unit="s",
                labels={
                    "engine.name": "pytest",
                    "run.outcome": "passed",
                },
            ),
        ),
        events=(
            TelemetryEvent(
                event_type="engine.run.finished",
                payload={
                    "engine.name": "pytest",
                    "run.outcome": "passed",
                },
            ),
        ),
    )

    assert PLAN_RUN_EXECUTION_CATALOG.is_telemetry_snapshot_compliant(
        snapshot,
        ("run", "planning"),
    )


def test_execution_engine_catalog_reports_invalid_metric_unit() -> None:
    snapshot = TelemetrySnapshot(
        provider_id="pytest-engine",
        metrics=(
            TelemetryMetric(
                name="engine.run.duration",
                value=1000,
                unit="ms",
                labels={
                    "engine.name": "pytest",
                    "run.outcome": "passed",
                },
            ),
        ),
    )

    validation = PLAN_RUN_EXECUTION_CATALOG.validate_telemetry_snapshot(
        snapshot,
        ("run",),
    )

    assert validation.is_valid() is False
    assert validation.invalid_metric_units == (
        "engine.run.duration: expected 's', got 'ms'",
    )


def test_telemetry_subset_validation_ignores_extra_signals_by_default() -> None:
    snapshot = TelemetrySnapshot(
        provider_id="pytest-engine",
        spans=(
            TelemetrySpan(
                trace_id="trace-1",
                span_id="span-run",
                parent_span_id=None,
                name="engine.run.execute",
                start_time=1.0,
                end_time=2.0,
                attributes={
                    "engine.name": "pytest",
                    "run.mode": "live",
                },
            ),
            TelemetrySpan(
                trace_id="trace-1",
                span_id="span-live",
                parent_span_id=None,
                name="engine.execution.subscribe",
                start_time=2.0,
                end_time=2.1,
                attributes={"engine.name": "pytest"},
            ),
        ),
    )

    assert PLAN_RUN_EXECUTION_CATALOG.is_telemetry_snapshot_compliant(
        snapshot,
        ("run",),
    )


def test_telemetry_subset_validation_can_reject_extra_signals_when_strict() -> None:
    snapshot = TelemetrySnapshot(
        provider_id="pytest-engine",
        events=(
            TelemetryEvent(
                event_type="engine.execution.status.updated",
                payload={
                    "engine.name": "pytest",
                    "execution.status": "running",
                },
            ),
        ),
    )

    validation = PLAN_RUN_EXECUTION_CATALOG.validate_telemetry_snapshot(
        snapshot,
        ("run",),
        reject_unknown_signals=True,
    )

    assert validation.is_valid() is False
    assert validation.unknown_events == ("engine.execution.status.updated",)


def test_mongodb_catalog_validates_shared_operation_telemetry() -> None:
    snapshot = TelemetrySnapshot(
        provider_id="example-mongodb",
        spans=(
            TelemetrySpan(
                trace_id="trace-1",
                span_id="span-1",
                parent_span_id=None,
                name="db.client.operation",
                start_time=1.0,
                end_time=1.5,
                attributes={
                    **_mongodb_payload(
                        **{
                            "db.system.name": "mongodb",
                            "db.operation.name": "find",
                            "db.namespace.name": "users.accounts",
                        }
                    ),
                },
            ),
        ),
        metrics=(
            TelemetryMetric(
                name="db.client.operation.duration",
                value=0.5,
                unit="s",
                labels={
                    **_mongodb_payload(
                        **{
                            "db.system.name": "mongodb",
                            "db.operation.name": "find",
                            "db.operation.outcome": "success",
                        }
                    ),
                },
            ),
        ),
        events=(
            TelemetryEvent(
                event_type="db.client.operation.completed",
                payload=_mongodb_payload(
                    **{
                        "db.system.name": "mongodb",
                        "db.operation.name": "find",
                        "db.namespace.name": "users.accounts",
                        "db.operation.outcome": "success",
                    }
                ),
            ),
        ),
    )

    assert MONGODB_CATALOG.is_telemetry_snapshot_compliant(
        snapshot,
        ("read", "write"),
    )


def test_mongodb_catalog_reports_missing_required_event_payload_keys() -> None:
    snapshot = TelemetrySnapshot(
        provider_id="example-mongodb",
        events=(
            TelemetryEvent(
                event_type="db.client.topology.discovered",
                payload=_mongodb_payload(
                    **{
                        "db.system.name": "mongodb",
                        "db.topology.type": "replica_set",
                    }
                ),
            ),
        ),
    )

    validation = MONGODB_CATALOG.validate_telemetry_snapshot(
        snapshot,
        ("topology_discovery",),
    )

    assert validation.is_valid() is False
    assert validation.missing_event_payload_keys == (
        "db.client.topology.discovered.db.topology.server.count",
    )


def test_playwright_catalog_validates_navigation_action_and_wait_telemetry() -> None:
    snapshot = TelemetrySnapshot(
        provider_id="playwright-provider",
        spans=(
            TelemetrySpan(
                trace_id="trace-1",
                span_id="nav-span",
                parent_span_id=None,
                name="browser.page.navigate",
                start_time=1.0,
                end_time=2.0,
                attributes={
                    **_browser_payload(
                        **{
                            "browser.engine": "playwright",
                            "browser.context.id": "ctx-1",
                            "browser.page.id": "page-1",
                            "browser.url.host": "example.com",
                            "browser.url.path_template": "/signup",
                        }
                    ),
                },
            ),
            TelemetrySpan(
                trace_id="trace-1",
                span_id="action-span",
                parent_span_id=None,
                name="browser.action",
                start_time=2.0,
                end_time=2.2,
                attributes={
                    **_browser_payload(
                        **{
                            "browser.engine": "playwright",
                            "browser.page.id": "page-1",
                            "browser.action.name": "click",
                            "browser.locator.kind": "role",
                        }
                    ),
                },
            ),
            TelemetrySpan(
                trace_id="trace-1",
                span_id="wait-span",
                parent_span_id=None,
                name="browser.wait",
                start_time=2.2,
                end_time=2.5,
                attributes={
                    **_browser_payload(
                        **{
                            "browser.engine": "playwright",
                            "browser.page.id": "page-1",
                            "browser.wait.condition": "response",
                        }
                    ),
                },
            ),
        ),
        metrics=(
            TelemetryMetric(
                name="browser.navigation.duration",
                value=1.0,
                unit="s",
                labels={
                    **_browser_payload(
                        **{
                            "browser.engine": "playwright",
                            "browser.url.host": "example.com",
                            "browser.outcome": "success",
                        }
                    ),
                },
            ),
            TelemetryMetric(
                name="browser.action.duration",
                value=0.2,
                unit="s",
                labels={
                    **_browser_payload(
                        **{
                            "browser.engine": "playwright",
                            "browser.action.name": "click",
                            "browser.outcome": "success",
                        }
                    ),
                },
            ),
            TelemetryMetric(
                name="browser.wait.duration",
                value=0.3,
                unit="s",
                labels={
                    **_browser_payload(
                        **{
                            "browser.engine": "playwright",
                            "browser.wait.condition": "response",
                            "browser.outcome": "success",
                        }
                    ),
                },
            ),
        ),
        events=(
            TelemetryEvent(
                event_type="browser.navigation.completed",
                payload=_browser_payload(
                    **{
                        "browser.engine": "playwright",
                        "browser.page.id": "page-1",
                        "browser.url.host": "example.com",
                        "browser.outcome": "success",
                    }
                ),
            ),
            TelemetryEvent(
                event_type="browser.action.completed",
                payload=_browser_payload(
                    **{
                        "browser.engine": "playwright",
                        "browser.page.id": "page-1",
                        "browser.action.name": "click",
                        "browser.outcome": "success",
                    }
                ),
            ),
            TelemetryEvent(
                event_type="browser.wait.completed",
                payload=_browser_payload(
                    **{
                        "browser.engine": "playwright",
                        "browser.page.id": "page-1",
                        "browser.wait.condition": "response",
                        "browser.outcome": "success",
                    }
                ),
            ),
        ),
    )

    assert PLAYWRIGHT_BROWSER_CATALOG.is_telemetry_snapshot_compliant(
        snapshot,
        ("page_navigation", "dom_interaction", "wait_conditions"),
    )


def test_playwright_catalog_reports_missing_network_payload_keys() -> None:
    snapshot = TelemetrySnapshot(
        provider_id="playwright-provider",
        events=(
            TelemetryEvent(
                event_type="browser.request.failed",
                severity="error",
                payload=_browser_payload(
                    **{
                        "browser.engine": "playwright",
                        "browser.page.id": "page-1",
                        "browser.network.phase": "response",
                    }
                ),
            ),
        ),
    )

    validation = PLAYWRIGHT_BROWSER_CATALOG.validate_telemetry_snapshot(
        snapshot,
        ("network_observation",),
    )

    assert validation.is_valid() is False
    assert validation.missing_event_payload_keys == (
        "browser.request.failed.browser.request.url.host",
    )


def test_mongodb_catalog_validates_aggregation_search_and_vector_telemetry() -> None:
    snapshot = TelemetrySnapshot(
        provider_id="example-mongodb",
        spans=(
            TelemetrySpan(
                trace_id="trace-agg",
                span_id="span-agg",
                parent_span_id=None,
                name="db.client.aggregate",
                start_time=1.0,
                end_time=1.4,
                attributes={
                    **_mongodb_payload(
                        **{
                            "db.system.name": "mongodb",
                            "db.operation.name": "aggregate",
                            "db.namespace.name": "users.accounts",
                            "db.pipeline.stage.count": 3,
                        }
                    ),
                },
            ),
            TelemetrySpan(
                trace_id="trace-search",
                span_id="span-search",
                parent_span_id=None,
                name="db.client.search",
                start_time=2.0,
                end_time=2.2,
                attributes={
                    **_mongodb_payload(
                        **{
                            "db.system.name": "mongodb",
                            "db.operation.name": "aggregate",
                            "db.namespace.name": "users.accounts",
                            "db.pipeline.stage.name": "$search",
                            "db.search.operator": "compound",
                        }
                    ),
                },
            ),
            TelemetrySpan(
                trace_id="trace-vector",
                span_id="span-vector",
                parent_span_id=None,
                name="db.client.vector_search",
                start_time=3.0,
                end_time=3.3,
                attributes={
                    **_mongodb_payload(
                        **{
                            "db.system.name": "mongodb",
                            "db.operation.name": "aggregate",
                            "db.namespace.name": "users.accounts",
                            "db.pipeline.stage.name": "$vectorSearch",
                            "db.vector_search.similarity": "cosine",
                        }
                    ),
                },
            ),
        ),
        metrics=(
            TelemetryMetric(
                name="db.client.aggregate.duration",
                value=0.4,
                unit="s",
                labels={
                    **_mongodb_payload(
                        **{
                            "db.system.name": "mongodb",
                            "db.operation.name": "aggregate",
                            "db.operation.outcome": "success",
                        }
                    ),
                },
            ),
            TelemetryMetric(
                name="db.client.search.duration",
                value=0.2,
                unit="s",
                labels={
                    **_mongodb_payload(
                        **{
                            "db.system.name": "mongodb",
                            "db.operation.name": "aggregate",
                            "db.operation.outcome": "success",
                            "db.pipeline.stage.name": "$search",
                        }
                    ),
                },
            ),
            TelemetryMetric(
                name="db.client.vector_search.duration",
                value=0.3,
                unit="s",
                labels={
                    **_mongodb_payload(
                        **{
                            "db.system.name": "mongodb",
                            "db.operation.name": "aggregate",
                            "db.operation.outcome": "success",
                            "db.vector_search.similarity": "cosine",
                        }
                    ),
                },
            ),
        ),
        events=(
            TelemetryEvent(
                event_type="db.client.aggregate.completed",
                payload=_mongodb_payload(
                    **{
                        "db.system.name": "mongodb",
                        "db.operation.name": "aggregate",
                        "db.namespace.name": "users.accounts",
                        "db.operation.outcome": "success",
                        "db.pipeline.stage.count": 3,
                    }
                ),
            ),
            TelemetryEvent(
                event_type="db.client.search.completed",
                payload=_mongodb_payload(
                    **{
                        "db.system.name": "mongodb",
                        "db.operation.name": "aggregate",
                        "db.namespace.name": "users.accounts",
                        "db.operation.outcome": "success",
                        "db.pipeline.stage.name": "$search",
                        "db.search.operator": "compound",
                    }
                ),
            ),
            TelemetryEvent(
                event_type="db.client.vector_search.completed",
                payload=_mongodb_payload(
                    **{
                        "db.system.name": "mongodb",
                        "db.operation.name": "aggregate",
                        "db.namespace.name": "users.accounts",
                        "db.operation.outcome": "success",
                        "db.pipeline.stage.name": "$vectorSearch",
                        "db.vector_search.similarity": "cosine",
                    }
                ),
            ),
        ),
    )

    assert MONGODB_CATALOG.is_telemetry_snapshot_compliant(
        snapshot,
        ("aggregation", "search", "vector_search"),
    )


def test_mongodb_catalog_requires_stage_specific_search_metadata() -> None:
    snapshot = TelemetrySnapshot(
        provider_id="example-mongodb",
        events=(
            TelemetryEvent(
                event_type="db.client.search.completed",
                payload=_mongodb_payload(
                    **{
                        "db.system.name": "mongodb",
                        "db.operation.name": "aggregate",
                        "db.namespace.name": "users.accounts",
                        "db.operation.outcome": "success",
                        "db.pipeline.stage.name": "$search",
                    }
                ),
            ),
        ),
    )

    validation = MONGODB_CATALOG.validate_telemetry_snapshot(
        snapshot,
        ("search",),
    )

    assert validation.is_valid() is False
    assert validation.missing_event_payload_keys == (
        "db.client.search.completed.db.search.operator",
    )


def test_mongodb_catalog_validates_consumer_style_search_snapshot() -> None:
    snapshot = TelemetrySnapshot(
        provider_id="example-mongodb",
        spans=(
            TelemetrySpan(
                trace_id="trace-search",
                span_id="span-search",
                parent_span_id=None,
                name="db.client.search",
                start_time=1.0,
                end_time=1.3,
                attributes={
                    **_mongodb_payload(
                        **{
                            "db.system.name": "mongodb",
                            "db.operation.name": "aggregate",
                            "db.namespace.name": "docs.articles",
                            "db.pipeline.stage.name": "$search",
                            "db.search.operator": "compound",
                        }
                    ),
                },
            ),
        ),
        metrics=(
            TelemetryMetric(
                name="db.client.search.duration",
                value=0.3,
                unit="s",
                labels={
                    **_mongodb_payload(
                        **{
                            "db.system.name": "mongodb",
                            "db.operation.name": "aggregate",
                            "db.operation.outcome": "success",
                            "db.pipeline.stage.name": "$search",
                        }
                    ),
                },
            ),
        ),
        events=(
            TelemetryEvent(
                event_type="db.client.search.completed",
                payload=_mongodb_payload(
                    **{
                        "db.system.name": "mongodb",
                        "db.operation.name": "aggregate",
                        "db.namespace.name": "docs.articles",
                        "db.operation.outcome": "success",
                        "db.pipeline.stage.name": "$search",
                        "db.search.operator": "compound",
                    }
                ),
            ),
        ),
    )

    assert MONGODB_CATALOG.is_telemetry_snapshot_compliant(snapshot, ("search",))


def test_catalog_registry_rejects_conflicting_shared_metric_definitions() -> None:
    registry = CatalogRegistry()

    with raises(ValueError, match="Conflicting telemetry metric definition"):
        registry.register(
            CapabilityCatalog(
                interface="execution/conflict-metric",
                capabilities=(
                    CatalogCapability(
                        name="run",
                        telemetry=CapabilityTelemetry(
                            metrics=(
                                TelemetryMetricSpec(
                                    name="engine.run.duration",
                                    unit="s",
                                    required_labels=(
                                        TelemetryFieldRequirement(name="engine.name"),
                                    ),
                                ),
                            ),
                        ),
                    ),
                    CatalogCapability(
                        name="planning",
                        telemetry=CapabilityTelemetry(
                            metrics=(
                                TelemetryMetricSpec(
                                    name="engine.run.duration",
                                    unit="ms",
                                    required_labels=(
                                        TelemetryFieldRequirement(name="engine.name"),
                                    ),
                                ),
                            ),
                        ),
                    ),
                ),
            )
        )


def test_catalog_registry_rejects_conflicting_shared_event_definitions() -> None:
    registry = CatalogRegistry()

    with raises(ValueError, match="Conflicting telemetry event definition"):
        registry.register(
            CapabilityCatalog(
                interface="execution/conflict-event",
                capabilities=(
                    CatalogCapability(
                        name="run",
                        telemetry=CapabilityTelemetry(
                            events=(
                                TelemetryEventSpec(
                                    event_type="engine.run.finished",
                                    severity="info",
                                    required_payload_keys=(
                                        TelemetryFieldRequirement(name="run.outcome"),
                                    ),
                                ),
                            ),
                        ),
                    ),
                    CatalogCapability(
                        name="planning",
                        telemetry=CapabilityTelemetry(
                            events=(
                                TelemetryEventSpec(
                                    event_type="engine.run.finished",
                                    severity="error",
                                    required_payload_keys=(
                                        TelemetryFieldRequirement(name="run.outcome"),
                                    ),
                                ),
                            ),
                        ),
                    ),
                ),
            )
        )


def test_catalog_registry_rejects_conflicting_shared_span_definitions() -> None:
    registry = CatalogRegistry()

    with raises(ValueError, match="Conflicting telemetry span definition"):
        registry.register(
            CapabilityCatalog(
                interface="execution/conflict-span",
                capabilities=(
                    CatalogCapability(
                        name="run",
                        telemetry=CapabilityTelemetry(
                            spans=(
                                TelemetrySpanSpec(
                                    name="engine.run.execute",
                                    required_attributes=(
                                        TelemetryFieldRequirement(name="engine.name"),
                                    ),
                                ),
                            ),
                        ),
                    ),
                    CatalogCapability(
                        name="planning",
                        telemetry=CapabilityTelemetry(
                            spans=(
                                TelemetrySpanSpec(
                                    name="engine.run.execute",
                                    required_attributes=(
                                        TelemetryFieldRequirement(name="engine.name"),
                                        TelemetryFieldRequirement(name="run.mode"),
                                    ),
                                ),
                            ),
                        ),
                    ),
                ),
            )
        )
