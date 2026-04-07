from cxp.capabilities import CapabilityMatrix
from cxp.catalogs import TelemetryFieldRequirement
from cxp.catalogs.interfaces.database.mongodb import _telemetry_fields
from cxp.integration import evaluate_capability_matrix_against_catalog
from cxp.telemetry import TelemetryBuffer


def test_mongodb_telemetry_fields_deduplication() -> None:
    f1 = TelemetryFieldRequirement(name="test.field")
    f2 = TelemetryFieldRequirement(name="test.field")
    groups = ((f1,), (f2,))

    result = _telemetry_fields(*groups)

    assert len(result) == 1
    assert result[0].name == "test.field"


def test_integration_abstract_validation_error() -> None:
    from cxp.catalogs.base import CapabilityCatalog, register_catalog

    abstract_iface = "test/always-abstract"
    cat = register_catalog(
        CapabilityCatalog(interface=abstract_iface, abstract=True),
        replace=True,
    )
    matrix = CapabilityMatrix(capabilities=())

    report = evaluate_capability_matrix_against_catalog(
        offered_interface=abstract_iface,
        capability_matrix=matrix,
        catalog=cat,
    )

    assert not report.compliant
    assert "Abstract catalog" in report.reason


def test_telemetry_buffer_dropped_items() -> None:
    buffer = TelemetryBuffer(provider_id="test", max_items=1, overflow_policy="drop_oldest")

    assert buffer.dropped_items == 0

    buffer.record_metric("m1", 1)
    buffer.record_metric("m2", 2)

    assert buffer.dropped_items == 1

    snapshot = buffer.flush()

    assert snapshot.dropped_items == 1
    assert buffer.dropped_items == 0
