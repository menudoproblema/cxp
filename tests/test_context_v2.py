"""Context v2 conformance independent of the v1 example vectors."""

from __future__ import annotations

import ast
import json
import subprocess
import sys
from importlib.resources import files

import jsonschema_rs
import pytest

from cxp.exchange import (
    CatalogStore,
    Document,
    ExchangeAgreement,
    InvalidDocumentError,
    catalog_reference,
    document_schema,
    evaluate_requirements,
    load_document,
    negotiate_exchange,
)


def make(kind: str, payload: dict, version: int = 1) -> Document:
    return Document(
        {"document_type": kind, "spec_version": version, "payload": payload},
        expected_type=kind,
    )


def context(sources: object, version: int = 2) -> dict:
    payload = {"subject_id": "server", "configuration_revision": "rev"}
    if version == 2:
        payload["accepted_sources"] = sources
    return {"document_type": "cxp.context", "spec_version": version, "payload": payload}


SUITE = json.loads(
    files("cxp.exchange").joinpath("vectors/context-v2.json").read_text()
)
VECTORS = SUITE["documents"]


@pytest.mark.parametrize("case", VECTORS, ids=lambda case: case["id"])
def test_portable_context_vectors(case):
    schema = document_schema(document_type="cxp.context", spec_version=2)
    value = case["document"]
    assert (
        jsonschema_rs.Draft202012Validator(schema).is_valid(value)
        == case["schema_valid"]
    )
    if case["schema_valid"]:
        assert Document(value, expected_type="cxp.context").spec_version == 2
    else:
        with pytest.raises(InvalidDocumentError):
            Document(value, expected_type="cxp.context")


@pytest.mark.parametrize("case", SUITE["evaluations"], ids=lambda case: case["id"])
def test_portable_context_evaluation_vectors(case):
    catalog = Document(SUITE["catalog"], expected_type="cxp.catalog")
    requirements = Document(SUITE["requirements"], expected_type="cxp.requirements")
    snapshot = Document(
        SUITE["snapshots"][case["snapshot"]], expected_type="cxp.snapshot"
    )
    context_document = Document(case["context"], expected_type="cxp.context")
    v1_validator = jsonschema_rs.Draft202012Validator(document_schema())
    for document in (catalog, requirements, snapshot):
        assert v1_validator.is_valid(document.as_dict())
    context_schema = document_schema(
        document_type="cxp.context", spec_version=context_document.spec_version
    )
    assert jsonschema_rs.Draft202012Validator(context_schema).is_valid(
        context_document.as_dict()
    )
    result = evaluate_requirements(
        snapshot, requirements, context_document, catalogs=CatalogStore([catalog])
    )
    assert result.payload["verdict"] == case["expected"]["verdict"]
    assert [finding["code"] for finding in result.payload["findings"]] == case[
        "expected"
    ]["codes"]
    assert result.payload["evaluator_version"] == case["expected"]["evaluator_version"]
    assert v1_validator.is_valid(result.as_dict())


def test_portable_context_source_order_has_identical_bytes():
    left, right = (
        Document(value, expected_type="cxp.context")
        for value in SUITE["canonical_equivalence"]
    )
    assert left.to_bytes() == right.to_bytes()
    assert left.sha256 == right.sha256


@pytest.mark.parametrize(
    "case_id,exit_code",
    [("observed-admitted", 0), ("observed-excluded", 3)],
)
def test_portable_context_evaluation_matches_cli(tmp_path, case_id, exit_code):
    case = next(case for case in SUITE["evaluations"] if case["id"] == case_id)
    inputs = {
        "catalog": SUITE["catalog"],
        "snapshot": SUITE["snapshots"][case["snapshot"]],
        "requirements": SUITE["requirements"],
        "context": case["context"],
    }
    for name, value in inputs.items():
        (tmp_path / f"{name}.json").write_text(json.dumps(value))
    command = subprocess.run(
        [
            sys.executable,
            "-m",
            "cxp.cli",
            "evaluate",
            "--catalog",
            str(tmp_path / "catalog.json"),
            "--snapshot",
            str(tmp_path / "snapshot.json"),
            "--requirements",
            str(tmp_path / "requirements.json"),
            "--context",
            str(tmp_path / "context.json"),
        ],
        capture_output=True,
        check=False,
    )
    assert command.returncode == exit_code, command.stderr.decode()
    expected = evaluate_requirements(
        Document(inputs["snapshot"], expected_type="cxp.snapshot"),
        Document(inputs["requirements"], expected_type="cxp.requirements"),
        Document(inputs["context"], expected_type="cxp.context"),
        catalogs=CatalogStore(
            [Document(inputs["catalog"], expected_type="cxp.catalog")]
        ),
    )
    assert json.loads(command.stdout) == expected.as_dict()


@pytest.fixture
def inputs():
    catalog = make(
        "cxp.catalog",
        {
            "identity": {
                "namespace": "org.example",
                "name": "deployment",
                "version": "1.0.0",
            },
            "owner": "Example",
            "capabilities": [
                {
                    "name": "storage",
                    "properties": {"durable": {"kind": "boolean"}},
                    "operations": [],
                }
            ],
        },
    )
    requirement = make(
        "cxp.requirements",
        {
            "catalog": catalog_reference(catalog),
            "requirement": {
                "id": "durable",
                "operator": "equals",
                "capability": "storage",
                "path": "/properties/durable",
                "value": True,
            },
        },
    )

    def snapshot(source: str):
        return make(
            "cxp.snapshot",
            {
                "provider_id": "provider",
                "subject_id": "server",
                "catalog": catalog_reference(catalog),
                "configuration_revision": "rev",
                "observed_at": "2026-09-26T00:00:00Z",
                "source": {"kind": source, "reference": "sha256:report"},
                "capabilities": [
                    {
                        "name": "storage",
                        "support": "supported",
                        "properties": {"durable": True},
                    }
                ],
            },
        )

    return catalog, requirement, snapshot


@pytest.mark.parametrize("source", ["declared", "observed", "tested"])
def test_source_acceptance_is_explicit_and_unordered(inputs, source):
    catalog, requirement, snapshot = inputs
    admitted = make("cxp.context", context([source])["payload"], version=2)
    excluded = make(
        "cxp.context",
        context(["tested" if source != "tested" else "declared"])["payload"],
        version=2,
    )
    store = CatalogStore([catalog])
    assert (
        evaluate_requirements(
            snapshot(source), requirement, admitted, catalogs=store
        ).payload["verdict"]
        == "compatible"
    )
    result = evaluate_requirements(
        snapshot(source), requirement, excluded, catalogs=store
    )
    assert result.payload["verdict"] == "indeterminate"
    assert result.payload["findings"][0]["code"] == "source_not_accepted"
    assert result.payload["evaluator_version"] == "1.1.0"


@pytest.mark.parametrize(
    "sources", [[], ["tested", "tested"], ["unknown"], [True], "tested"]
)
def test_invalid_sources_rejected_by_both_validators(sources):
    value = context(sources)
    schema = document_schema(document_type="cxp.context", spec_version=2)
    assert not jsonschema_rs.Draft202012Validator(schema).is_valid(value)
    with pytest.raises(InvalidDocumentError):
        Document(value, expected_type="cxp.context")


def test_source_set_has_canonical_bytes_and_v1_is_unchanged(inputs):
    catalog, requirement, snapshot = inputs
    left = make("cxp.context", context(["tested", "observed"])["payload"], version=2)
    right = make("cxp.context", context(["observed", "tested"])["payload"], version=2)
    assert left.to_bytes() == right.to_bytes()
    assert left.sha256 == right.sha256
    v1 = make("cxp.context", context(None, version=1)["payload"])
    assert (
        evaluate_requirements(
            snapshot("declared"), requirement, v1, catalogs=CatalogStore([catalog])
        ).payload["evaluator_version"]
        == "1.0.0"
    )
    with pytest.raises(InvalidDocumentError):
        make("cxp.context", context(None, version=1)["payload"], version=2)


@pytest.mark.parametrize(
    "update,expected",
    [
        ({"subject_id": "other"}, "subject_mismatch"),
        ({"configuration_revision": "other"}, "configuration_mismatch"),
        (
            {"as_of": "2026-09-26T00:02:00Z", "max_age_seconds": 60},
            "source_not_accepted",
        ),
    ],
)
def test_source_exclusion_combined_with_other_context_failures(
    inputs, update, expected
):
    catalog, requirement, snapshot = inputs
    payload = context(["observed"])["payload"] | update
    result = evaluate_requirements(
        snapshot("tested"),
        requirement,
        make("cxp.context", payload, version=2),
        catalogs=CatalogStore([catalog]),
    )
    assert result.payload["verdict"] == "indeterminate"
    assert result.payload["findings"][0]["code"] == expected


def test_v2_schema_and_negotiation_do_not_fallback():
    schema = document_schema(document_type="cxp.context", spec_version=2)
    valid = context(["tested"])
    assert jsonschema_rs.Draft202012Validator(schema).is_valid(valid)
    assert (
        load_document(json.dumps(valid), expected_type="cxp.context").spec_version == 2
    )
    request = make(
        "cxp.exchange_request",
        {
            "protocol_version": 2,
            "formats": [{"document_type": "cxp.context", "spec_versions": [1, 2]}],
        },
    )
    response = negotiate_exchange(request)
    assert response.payload["formats"][0]["spec_version"] == 2
    agreement = ExchangeAgreement(request, response)
    assert (
        agreement.decode(
            agreement.encode(make("cxp.context", valid["payload"], version=2)),
            expected_type="cxp.context",
        ).spec_version
        == 2
    )
    old_request = make(
        "cxp.exchange_request",
        {
            "protocol_version": 2,
            "formats": [{"document_type": "cxp.context", "spec_versions": [1]}],
        },
    )
    old_agreement = ExchangeAgreement(old_request, negotiate_exchange(old_request))
    with pytest.raises(Exception) as error:
        old_agreement.encode(make("cxp.context", valid["payload"], version=2))
    assert error.value.issues[0].code == "format_not_negotiated"


def test_pure_core_has_no_validator_imports():
    source = files("cxp.exchange").joinpath("core.py").read_text()
    imports = {
        node.module
        for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.ImportFrom)
    }
    assert "cxp.exchange.documents" not in imports
    assert "cxp.exchange.registry" not in imports
    assert "jsonschema" not in imports
    assert "referencing" not in imports


def test_pure_core_import_does_not_load_document_validators_or_legacy_catalogs():
    command = subprocess.run(
        [
            sys.executable,
            "-c",
            "import sys; import cxp.exchange.core; "
            "assert 'jsonschema' not in sys.modules; "
            "assert 'referencing' not in sys.modules; "
            "assert not any(n.startswith('cxp.catalogs') for n in sys.modules)",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert command.returncode == 0, command.stderr


def test_cli_and_python_use_same_v2_contract(tmp_path):
    path = tmp_path / "context.json"
    path.write_text(json.dumps(context(["tested", "observed"])))
    expected = load_document(path.read_bytes(), expected_type="cxp.context")
    command = subprocess.run(
        [
            sys.executable,
            "-m",
            "cxp.cli",
            "validate",
            str(path),
            "--type",
            "cxp.context",
        ],
        capture_output=True,
        check=False,
    )
    assert command.returncode == 0
    assert json.loads(command.stdout)["sha256"] == expected.sha256
    schema = subprocess.run(
        [
            sys.executable,
            "-m",
            "cxp.cli",
            "schema",
            "document",
            "--type",
            "cxp.context",
            "--spec-version",
            "2",
        ],
        capture_output=True,
        check=False,
    )
    assert schema.returncode == 0
    assert json.loads(schema.stdout) == document_schema(
        document_type="cxp.context", spec_version=2
    )
