from __future__ import annotations

import msgspec

from cxp.catalogs.base import (
    CapabilityCatalog,
    CapabilityProfile,
    CapabilityRequirement,
    CapabilityTelemetry,
    CatalogCapability,
    CatalogOperation,
    ConformanceTier,
    TelemetryFieldRequirement,
    TelemetrySpanSpec,
    register_catalog,
)

COSECHA_REPORTER_INTERFACE = "cosecha/reporter"

COSECHA_REPORTER_REPORT_LIFECYCLE = "report_lifecycle"
COSECHA_REPORTER_RESULT_PROJECTION = "result_projection"
COSECHA_REPORTER_ARTIFACT_OUTPUT = "artifact_output"
COSECHA_REPORTER_STRUCTURED_OUTPUT = "structured_output"
COSECHA_REPORTER_HUMAN_OUTPUT = "human_output"

COSECHA_REPORTER_START = "reporter.start"
COSECHA_REPORTER_ADD_TEST = "reporter.add_test"
COSECHA_REPORTER_ADD_TEST_RESULT = "reporter.add_test_result"
COSECHA_REPORTER_PRINT_REPORT = "reporter.print_report"

COSECHA_REPORTER_CORE_TIER = "core"
COSECHA_REPORTER_ARTIFACT_TIER = "artifact"
COSECHA_REPORTER_STRUCTURED_TIER = "structured"
COSECHA_REPORTER_HUMAN_TIER = "human"

COSECHA_REPORTER_CORE_PROFILE_NAME = "cosecha-reporter-core"
COSECHA_REPORTER_ARTIFACT_PROFILE_NAME = "cosecha-reporter-artifact"
COSECHA_REPORTER_STRUCTURED_PROFILE_NAME = "cosecha-reporter-structured"
COSECHA_REPORTER_HUMAN_PROFILE_NAME = "cosecha-reporter-human"

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
            "Canonical catalog for Cosecha reporters with explicit human, "
            "structured and artifact-writing contracts."
        ),
        capabilities=(
            CatalogCapability(
                name=COSECHA_REPORTER_REPORT_LIFECYCLE,
                description="Reporter startup and final report lifecycle.",
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
                description="Project test starts and results into reporter-specific views.",
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
                description="Write a final artifact or persisted report output.",
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
            CatalogCapability(
                name=COSECHA_REPORTER_STRUCTURED_OUTPUT,
                description="Emit machine-readable structured output.",
                metadata_schema=ArtifactOutputMetadata,
                operations=(
                    CatalogOperation(
                        name=COSECHA_REPORTER_PRINT_REPORT,
                        result_type="none",
                    ),
                ),
            ),
            CatalogCapability(
                name=COSECHA_REPORTER_HUMAN_OUTPUT,
                description="Emit human-oriented rendered output.",
                metadata_schema=ArtifactOutputMetadata,
                operations=(
                    CatalogOperation(
                        name=COSECHA_REPORTER_PRINT_REPORT,
                        result_type="none",
                    ),
                ),
            ),
        ),
        tiers=(
            ConformanceTier(
                name=COSECHA_REPORTER_CORE_TIER,
                required_capabilities=(
                    COSECHA_REPORTER_REPORT_LIFECYCLE,
                    COSECHA_REPORTER_RESULT_PROJECTION,
                ),
                description="Minimal reporter contract.",
            ),
            ConformanceTier(
                name=COSECHA_REPORTER_ARTIFACT_TIER,
                required_capabilities=(
                    COSECHA_REPORTER_REPORT_LIFECYCLE,
                    COSECHA_REPORTER_RESULT_PROJECTION,
                    COSECHA_REPORTER_ARTIFACT_OUTPUT,
                ),
                description="Reporter that writes a final artifact or persisted output.",
            ),
            ConformanceTier(
                name=COSECHA_REPORTER_STRUCTURED_TIER,
                required_capabilities=(
                    COSECHA_REPORTER_REPORT_LIFECYCLE,
                    COSECHA_REPORTER_RESULT_PROJECTION,
                    COSECHA_REPORTER_ARTIFACT_OUTPUT,
                    COSECHA_REPORTER_STRUCTURED_OUTPUT,
                ),
                description="Machine-readable structured reporter.",
            ),
            ConformanceTier(
                name=COSECHA_REPORTER_HUMAN_TIER,
                required_capabilities=(
                    COSECHA_REPORTER_REPORT_LIFECYCLE,
                    COSECHA_REPORTER_RESULT_PROJECTION,
                    COSECHA_REPORTER_HUMAN_OUTPUT,
                ),
                description="Human-oriented rendered reporter.",
            ),
        ),
    )
)

COSECHA_REPORTER_CORE_PROFILE = CapabilityProfile(
    name=COSECHA_REPORTER_CORE_PROFILE_NAME,
    interface=COSECHA_REPORTER_INTERFACE,
    requirements=(
        CapabilityRequirement(
            capability_name=COSECHA_REPORTER_REPORT_LIFECYCLE,
            required_operations=(
                COSECHA_REPORTER_START,
                COSECHA_REPORTER_PRINT_REPORT,
            ),
        ),
        CapabilityRequirement(
            capability_name=COSECHA_REPORTER_RESULT_PROJECTION,
            required_operations=(
                COSECHA_REPORTER_ADD_TEST,
                COSECHA_REPORTER_ADD_TEST_RESULT,
            ),
        ),
    ),
    description="Core reporter projection profile.",
)

COSECHA_REPORTER_ARTIFACT_PROFILE = CapabilityProfile(
    name=COSECHA_REPORTER_ARTIFACT_PROFILE_NAME,
    interface=COSECHA_REPORTER_INTERFACE,
    requirements=(
        CapabilityRequirement(
            capability_name=COSECHA_REPORTER_ARTIFACT_OUTPUT,
            required_metadata_keys=(
                "output_kind",
                "artifact_formats",
            ),
        ),
    ),
    description="Artifact-writing reporter profile.",
)

COSECHA_REPORTER_STRUCTURED_PROFILE = CapabilityProfile(
    name=COSECHA_REPORTER_STRUCTURED_PROFILE_NAME,
    interface=COSECHA_REPORTER_INTERFACE,
    requirements=(
        CapabilityRequirement(
            capability_name=COSECHA_REPORTER_STRUCTURED_OUTPUT,
            required_metadata_keys=("output_kind",),
        ),
    ),
    description="Structured reporter profile.",
)

COSECHA_REPORTER_HUMAN_PROFILE = CapabilityProfile(
    name=COSECHA_REPORTER_HUMAN_PROFILE_NAME,
    interface=COSECHA_REPORTER_INTERFACE,
    requirements=(
        CapabilityRequirement(
            capability_name=COSECHA_REPORTER_HUMAN_OUTPUT,
            required_metadata_keys=("output_kind",),
        ),
    ),
    description="Human-oriented reporter profile.",
)

__all__ = (
    "ArtifactOutputMetadata",
    "COSECHA_REPORTER_ADD_TEST",
    "COSECHA_REPORTER_ADD_TEST_RESULT",
    "COSECHA_REPORTER_ARTIFACT_OUTPUT",
    "COSECHA_REPORTER_ARTIFACT_PROFILE",
    "COSECHA_REPORTER_ARTIFACT_PROFILE_NAME",
    "COSECHA_REPORTER_ARTIFACT_TIER",
    "COSECHA_REPORTER_CATALOG",
    "COSECHA_REPORTER_CORE_PROFILE",
    "COSECHA_REPORTER_CORE_PROFILE_NAME",
    "COSECHA_REPORTER_CORE_TIER",
    "COSECHA_REPORTER_HUMAN_OUTPUT",
    "COSECHA_REPORTER_HUMAN_PROFILE",
    "COSECHA_REPORTER_HUMAN_PROFILE_NAME",
    "COSECHA_REPORTER_HUMAN_TIER",
    "COSECHA_REPORTER_INTERFACE",
    "COSECHA_REPORTER_PRINT_REPORT",
    "COSECHA_REPORTER_REPORT_LIFECYCLE",
    "COSECHA_REPORTER_RESULT_PROJECTION",
    "COSECHA_REPORTER_START",
    "COSECHA_REPORTER_STRUCTURED_OUTPUT",
    "COSECHA_REPORTER_STRUCTURED_PROFILE",
    "COSECHA_REPORTER_STRUCTURED_PROFILE_NAME",
    "COSECHA_REPORTER_STRUCTURED_TIER",
    "ResultProjectionMetadata",
)
