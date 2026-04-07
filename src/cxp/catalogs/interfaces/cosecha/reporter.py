from __future__ import annotations

import msgspec

from cxp.catalogs.base import (
    CapabilityCatalog,
    CapabilityTelemetry,
    CatalogCapability,
    CatalogOperation,
    TelemetryFieldRequirement,
    TelemetrySpanSpec,
    register_catalog,
)

COSECHA_REPORTER_INTERFACE = "cosecha/reporter"

COSECHA_REPORTER_REPORT_LIFECYCLE = "report_lifecycle"
COSECHA_REPORTER_RESULT_PROJECTION = "result_projection"
COSECHA_REPORTER_ARTIFACT_OUTPUT = "artifact_output"

COSECHA_REPORTER_START = "reporter.start"
COSECHA_REPORTER_ADD_TEST = "reporter.add_test"
COSECHA_REPORTER_ADD_TEST_RESULT = "reporter.add_test_result"
COSECHA_REPORTER_PRINT_REPORT = "reporter.print_report"

_REPORTER_NAME_FIELD = TelemetryFieldRequirement(name="cosecha.reporter.name")
_REPORTER_OUTPUT_KIND_FIELD = TelemetryFieldRequirement(
    name="cosecha.reporter.output_kind"
)


class ResultProjectionMetadata(msgspec.Struct, frozen=True):
    supports_engine_specific_projection: bool = False


class ArtifactOutputMetadata(msgspec.Struct, frozen=True):
    output_kind: str
    artifact_formats: tuple[str, ...] = ()
    supports_engine_specific_projection: bool = False


def _reporter_span(
    name: str,
    *required_attributes: TelemetryFieldRequirement,
    description: str,
) -> CapabilityTelemetry:
    return CapabilityTelemetry(
        spans=(
            TelemetrySpanSpec(
                name=name,
                required_attributes=required_attributes,
                description=description,
            ),
        ),
    )


COSECHA_REPORTER_CATALOG = register_catalog(
    CapabilityCatalog(
        interface=COSECHA_REPORTER_INTERFACE,
        description=(
            "Canonical catalog for Cosecha reporters that project test "
            "results and optionally write human or structured artifacts."
        ),
        capabilities=(
            CatalogCapability(
                name=COSECHA_REPORTER_REPORT_LIFECYCLE,
                description="Reporter startup and teardown lifecycle.",
                telemetry=CapabilityTelemetry(
                    spans=(
                        TelemetrySpanSpec(
                            name="reporter.start",
                            required_attributes=(
                                _REPORTER_NAME_FIELD,
                                _REPORTER_OUTPUT_KIND_FIELD,
                            ),
                        ),
                        TelemetrySpanSpec(
                            name="reporter.print_report",
                            required_attributes=(
                                _REPORTER_NAME_FIELD,
                                _REPORTER_OUTPUT_KIND_FIELD,
                            ),
                        ),
                    ),
                ),
                operations=(
                    CatalogOperation(
                        name=COSECHA_REPORTER_START,
                        result_type="none",
                    ),
                    CatalogOperation(
                        name=COSECHA_REPORTER_PRINT_REPORT,
                        result_type="none",
                    ),
                ),
            ),
            CatalogCapability(
                name=COSECHA_REPORTER_RESULT_PROJECTION,
                description=(
                    "Project test starts and results into reporter-specific "
                    "views."
                ),
                metadata_schema=ResultProjectionMetadata,
                telemetry=CapabilityTelemetry(
                    spans=(
                        TelemetrySpanSpec(
                            name="reporter.add_test",
                            required_attributes=(
                                _REPORTER_NAME_FIELD,
                                _REPORTER_OUTPUT_KIND_FIELD,
                            ),
                        ),
                        TelemetrySpanSpec(
                            name="reporter.add_test_result",
                            required_attributes=(
                                _REPORTER_NAME_FIELD,
                                _REPORTER_OUTPUT_KIND_FIELD,
                            ),
                        ),
                    ),
                ),
                operations=(
                    CatalogOperation(
                        name=COSECHA_REPORTER_ADD_TEST,
                        result_type="none",
                    ),
                    CatalogOperation(
                        name=COSECHA_REPORTER_ADD_TEST_RESULT,
                        result_type="none",
                    ),
                ),
            ),
            CatalogCapability(
                name=COSECHA_REPORTER_ARTIFACT_OUTPUT,
                description="Write console or file-based report artifacts.",
                metadata_schema=ArtifactOutputMetadata,
                telemetry=_reporter_span(
                    "reporter.output.write",
                    _REPORTER_NAME_FIELD,
                    _REPORTER_OUTPUT_KIND_FIELD,
                    description="Reporter output-write span.",
                ),
                operations=(
                    CatalogOperation(
                        name=COSECHA_REPORTER_PRINT_REPORT,
                        result_type="none",
                    ),
                ),
            ),
        ),
    )
)

__all__ = (
    "COSECHA_REPORTER_ADD_TEST",
    "COSECHA_REPORTER_ADD_TEST_RESULT",
    "COSECHA_REPORTER_ARTIFACT_OUTPUT",
    "COSECHA_REPORTER_CATALOG",
    "COSECHA_REPORTER_INTERFACE",
    "COSECHA_REPORTER_PRINT_REPORT",
    "COSECHA_REPORTER_REPORT_LIFECYCLE",
    "COSECHA_REPORTER_RESULT_PROJECTION",
    "COSECHA_REPORTER_START",
)
