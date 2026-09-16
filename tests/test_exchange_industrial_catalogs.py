"""Casos portables para los catálogos industriales declarativos de CXP."""

from __future__ import annotations

import json
from importlib.resources import files

import jsonschema_rs
import pytest

from cxp.exchange import (
    CatalogStore,
    Document,
    InvalidDocumentError,
    catalog_reference,
    document_schema,
    evaluate_requirements,
    load_reference_catalog,
)
from cxp.exchange.industrial_examples import run_industrial_examples

INDUSTRIAL_SUITE = json.loads(
    files("cxp.exchange").joinpath("vectors/industrial-v1.json").read_bytes()
)


def document(document_type: str, payload: dict[str, object]) -> Document:
    return Document(
        {
            "document_type": document_type,
            "spec_version": 1,
            "payload": payload,
        },
        expected_type=document_type,
    )


def snapshot(
    catalog: Document,
    capabilities: list[dict[str, object]],
    *,
    configuration_revision: str = "configured-1",
    observed_at: str = "2026-09-16T10:00:00Z",
) -> Document:
    return document(
        "cxp.snapshot",
        {
            "provider_id": "portable-example",
            "subject_id": "configured-subject",
            "catalog": catalog_reference(catalog),
            "configuration_revision": configuration_revision,
            "observed_at": observed_at,
            "source": {"kind": "declared", "reference": "portable-example"},
            "capabilities": capabilities,
        },
    )


def requirements(catalog: Document, requirement: dict[str, object]) -> Document:
    return document(
        "cxp.requirements",
        {"catalog": catalog_reference(catalog), "requirement": requirement},
    )


def context(
    *,
    configuration_revision: str = "configured-1",
    **extra: object,
) -> Document:
    return document(
        "cxp.context",
        {
            "subject_id": "configured-subject",
            "configuration_revision": configuration_revision,
            **extra,
        },
    )


def evaluate(
    catalog: Document,
    capabilities: list[dict[str, object]],
    requirement: dict[str, object],
    *,
    configuration_revision: str = "configured-1",
    context_extra: dict[str, object] | None = None,
):
    return evaluate_requirements(
        snapshot(
            catalog,
            capabilities,
            configuration_revision=configuration_revision,
        ),
        requirements(catalog, requirement),
        context(configuration_revision=configuration_revision, **(context_extra or {})),
        catalogs=CatalogStore([catalog]),
    )


@pytest.mark.parametrize(
    ("name", "version"),
    [
        ("positioning", "1.0.0"),
        ("identification", "1.0.0"),
        ("finishing", "1.1.0"),
        ("document-processing", "1.1.0"),
    ],
)
def test_new_catalogs_are_portable_schema_documents(name: str, version: str) -> None:
    catalog = load_reference_catalog(name, version=version)
    assert jsonschema_rs.Draft202012Validator(document_schema()).is_valid(
        catalog.as_dict()
    )
    assert Document(catalog.as_dict(), expected_type="cxp.catalog") == catalog


@pytest.mark.parametrize("case", INDUSTRIAL_SUITE["cases"], ids=lambda case: case["id"])
def test_industrial_portable_vectors_are_reproducible(case: dict[str, object]) -> None:
    reference = case["catalog"]
    assert isinstance(reference, dict)
    catalog = load_reference_catalog(reference["name"], version=reference["version"])
    assert catalog_reference(catalog) == reference
    validator = jsonschema_rs.Draft202012Validator(document_schema())
    for name in ("snapshot", "requirements", "context"):
        assert validator.is_valid(case[name])
    snapshot_document = Document(case["snapshot"], expected_type="cxp.snapshot")
    requirements_document = Document(
        case["requirements"], expected_type="cxp.requirements"
    )
    context_document = Document(case["context"], expected_type="cxp.context")
    first = evaluate_requirements(
        snapshot_document,
        requirements_document,
        context_document,
        catalogs=CatalogStore([catalog]),
    )
    second = evaluate_requirements(
        snapshot_document,
        requirements_document,
        context_document,
        catalogs=CatalogStore([catalog]),
    )
    expected = case["expected"]
    assert isinstance(expected, dict)
    assert first.payload["verdict"] == expected["verdict"]
    assert [item["code"] for item in first.payload["findings"]] == expected["codes"]
    assert first.to_bytes() == second.to_bytes()


@pytest.mark.parametrize(
    ("name", "version", "sha256"),
    [
        (
            "finishing",
            "1.1.0",
            "5ef014fbeb492b463bc96ca08c0bebbf6b27574e151514c2a51cce6544f9fcc6",
        ),
        (
            "document-processing",
            "1.1.0",
            "726f82eb53db98c4bab10e4e688ce1c396c69eeffb62b859fd940b58545977ef",
        ),
    ],
)
def test_versioned_catalogs_preserve_their_default_contracts(
    name: str, version: str, sha256: str
) -> None:
    default = load_reference_catalog(name)
    published = load_reference_catalog(name, version="1.0.0")
    current = load_reference_catalog(name, version=version)
    assert default.to_bytes() == published.to_bytes()
    assert published.sha256 == sha256
    assert current.payload["identity"]["version"] == version


def test_document_processing_1_1_preserves_the_original_definition() -> None:
    original = load_reference_catalog("document-processing")
    expanded = load_reference_catalog("document-processing", version="1.1.0")
    original_capabilities = {
        item["name"]: item for item in original.payload["capabilities"]
    }
    expanded_capabilities = {
        item["name"]: item for item in expanded.payload["capabilities"]
    }
    assert (
        expanded_capabilities["document.processing"]
        == original_capabilities["document.processing"]
    )


def test_qr_reading_does_not_imply_geometric_positioning() -> None:
    catalog = load_reference_catalog("identification")
    result = evaluate(
        catalog,
        [
            {
                "name": "identification.symbol_reading",
                "support": "supported",
                "properties": {"symbologies": ["qr_code"]},
            }
        ],
        {
            "id": "read-qr",
            "operator": "contains_all",
            "capability": "identification.symbol_reading",
            "path": "/properties/symbologies",
            "values": ["qr_code"],
        },
    )
    assert result.payload["verdict"] == "compatible"
    capability_names = {item["name"] for item in catalog.payload["capabilities"]}
    assert not any(name.startswith("positioning.") for name in capability_names)


def test_identification_profiles_and_limits_are_function_specific() -> None:
    catalog = load_reference_catalog("identification")
    generation_minimum = {"value": "0.1", "unit": "mm"}
    reading_minimum = {"value": "0.5", "unit": "mm"}
    capabilities: list[dict[str, object]] = [
        {
            "name": "identification.symbol_generation",
            "support": "supported",
            "properties": {
                "symbologies": ["qr_code"],
                "content_profiles": ["opaque_payload"],
                "min_module_width": generation_minimum,
                "max_module_width": {"value": "0.4", "unit": "mm"},
                "minimum_quiet_zone_modules": "4",
            },
        },
        {
            "name": "identification.symbol_reading",
            "support": "supported",
            "properties": {
                "symbologies": ["qr_code"],
                "content_profiles": ["gs1_element_string"],
                "min_module_width": reading_minimum,
                "max_module_width": {"value": "1", "unit": "mm"},
                "minimum_quiet_zone_modules": "4",
            },
        },
        {
            "name": "identification.quality_verification",
            "support": "supported",
            "properties": {
                "symbologies": ["qr_code"],
                "quality_methods": ["iso_iec_15415"],
                "content_profiles": ["gs1_element_string"],
                "min_module_width": reading_minimum,
                "max_module_width": {"value": "1", "unit": "mm"},
                "minimum_quiet_zone_modules": "4",
            },
        },
    ]
    generated = evaluate(
        catalog,
        capabilities,
        {
            "id": "generate-opaque-payload",
            "operator": "contains_all",
            "capability": "identification.symbol_generation",
            "path": "/properties/content_profiles",
            "values": ["opaque_payload"],
        },
    )
    read = evaluate(
        catalog,
        capabilities,
        {
            "id": "read-gs1-element-string",
            "operator": "contains_all",
            "capability": "identification.symbol_reading",
            "path": "/properties/content_profiles",
            "values": ["gs1_element_string"],
        },
    )
    unreadable = evaluate(
        catalog,
        capabilities,
        {
            "id": "read-opaque-payload",
            "operator": "contains_all",
            "capability": "identification.symbol_reading",
            "path": "/properties/content_profiles",
            "values": ["opaque_payload"],
        },
    )
    generated_width = evaluate(
        catalog,
        capabilities,
        {
            "id": "generated-module-width",
            "operator": "equals",
            "capability": "identification.symbol_generation",
            "path": "/properties/min_module_width",
            "value": generation_minimum,
        },
    )
    read_width = evaluate(
        catalog,
        capabilities,
        {
            "id": "read-module-width",
            "operator": "equals",
            "capability": "identification.symbol_reading",
            "path": "/properties/min_module_width",
            "value": reading_minimum,
        },
    )
    assert generated.payload["verdict"] == "compatible"
    assert read.payload["verdict"] == "compatible"
    assert unreadable.payload["verdict"] == "incompatible"
    assert generated_width.payload["verdict"] == "compatible"
    assert read_width.payload["verdict"] == "compatible"
    catalog_capability_names = {
        item["name"] for item in catalog.payload["capabilities"]
    }
    assert "identification.content_profiles" not in catalog_capability_names
    assert "identification.physical_limits" not in catalog_capability_names


def test_detection_does_not_imply_compensation_application() -> None:
    catalog = load_reference_catalog("positioning")
    result = evaluate(
        catalog,
        [
            {
                "name": "positioning.feature_detection",
                "support": "supported",
                "properties": {"detectable_features": ["registration_mark"]},
            },
            {
                "name": "positioning.compensation_application",
                "support": "unsupported",
                "properties": {},
            },
        ],
        {
            "id": "detect-and-compensate",
            "operator": "all",
            "conditions": [
                {
                    "id": "detect",
                    "operator": "support",
                    "capability": "positioning.feature_detection",
                },
                {
                    "id": "compensate",
                    "operator": "support",
                    "capability": "positioning.compensation_application",
                },
            ],
        },
    )
    assert result.payload["verdict"] == "incompatible"
    assert [item["code"] for item in result.payload["findings"]] == [
        "requirement_satisfied",
        "unsupported_capability",
    ]


def test_transform_models_keep_size_and_scaling_as_separate_declarations() -> None:
    catalog = load_reference_catalog("positioning")
    capabilities = [
        {
            "name": "positioning.transformation_estimation",
            "support": "supported",
            "properties": {"transform_models": ["rigid_2d"]},
        }
    ]
    preserving = evaluate(
        catalog,
        capabilities,
        {
            "id": "preserves-size",
            "operator": "contains_all",
            "capability": "positioning.transformation_estimation",
            "path": "/properties/transform_models",
            "values": ["rigid_2d"],
        },
    )
    scaling = evaluate(
        catalog,
        capabilities,
        {
            "id": "permits-scaling",
            "operator": "contains_all",
            "capability": "positioning.transformation_estimation",
            "path": "/properties/transform_models",
            "values": ["similarity_2d"],
        },
    )
    assert preserving.payload["verdict"] == "compatible"
    assert scaling.payload["verdict"] == "incompatible"


def test_global_and_local_registration_and_a_camera_free_fixture_are_distinct() -> None:
    catalog = load_reference_catalog("positioning")
    result = evaluate(
        catalog,
        [
            {
                "name": "positioning.physical_referencing",
                "support": "supported",
                "properties": {
                    "reference_types": ["registration_pin"],
                    "acquisition_methods": ["mechanical_constraint"],
                    "target_scopes": ["piece"],
                },
            },
            {
                "name": "positioning.transformation_estimation",
                "support": "supported",
                "properties": {
                    "registration_extents": ["global", "local"],
                    "target_scopes": ["piece", "panel"],
                },
            },
        ],
        {
            "id": "fixture-and-extents",
            "operator": "all",
            "conditions": [
                {
                    "id": "fixture",
                    "operator": "contains_all",
                    "capability": "positioning.physical_referencing",
                    "path": "/properties/acquisition_methods",
                    "values": ["mechanical_constraint"],
                },
                {
                    "id": "extents",
                    "operator": "contains_all",
                    "capability": "positioning.transformation_estimation",
                    "path": "/properties/registration_extents",
                    "values": ["global", "local"],
                },
            ],
        },
    )
    assert result.payload["verdict"] == "compatible"


def test_finishing_processes_remain_distinct_from_each_other() -> None:
    catalog = load_reference_catalog("finishing", version="1.1.0")
    capabilities = [
        {
            "name": "finishing.through_cut",
            "support": "supported",
            "properties": {
                "configured_tool_id": "knife-a",
                "tool_type": "drag_knife",
                "methods": ["blade"],
                "material_types": ["self_adhesive_sheet"],
            },
        },
        {"name": "finishing.kiss_cut", "support": "unsupported", "properties": {}},
        {
            "name": "finishing.creasing",
            "support": "supported",
            "properties": {"methods": ["wheel"]},
        },
        {"name": "finishing.folding", "support": "unsupported", "properties": {}},
    ]
    cut_result = evaluate(
        catalog,
        capabilities,
        {
            "id": "both-cut-kinds",
            "operator": "all",
            "conditions": [
                {
                    "id": "through",
                    "operator": "support",
                    "capability": "finishing.through_cut",
                },
                {
                    "id": "kiss",
                    "operator": "support",
                    "capability": "finishing.kiss_cut",
                },
            ],
        },
    )
    fold_result = evaluate(
        catalog,
        capabilities,
        {
            "id": "crease-and-fold",
            "operator": "all",
            "conditions": [
                {
                    "id": "crease",
                    "operator": "support",
                    "capability": "finishing.creasing",
                },
                {
                    "id": "fold",
                    "operator": "support",
                    "capability": "finishing.folding",
                },
            ],
        },
    )
    assert cut_result.payload["verdict"] == "incompatible"
    assert fold_result.payload["verdict"] == "incompatible"


def test_document_acceptance_does_not_imply_finishing_interpretation() -> None:
    catalog = load_reference_catalog("document-processing", version="1.1.0")
    result = evaluate(
        catalog,
        [
            {
                "name": "document.acceptance",
                "support": "supported",
                "properties": {"input_formats": ["pdf-x-4"]},
            },
            {
                "name": "document.production_interpretation",
                "support": "unsupported",
                "properties": {},
            },
        ],
        {
            "id": "accepted-and-interpreted",
            "operator": "all",
            "conditions": [
                {
                    "id": "accepted",
                    "operator": "contains_all",
                    "capability": "document.acceptance",
                    "path": "/properties/input_formats",
                    "values": ["pdf-x-4"],
                },
                {
                    "id": "interpreted",
                    "operator": "support",
                    "capability": "document.production_interpretation",
                },
            ],
        },
    )
    assert result.payload["verdict"] == "incompatible"


def test_alternative_configurations_are_evaluated_separately() -> None:
    catalog = load_reference_catalog("finishing", version="1.1.0")
    requirement = {
        "id": "wide-through-cut",
        "operator": "range",
        "capability": "finishing.through_cut",
        "path": "/properties/max_width",
        "minimum": {"value": "500", "unit": "mm"},
    }
    wide = evaluate(
        catalog,
        [
            {
                "name": "finishing.through_cut",
                "support": "supported",
                "properties": {"max_width": {"value": "600", "unit": "mm"}},
            }
        ],
        requirement,
        configuration_revision="wide-tool",
    )
    narrow = evaluate(
        catalog,
        [
            {
                "name": "finishing.through_cut",
                "support": "supported",
                "properties": {"max_width": {"value": "300", "unit": "mm"}},
            }
        ],
        requirement,
        configuration_revision="narrow-tool",
    )
    assert wide.payload["verdict"] == "compatible"
    assert narrow.payload["verdict"] == "incompatible"


@pytest.mark.parametrize(
    ("support", "properties", "operator", "expected"),
    [
        ("supported", {}, "contains_all", "indeterminate"),
        ("unsupported", {}, "support", "incompatible"),
        ("accepted_noop", {}, "support", "incompatible"),
    ],
)
def test_absence_negative_support_and_noop_stay_distinct(
    support: str,
    properties: dict[str, object],
    operator: str,
    expected: str,
) -> None:
    catalog = load_reference_catalog("positioning")
    requirement: dict[str, object] = {
        "id": "effective-detection",
        "operator": operator,
        "capability": "positioning.feature_detection",
    }
    if operator == "contains_all":
        requirement.update(
            path="/properties/detectable_features", values=["registration_mark"]
        )
    result = evaluate(
        catalog,
        [
            {
                "name": "positioning.feature_detection",
                "support": support,
                "properties": properties,
            }
        ],
        requirement,
    )
    assert result.payload["verdict"] == expected


def test_context_time_and_configuration_do_not_mix_declarations() -> None:
    catalog = load_reference_catalog("positioning")
    capabilities = [
        {
            "name": "positioning.feature_detection",
            "support": "supported",
            "properties": {},
        }
    ]
    requirement = {
        "id": "detection",
        "operator": "support",
        "capability": "positioning.feature_detection",
    }
    stale = evaluate(
        catalog,
        capabilities,
        requirement,
        context_extra={"as_of": "2026-09-16T10:02:00Z", "max_age_seconds": 60},
    )
    snapshot_document = snapshot(catalog, capabilities)
    mismatch = evaluate_requirements(
        snapshot_document,
        requirements(catalog, requirement),
        context(configuration_revision="other-configuration"),
        catalogs=CatalogStore([catalog]),
    )
    assert stale.payload["verdict"] == "indeterminate"
    assert mismatch.payload["verdict"] == "indeterminate"
    assert [item["code"] for item in mismatch.payload["findings"]] == [
        "configuration_mismatch"
    ]


def test_invalid_properties_and_document_units_are_rejected() -> None:
    catalog = load_reference_catalog("positioning")
    with pytest.raises(InvalidDocumentError) as error:
        snapshot(
            catalog,
            [
                {
                    "name": "positioning.feature_detection",
                    "support": "supported",
                    "properties": {
                        "minimum_feature_size": {"value": "1", "unit": "cm"}
                    },
                }
            ],
        )
    assert error.value.issues[0].code == "schema_violation"
    invalid_snapshot = snapshot(
        catalog,
        [
            {
                "name": "positioning.feature_detection",
                "support": "supported",
                "properties": {"not_a_capability_property": "unexpected"},
            }
        ],
    )
    with pytest.raises(InvalidDocumentError) as property_error:
        CatalogStore([catalog]).validate_snapshot(invalid_snapshot)
    assert property_error.value.issues[0].code == "unknown_property"
    contrast_snapshot = snapshot(
        catalog,
        [
            {
                "name": "positioning.feature_detection",
                "support": "supported",
                "properties": {"minimum_contrast_ratio": "1.5"},
            }
        ],
    )
    with pytest.raises(InvalidDocumentError) as contrast_error:
        CatalogStore([catalog]).validate_snapshot(contrast_snapshot)
    assert contrast_error.value.issues[0].code == "unknown_property"


def test_documents_hashes_and_evaluations_are_reproducible() -> None:
    catalog = load_reference_catalog("identification")
    capabilities = [
        {
            "name": "identification.symbol_reading",
            "support": "supported",
            "properties": {"symbologies": ["data_matrix", "qr_code"]},
        }
    ]
    requirement = {
        "id": "read-two-symbols",
        "operator": "contains_all",
        "capability": "identification.symbol_reading",
        "path": "/properties/symbologies",
        "values": ["qr_code", "data_matrix"],
    }
    first = evaluate(catalog, capabilities, requirement)
    second = evaluate(catalog, capabilities, requirement)
    assert first.to_bytes() == second.to_bytes()
    assert first.sha256 == second.sha256


def test_examples_are_packaged_and_cover_all_verdicts() -> None:
    assert set(run_industrial_examples().values()) == {
        "compatible",
        "incompatible",
        "indeterminate",
    }
    assert files("cxp.exchange").joinpath("catalogs/positioning.json").is_file()
    identification = files("cxp.exchange").joinpath("catalogs/identification.json")
    assert json.loads(identification.read_bytes())
