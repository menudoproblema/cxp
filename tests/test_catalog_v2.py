"""Catalog v2 conformance with independently authored outcomes."""

from __future__ import annotations

import json
import subprocess
import sys
from copy import deepcopy
from fractions import Fraction
from importlib.resources import files

import jsonschema_rs
import pytest
from jsonschema import Draft202012Validator

from cxp.exchange import (
    CatalogStore,
    Document,
    ExchangeAgreement,
    InvalidDocumentError,
    catalog_reference,
    document_schema,
    evaluate_requirements,
    negotiate_exchange,
)

VECTORS = json.loads(
    files("cxp.exchange").joinpath("vectors/catalog-v2.json").read_text()
)


def source(locator: str) -> dict[str, str]:
    return {
        "reference": "org.example:equipment-contract",
        "revision": "2026-09-26",
        "locator": locator,
    }


def catalog_data() -> dict:
    return {
        "document_type": "cxp.catalog",
        "spec_version": 2,
        "payload": {
            "identity": {
                "namespace": "org.example",
                "name": "device",
                "version": "2.0.0",
            },
            "owner": "Example",
            "source": source("catalog"),
            "capabilities": [
                {
                    "name": "device.print",
                    "source": source("device.print"),
                    "properties": {
                        "modes": {
                            "kind": "string_set",
                            "domain": {
                                "mode": "closed",
                                "values": ["duplex", "simplex"],
                            },
                            "source": source("device.print/modes"),
                        },
                        "width": {
                            "kind": "quantity",
                            "dimension": "length",
                            "bounds": {
                                "minimum": {"value": "100", "unit": "mm"},
                                "maximum": {"value": "400", "unit": "mm"},
                                "maximum_inclusive": False,
                            },
                            "source": source("device.print/width"),
                        },
                        "copies": {
                            "kind": "integer",
                            "bounds": {"minimum": 1, "maximum": 100},
                            "source": source("device.print/copies"),
                        },
                        "label": {
                            "kind": "string",
                            "domain": {"mode": "open"},
                            "source": source("device.print/label"),
                        },
                    },
                    "operations": [
                        {
                            "name": "print",
                            "result_type": "org.example:print-result",
                            "source": source("device.print/print"),
                        }
                    ],
                }
            ],
        },
    }


def document(kind: str, payload: dict, version: int = 1) -> Document:
    return Document(
        {"document_type": kind, "spec_version": version, "payload": payload},
        expected_type=kind,
    )


def inputs(*, modes: list[str] | None = None, width: str = "200") -> tuple:
    catalog = Document(catalog_data(), expected_type="cxp.catalog")
    reference = catalog_reference(catalog)
    properties: dict = {"width": {"value": width, "unit": "mm"}, "copies": 2}
    if modes is not None:
        properties["modes"] = modes
    snapshot = document(
        "cxp.snapshot",
        {
            "provider_id": "example",
            "subject_id": "printer",
            "catalog": reference,
            "configuration_revision": "rev-1",
            "observed_at": "2026-09-26T10:00:00Z",
            "source": {"kind": "observed", "reference": "report-sha256"},
            "capabilities": [
                {
                    "name": "device.print",
                    "support": "supported",
                    "properties": properties,
                }
            ],
        },
    )
    requirements = document(
        "cxp.requirements",
        {
            "catalog": reference,
            "requirement": {
                "id": "duplex",
                "operator": "contains_all",
                "capability": "device.print",
                "path": "/properties/modes",
                "values": ["duplex"],
            },
        },
    )
    context = document(
        "cxp.context",
        {
            "subject_id": "printer",
            "configuration_revision": "rev-1",
            "accepted_sources": ["observed"],
        },
        version=2,
    )
    return catalog, snapshot, requirements, context


def test_catalog_v2_is_a_separate_schema_and_v1_remains_stable() -> None:
    value = catalog_data()
    schema = document_schema(document_type="cxp.catalog", spec_version=2)
    assert jsonschema_rs.Draft202012Validator(schema).is_valid(value)
    assert not jsonschema_rs.Draft202012Validator(document_schema()).is_valid(value)
    assert Document(value, expected_type="cxp.catalog").spec_version == 2


def test_closed_domain_canonical_order_and_observation() -> None:
    first = catalog_data()
    second = deepcopy(first)
    second["payload"]["capabilities"][0]["properties"]["modes"]["domain"][
        "values"
    ].reverse()
    assert (
        Document(first, expected_type="cxp.catalog").to_bytes()
        == Document(second, expected_type="cxp.catalog").to_bytes()
    )
    catalog, snapshot, requirements, context = inputs(modes=["duplex"])
    assert (
        evaluate_requirements(
            snapshot, requirements, context, catalogs=CatalogStore([catalog])
        ).payload["verdict"]
        == "compatible"
    )
    catalog, snapshot, requirements, context = inputs(modes=["simplex"])
    assert (
        evaluate_requirements(
            snapshot, requirements, context, catalogs=CatalogStore([catalog])
        ).payload["verdict"]
        == "incompatible"
    )
    catalog, snapshot, requirements, context = inputs()
    assert (
        evaluate_requirements(
            snapshot, requirements, context, catalogs=CatalogStore([catalog])
        ).payload["verdict"]
        == "indeterminate"
    )


@pytest.mark.parametrize(
    "value,code",
    [
        (["simplex", "unknown"], "value_outside_domain"),
        (["duplex", "duplex"], "schema_violation"),
    ],
)
def test_invalid_observed_domain_is_a_document_error(
    value: list[str], code: str
) -> None:
    if len(value) != len(set(value)):
        _, snapshot, _, _ = inputs(modes=["duplex"])
        data = snapshot.as_dict()
        data["payload"]["capabilities"][0]["properties"]["modes"] = value
        with pytest.raises(InvalidDocumentError) as error:
            Document(data, expected_type="cxp.snapshot")
    else:
        catalog, snapshot, requirements, context = inputs(modes=value)
        with pytest.raises(InvalidDocumentError) as error:
            evaluate_requirements(
                snapshot, requirements, context, catalogs=CatalogStore([catalog])
            )
    assert error.value.issues[0].code == code


def test_invalid_required_domain_is_rejected_before_evaluation() -> None:
    catalog, snapshot, requirements, context = inputs(modes=["duplex"])
    data = requirements.as_dict()
    data["payload"]["requirement"]["values"] = ["unknown"]
    requirements = Document(data, expected_type="cxp.requirements")
    with pytest.raises(InvalidDocumentError) as error:
        evaluate_requirements(
            snapshot, requirements, context, catalogs=CatalogStore([catalog])
        )
    assert error.value.issues[0].code == "value_outside_domain"


@pytest.mark.parametrize("width", ["99.999", "400", "401"])
def test_observed_numeric_outside_catalog_bounds_is_invalid(width: str) -> None:
    catalog, snapshot, requirements, context = inputs(modes=["duplex"], width=width)
    with pytest.raises(InvalidDocumentError) as error:
        evaluate_requirements(
            snapshot, requirements, context, catalogs=CatalogStore([catalog])
        )
    assert error.value.issues[0].code in {
        "below_catalog_minimum",
        "above_catalog_maximum",
    }


def test_inverted_catalog_bounds_are_invalid() -> None:
    value = catalog_data()
    value["payload"]["capabilities"][0]["properties"]["copies"]["bounds"]["minimum"] = (
        101
    )
    with pytest.raises(InvalidDocumentError) as error:
        Document(value, expected_type="cxp.catalog")
    assert error.value.issues[0].code == "invalid_catalog_bounds"


def test_duplicate_closed_domain_member_has_stable_diagnostic() -> None:
    value = catalog_data()
    value["payload"]["capabilities"][0]["properties"]["modes"]["domain"]["values"] = [
        "duplex",
        "duplex",
    ]
    with pytest.raises(InvalidDocumentError) as error:
        Document(value, expected_type="cxp.catalog")
    assert error.value.issues[0].code == "duplicate_domain_value"


def test_catalog_v2_requires_element_sources_and_explicit_string_domain() -> None:
    value = catalog_data()
    del value["payload"]["capabilities"][0]["properties"]["label"]["domain"]
    assert not jsonschema_rs.Draft202012Validator(
        document_schema(document_type="cxp.catalog", spec_version=2)
    ).is_valid(value)
    with pytest.raises(InvalidDocumentError):
        Document(value, expected_type="cxp.catalog")
    value = catalog_data()
    del value["payload"]["capabilities"][0]["operations"][0]["source"]
    with pytest.raises(InvalidDocumentError):
        Document(value, expected_type="cxp.catalog")


def test_catalog_v2_negotiates_explicitly_without_old_reader_fallback() -> None:
    request = document(
        "cxp.exchange_request",
        {
            "protocol_version": 2,
            "formats": [{"document_type": "cxp.catalog", "spec_versions": [1, 2]}],
        },
    )
    response = negotiate_exchange(request)
    assert response.payload["formats"][0]["spec_version"] == 2
    agreement = ExchangeAgreement(request, response)
    catalog = Document(catalog_data(), expected_type="cxp.catalog")
    assert (
        agreement.decode(agreement.encode(catalog), expected_type="cxp.catalog").sha256
        == catalog.sha256
    )
    old_request = document(
        "cxp.exchange_request",
        {
            "protocol_version": 2,
            "formats": [{"document_type": "cxp.catalog", "spec_versions": [1]}],
        },
    )
    old_agreement = ExchangeAgreement(old_request, negotiate_exchange(old_request))
    with pytest.raises(Exception) as error:
        old_agreement.encode(catalog)
    assert error.value.issues[0].code == "format_not_negotiated"


def test_catalog_v2_cli_matches_python_and_exposes_versioned_schema(tmp_path) -> None:
    catalog, snapshot, requirements, context = inputs(modes=["duplex"])
    paths = {}
    for name, value in {
        "catalog": catalog,
        "snapshot": snapshot,
        "requirements": requirements,
        "context": context,
    }.items():
        path = tmp_path / f"{name}.json"
        path.write_bytes(value.to_bytes())
        paths[name] = path
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "cxp.cli",
            "evaluate",
            "--catalog",
            str(paths["catalog"]),
            "--snapshot",
            str(paths["snapshot"]),
            "--requirements",
            str(paths["requirements"]),
            "--context",
            str(paths["context"]),
        ],
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr.decode()
    expected = evaluate_requirements(
        snapshot, requirements, context, catalogs=CatalogStore([catalog])
    )
    assert json.loads(result.stdout) == expected.as_dict()
    schema = subprocess.run(
        [
            sys.executable,
            "-m",
            "cxp.cli",
            "schema",
            "document",
            "--type",
            "cxp.catalog",
            "--spec-version",
            "2",
        ],
        capture_output=True,
        check=False,
    )
    assert schema.returncode == 0, schema.stderr.decode()
    assert json.loads(schema.stdout)["$id"] == "urn:cxp:schema:catalog:2"


def test_decimal_and_integer_bounds_use_exact_values() -> None:
    value = catalog_data()
    properties = value["payload"]["capabilities"][0]["properties"]
    properties["copies"]["bounds"]["maximum_inclusive"] = False
    properties["ratio"] = {
        "kind": "decimal",
        "bounds": {"minimum": "0.1", "maximum": "0.2"},
        "source": source("device.print/ratio"),
    }
    catalog = Document(value, expected_type="cxp.catalog")
    from cxp.exchange.property_values import property_value

    assert property_value(
        "0.2", catalog.payload["capabilities"][0]["properties"]["ratio"], "/ratio"
    ) == Fraction(1, 5)
    with pytest.raises(InvalidDocumentError) as error:
        property_value(
            100, catalog.payload["capabilities"][0]["properties"]["copies"], "/copies"
        )
    assert error.value.issues[0].code == "above_catalog_maximum"
    with pytest.raises(InvalidDocumentError) as error:
        property_value(
            "0.099999999999999999",
            catalog.payload["capabilities"][0]["properties"]["ratio"],
            "/ratio",
        )
    assert error.value.issues[0].code == "below_catalog_minimum"


def test_invalid_branch_of_any_is_rejected_before_compatible_branch() -> None:
    catalog, snapshot, requirements, context = inputs(modes=["duplex"])
    data = requirements.as_dict()
    valid = data["payload"]["requirement"]
    invalid = deepcopy(valid)
    invalid["id"] = "bad-mode"
    invalid["values"] = ["unknown"]
    data["payload"]["requirement"] = {
        "id": "either",
        "operator": "any",
        "conditions": [valid, invalid],
    }
    with pytest.raises(InvalidDocumentError) as error:
        evaluate_requirements(
            snapshot,
            Document(data, expected_type="cxp.requirements"),
            context,
            catalogs=CatalogStore([catalog]),
        )
    assert error.value.issues[0].code == "value_outside_domain"


@pytest.mark.parametrize("case", VECTORS["evaluations"], ids=lambda case: case["id"])
def test_portable_catalog_v2_vectors(case: dict) -> None:
    catalog_schema = document_schema(document_type="cxp.catalog", spec_version=2)
    assert Draft202012Validator(catalog_schema).is_valid(VECTORS["catalog"])
    assert jsonschema_rs.Draft202012Validator(catalog_schema).is_valid(
        VECTORS["catalog"]
    )
    catalog = Document(VECTORS["catalog"], expected_type="cxp.catalog")
    assert (
        catalog.sha256
        == VECTORS["snapshots"][case["snapshot"]]["payload"]["catalog"]["sha256"]
    )
    snapshot = Document(
        VECTORS["snapshots"][case["snapshot"]], expected_type="cxp.snapshot"
    )
    requirement_data = (
        VECTORS["requirements"]
        if "requirements" not in case
        else VECTORS["invalid_requirements"][case["requirements"]]
    )
    requirements = Document(requirement_data, expected_type="cxp.requirements")
    context = Document(VECTORS["context"], expected_type="cxp.context")
    if "error" in case:
        with pytest.raises(InvalidDocumentError) as error:
            evaluate_requirements(
                snapshot, requirements, context, catalogs=CatalogStore([catalog])
            )
        assert error.value.issues[0].code == case["error"]
    else:
        result = evaluate_requirements(
            snapshot, requirements, context, catalogs=CatalogStore([catalog])
        )
        assert result.payload["verdict"] == case["verdict"]


def test_portable_v2_catalog_semantic_invalidity_is_not_schema_invalidity() -> None:
    inverted = VECTORS["invalid_catalogs"]["inverted_bounds"]
    schema = document_schema(document_type="cxp.catalog", spec_version=2)
    assert Draft202012Validator(schema).is_valid(inverted)
    assert jsonschema_rs.Draft202012Validator(schema).is_valid(inverted)
    with pytest.raises(InvalidDocumentError) as error:
        Document(inverted, expected_type="cxp.catalog")
    assert error.value.issues[0].code == "invalid_catalog_bounds"
