from cxp import (
    COSECHA_ENGINE_CATALOG,
    COSECHA_ENGINE_DEFINITION_KNOWLEDGE,
    COSECHA_ENGINE_DEPENDENCY_KNOWLEDGE,
    COSECHA_ENGINE_DRAFT_VALIDATION,
    COSECHA_ENGINE_INTERFACE,
    COSECHA_ENGINE_LIFECYCLE,
    COSECHA_ENGINE_ON_DEMAND_DEFINITION_MATERIALIZATION,
    COSECHA_ENGINE_PLAN_EXPLANATION,
    COSECHA_ENGINE_SELECTION_LABELS,
    COSECHA_ENGINE_STATIC_DEFINITION_DISCOVERY,
    COSECHA_ENGINE_TEST_EXECUTE,
    COSECHA_ENGINE_TEST_LIFECYCLE,
    COSECHA_ENGINE_TEST_PHASE,
    COSECHA_PLUGIN_CATALOG,
    COSECHA_PLUGIN_INTERFACE,
    COSECHA_PLUGIN_TELEMETRY_EXPORT,
    COSECHA_REPORTER_ARTIFACT_OUTPUT,
    COSECHA_REPORTER_CATALOG,
    COSECHA_REPORTER_INTERFACE,
    COSECHA_REPORTER_RESULT_PROJECTION,
    CapabilityDescriptor,
    CapabilityOperationBinding,
    ComponentCapabilitySnapshot,
    ComponentIdentity,
    TelemetrySnapshot,
    TelemetrySpan,
    get_catalog,
)


def test_cosecha_catalogs_are_registered() -> None:
    assert get_catalog(COSECHA_ENGINE_INTERFACE) is COSECHA_ENGINE_CATALOG
    assert get_catalog(COSECHA_REPORTER_INTERFACE) is COSECHA_REPORTER_CATALOG
    assert get_catalog(COSECHA_PLUGIN_INTERFACE) is COSECHA_PLUGIN_CATALOG


def test_cosecha_engine_catalog_validates_normalized_snapshot() -> None:
    snapshot = ComponentCapabilitySnapshot(
        component_name='gherkin',
        identity=ComponentIdentity(
            interface=COSECHA_ENGINE_INTERFACE,
            provider='gherkin',
            version='1',
        ),
        capabilities=(
            CapabilityDescriptor(
                name=COSECHA_ENGINE_LIFECYCLE,
                level='supported',
                operations=(
                    CapabilityOperationBinding('collect'),
                    CapabilityOperationBinding('session.start'),
                    CapabilityOperationBinding('session.finish'),
                ),
            ),
            CapabilityDescriptor(
                name=COSECHA_ENGINE_TEST_LIFECYCLE,
                level='supported',
                operations=(
                    CapabilityOperationBinding('test.start'),
                    CapabilityOperationBinding('test.finish'),
                    CapabilityOperationBinding(COSECHA_ENGINE_TEST_EXECUTE),
                    CapabilityOperationBinding(COSECHA_ENGINE_TEST_PHASE),
                ),
            ),
            CapabilityDescriptor(
                name=COSECHA_ENGINE_DRAFT_VALIDATION,
                level='supported',
                operations=(CapabilityOperationBinding('draft.validate'),),
            ),
            CapabilityDescriptor(
                name=COSECHA_ENGINE_SELECTION_LABELS,
                level='supported',
                metadata={
                    'label_sources': ['feature_tag', 'scenario_tag'],
                    'supports_glob_matching': True,
                },
            ),
            CapabilityDescriptor(
                name=COSECHA_ENGINE_DEFINITION_KNOWLEDGE,
                level='supported',
                metadata={
                    'knowledge_origin_kinds': [
                        'project_definitions',
                        'project_registry',
                        'library_definitions',
                    ],
                    'knowledge_scopes': ['project', 'library'],
                    'supports_fresh_resolution': True,
                    'supports_knowledge_base_projection': True,
                },
                operations=(
                    CapabilityOperationBinding('definition.resolve'),
                    CapabilityOperationBinding('knowledge.query_tests'),
                    CapabilityOperationBinding('knowledge.query_definitions'),
                    CapabilityOperationBinding('knowledge.query_registry_items'),
                ),
            ),
            CapabilityDescriptor(
                name=COSECHA_ENGINE_PLAN_EXPLANATION,
                level='supported',
                operations=(
                    CapabilityOperationBinding('plan.analyze'),
                    CapabilityOperationBinding('plan.explain'),
                    CapabilityOperationBinding('plan.simulate'),
                ),
            ),
            CapabilityDescriptor(
                name=COSECHA_ENGINE_STATIC_DEFINITION_DISCOVERY,
                level='supported',
                metadata={'discovery_backends': ['ast']},
                operations=(
                    CapabilityOperationBinding('knowledge.query_tests'),
                    CapabilityOperationBinding('knowledge.query_definitions'),
                ),
            ),
            CapabilityDescriptor(
                name=COSECHA_ENGINE_ON_DEMAND_DEFINITION_MATERIALIZATION,
                level='supported',
                metadata={'materialization_granularities': ['file']},
                operations=(CapabilityOperationBinding('definition.resolve'),),
            ),
            CapabilityDescriptor(
                name=COSECHA_ENGINE_DEPENDENCY_KNOWLEDGE,
                level='supported',
                operations=(
                    CapabilityOperationBinding('dependencies.describe'),
                ),
            ),
        ),
    )

    assert COSECHA_ENGINE_CATALOG.is_component_snapshot_compliant(snapshot)


def test_cosecha_selection_labels_rejects_plan_operations() -> None:
    snapshot = ComponentCapabilitySnapshot(
        component_name='gherkin',
        identity=ComponentIdentity(
            interface=COSECHA_ENGINE_INTERFACE,
            provider='gherkin',
            version='1',
        ),
        capabilities=(
            CapabilityDescriptor(
                name=COSECHA_ENGINE_SELECTION_LABELS,
                level='supported',
                metadata={
                    'label_sources': ['feature_tag'],
                },
                operations=(
                    CapabilityOperationBinding('plan.analyze'),
                ),
            ),
        ),
    )

    validation = COSECHA_ENGINE_CATALOG.validate_component_snapshot(snapshot)

    assert validation.is_valid() is False
    assert len(validation.unknown_operations) == 1
    assert validation.unknown_operations[0].capability_name == COSECHA_ENGINE_SELECTION_LABELS
    assert validation.unknown_operations[0].operation_names == ('plan.analyze',)


def test_cosecha_engine_catalog_rejects_legacy_dependency_operation_name() -> None:
    snapshot = ComponentCapabilitySnapshot(
        component_name='gherkin',
        identity=ComponentIdentity(
            interface=COSECHA_ENGINE_INTERFACE,
            provider='gherkin',
            version='1',
        ),
        capabilities=(
            CapabilityDescriptor(
                name=COSECHA_ENGINE_DEPENDENCY_KNOWLEDGE,
                level='supported',
                operations=(
                    CapabilityOperationBinding('engine_dependencies.describe'),
                ),
            ),
        ),
    )

    validation = COSECHA_ENGINE_CATALOG.validate_component_snapshot(snapshot)

    assert validation.is_valid() is False
    assert len(validation.unknown_operations) == 1
    assert (
        validation.unknown_operations[0].capability_name
        == COSECHA_ENGINE_DEPENDENCY_KNOWLEDGE
    )
    assert validation.unknown_operations[0].operation_names == (
        'engine_dependencies.describe',
    )


def test_cosecha_engine_catalog_reports_invalid_definition_metadata() -> None:
    snapshot = ComponentCapabilitySnapshot(
        component_name='pytest',
        identity=ComponentIdentity(
            interface=COSECHA_ENGINE_INTERFACE,
            provider='pytest',
            version='1',
        ),
        capabilities=(
            CapabilityDescriptor(
                name=COSECHA_ENGINE_DEFINITION_KNOWLEDGE,
                level='supported',
                metadata={
                    'knowledge_origin_kinds': ['project_definitions'],
                    'knowledge_scopes': ['project'],
                    'supports_fresh_resolution': 'yes',
                    'supports_knowledge_base_projection': True,
                },
                operations=(CapabilityOperationBinding('definition.resolve'),),
            ),
        ),
    )

    validation = COSECHA_ENGINE_CATALOG.validate_component_snapshot(snapshot)

    assert validation.is_valid() is False
    assert validation.invalid_metadata == (COSECHA_ENGINE_DEFINITION_KNOWLEDGE,)


def test_cosecha_engine_catalog_rejects_unknown_test_lifecycle_operation() -> None:
    snapshot = ComponentCapabilitySnapshot(
        component_name='gherkin',
        identity=ComponentIdentity(
            interface=COSECHA_ENGINE_INTERFACE,
            provider='gherkin',
            version='1',
        ),
        capabilities=(
            CapabilityDescriptor(
                name=COSECHA_ENGINE_TEST_LIFECYCLE,
                level='supported',
                operations=(
                    CapabilityOperationBinding('test.retry'),
                ),
            ),
        ),
    )

    validation = COSECHA_ENGINE_CATALOG.validate_component_snapshot(snapshot)

    assert validation.is_valid() is False
    assert len(validation.unknown_operations) == 1
    assert (
        validation.unknown_operations[0].capability_name
        == COSECHA_ENGINE_TEST_LIFECYCLE
    )
    assert validation.unknown_operations[0].operation_names == (
        'test.retry',
    )


def test_cosecha_reporter_and_plugin_catalogs_validate_snapshots() -> None:
    reporter_snapshot = ComponentCapabilitySnapshot(
        component_name='json',
        identity=ComponentIdentity(
            interface=COSECHA_REPORTER_INTERFACE,
            provider='json',
            version='1',
        ),
        capabilities=(
            CapabilityDescriptor(
                name='report_lifecycle',
                level='supported',
                operations=(
                    CapabilityOperationBinding('reporter.start'),
                    CapabilityOperationBinding('reporter.print_report'),
                ),
            ),
            CapabilityDescriptor(
                name=COSECHA_REPORTER_RESULT_PROJECTION,
                level='supported',
                metadata={'supports_engine_specific_projection': True},
                operations=(
                    CapabilityOperationBinding('reporter.add_test'),
                    CapabilityOperationBinding('reporter.add_test_result'),
                ),
            ),
            CapabilityDescriptor(
                name=COSECHA_REPORTER_ARTIFACT_OUTPUT,
                level='supported',
                metadata={
                    'output_kind': 'structured',
                    'artifact_formats': ['json'],
                    'supports_engine_specific_projection': True,
                },
                operations=(
                    CapabilityOperationBinding('reporter.print_report'),
                ),
            ),
        ),
    )
    plugin_snapshot = ComponentCapabilitySnapshot(
        component_name='TelemetryPlugin',
        identity=ComponentIdentity(
            interface=COSECHA_PLUGIN_INTERFACE,
            provider='TelemetryPlugin',
            version='1',
        ),
        capabilities=(
            CapabilityDescriptor(
                name='plugin_lifecycle',
                level='supported',
                operations=(
                    CapabilityOperationBinding('plugin.initialize'),
                    CapabilityOperationBinding('plugin.start'),
                    CapabilityOperationBinding('plugin.finish'),
                    CapabilityOperationBinding('plugin.after_session_closed'),
                ),
            ),
            CapabilityDescriptor(
                name='surface_publication',
                level='supported',
                metadata={'provided_surfaces': []},
            ),
            CapabilityDescriptor(
                name='capability_requirements',
                level='supported',
                metadata={'required_capabilities': []},
            ),
            CapabilityDescriptor(
                name=COSECHA_PLUGIN_TELEMETRY_EXPORT,
                level='supported',
                metadata={'output_formats': ['jsonl']},
            ),
        ),
    )

    assert COSECHA_REPORTER_CATALOG.is_component_snapshot_compliant(
        reporter_snapshot
    )
    assert COSECHA_PLUGIN_CATALOG.is_component_snapshot_compliant(
        plugin_snapshot
    )


def test_cosecha_catalogs_validate_span_only_telemetry() -> None:
    engine_snapshot = TelemetrySnapshot(
        provider_id='gherkin',
        spans=(
            TelemetrySpan(
                trace_id='trace-1',
                span_id='collect',
                parent_span_id=None,
                name='engine.collect',
                start_time=1.0,
                end_time=1.1,
                attributes={
                    'cosecha.engine.name': 'gherkin',
                    'cosecha.operation.name': 'collect',
                    'cosecha.outcome': 'success',
                },
            ),
            TelemetrySpan(
                trace_id='trace-1',
                span_id='phase',
                parent_span_id='collect',
                name='engine.test.phase',
                start_time=1.1,
                end_time=1.2,
                attributes={
                    'cosecha.engine.name': 'gherkin',
                    'cosecha.operation.name': 'test.phase',
                    'cosecha.outcome': 'success',
                    'cosecha.node.id': 'node-1',
                    'cosecha.node.stable_id': 'stable-1',
                    'cosecha.phase': 'run',
                },
            ),
        ),
    )
    reporter_snapshot = TelemetrySnapshot(
        provider_id='json',
        spans=(
            TelemetrySpan(
                trace_id='trace-1',
                span_id='write',
                parent_span_id=None,
                name='reporter.output.write',
                start_time=1.0,
                end_time=1.1,
                attributes={
                    'cosecha.reporter.name': 'json',
                    'cosecha.reporter.output_kind': 'structured',
                },
            ),
        ),
    )
    plugin_snapshot = TelemetrySnapshot(
        provider_id='TelemetryPlugin',
        spans=(
            TelemetrySpan(
                trace_id='trace-1',
                span_id='sink',
                parent_span_id=None,
                name='plugin.telemetry.sink.start',
                start_time=1.0,
                end_time=1.1,
                attributes={'cosecha.plugin.name': 'TelemetryPlugin'},
            ),
        ),
    )

    assert COSECHA_ENGINE_CATALOG.is_telemetry_snapshot_compliant(
        engine_snapshot,
        ('engine_lifecycle', 'test_lifecycle'),
    )
    assert COSECHA_REPORTER_CATALOG.is_telemetry_snapshot_compliant(
        reporter_snapshot,
        (COSECHA_REPORTER_ARTIFACT_OUTPUT,),
    )
    assert COSECHA_PLUGIN_CATALOG.is_telemetry_snapshot_compliant(
        plugin_snapshot,
        (COSECHA_PLUGIN_TELEMETRY_EXPORT,),
    )
