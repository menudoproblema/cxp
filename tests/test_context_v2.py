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


VECTORS = json.loads(
    files("cxp.exchange").joinpath("vectors/context-v2.json").read_text()
)["documents"]


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
