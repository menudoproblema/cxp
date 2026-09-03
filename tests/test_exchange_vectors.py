"""Vectores portables: JSON Schema con un segundo motor y semántica CXP."""

import hashlib
import json
from importlib.resources import files

import jsonschema_rs
import pytest

from cxp.exchange import (
    REFERENCE_CATALOGS,
    CatalogStore,
    Document,
    ExchangeAgreement,
    InvalidDocumentError,
    UnsupportedContractError,
    document_schema,
    evaluate_requirements,
    legacy_idempotency,
    load_document,
    load_reference_catalog,
    negotiate_exchange,
    operation_schema,
    validate_operation_payload,
)
from cxp.exchange.examples import run_reference_examples

SUITE = json.loads(
    files("cxp.exchange").joinpath("vectors/exchange-v1.json").read_bytes()
)


@pytest.mark.parametrize("case", SUITE["canonicalization"], ids=lambda case: case["id"])
def test_portable_canonical_bytes(case):
    document = Document(case["document"], expected_type=case["document_type"])
    expected = case["expected_utf8"].encode("utf-8")
    assert document.to_bytes() == expected
    assert document.sha256 == hashlib.sha256(expected).hexdigest()


@pytest.mark.parametrize("case", SUITE["documents"], ids=lambda case: case["id"])
def test_portable_document_vectors(case):
    if case["schema_valid"] is not None:
        assert (
            jsonschema_rs.Draft202012Validator(document_schema()).is_valid(
                case["document"]
            )
            == case["schema_valid"]
        )
    data = case.get("raw_json") or json.dumps(case["document"])
    status = case["expected"]["status"]
    if status == "accepted":
        document = load_document(data, expected_type=case["document_type"])
        assert (
            load_document(document.to_bytes(), expected_type=case["document_type"])
            == document
        )
    else:
        error_type = (
            InvalidDocumentError if status == "invalid" else UnsupportedContractError
        )
        with pytest.raises(error_type) as error:
            load_document(data, expected_type=case["document_type"])
        assert error.value.issues[0].code == case["expected"]["code"]
        if "path" in case["expected"]:
            assert error.value.issues[0].path == case["expected"]["path"]
        if "document" in case:
            with pytest.raises(error_type) as mapping_error:
                Document(case["document"], expected_type=case["document_type"])
            assert [
                (issue.code, issue.path) for issue in mapping_error.value.issues
            ] == [(issue.code, issue.path) for issue in error.value.issues]


@pytest.mark.parametrize("case", SUITE["negotiations"], ids=lambda case: case["id"])
def test_portable_negotiation_vectors(case):
    validator = jsonschema_rs.Draft202012Validator(document_schema())
    assert validator.is_valid(case["request"])
    assert validator.is_valid(case["expected_response"])
    request = Document(case["request"], expected_type="cxp.exchange_request")
    options = {}
    if "supported_formats" in case:
        options["supported_formats"] = {
            name: tuple(versions)
            for name, versions in case["supported_formats"].items()
        }
    response = negotiate_exchange(request, **options)
    assert response.as_dict() == case["expected_response"]


@pytest.mark.parametrize("case", SUITE["agreements"], ids=lambda case: case["id"])
def test_portable_agreement_vectors(case):
    validator = jsonschema_rs.Draft202012Validator(document_schema())
    assert validator.is_valid(case["request"])
    assert validator.is_valid(case["response"])
    request = Document(case["request"], expected_type="cxp.exchange_request")
    response = Document(case["response"], expected_type="cxp.exchange_response")
    if case["expected"]["status"] == "accepted":
        assert ExchangeAgreement(request, response)
    else:
        error_type = (
            InvalidDocumentError
            if case["expected"]["status"] == "invalid"
            else UnsupportedContractError
        )
        with pytest.raises(error_type) as error:
            ExchangeAgreement(request, response)
        assert error.value.issues[0].code == case["expected"]["code"]


def evaluate_case(case):
    validator = jsonschema_rs.Draft202012Validator(document_schema())
    catalog = load_reference_catalog(case["catalog"])
    assert validator.is_valid(catalog.as_dict())
    for key in ("snapshot", "requirements", "context"):
        assert validator.is_valid(case[key])
    return evaluate_requirements(
        Document(case["snapshot"], expected_type="cxp.snapshot"),
        Document(case["requirements"], expected_type="cxp.requirements"),
        Document(case["context"], expected_type="cxp.context"),
        catalogs=CatalogStore([catalog]),
    )


@pytest.mark.parametrize("case", SUITE["evaluations"], ids=lambda case: case["id"])
def test_portable_evaluation_vectors(case):
    result = evaluate_case(case)
    assert result.payload["verdict"] == case["expected"]["verdict"]
    assert [finding["code"] for finding in result.payload["findings"]] == case[
        "expected"
    ]["codes"]
    assert jsonschema_rs.Draft202012Validator(document_schema()).is_valid(
        result.as_dict()
    )
    assert result.to_bytes() == evaluate_case(case).to_bytes()


@pytest.mark.parametrize("case", SUITE["rejections"], ids=lambda case: case["id"])
def test_portable_semantic_rejection_vectors(case):
    with pytest.raises(InvalidDocumentError) as error:
        evaluate_case(case)
    assert error.value.issues[0].code == case["expected"]["code"]


@pytest.mark.parametrize("name", REFERENCE_CATALOGS)
def test_reference_catalog_contracts(name):
    catalog = load_reference_catalog(name)
    assert jsonschema_rs.Draft202012Validator(document_schema()).is_valid(
        catalog.as_dict()
    )
    for capability in catalog.payload["capabilities"]:
        for operation in capability["operations"]:
            assert operation_schema(operation["input_type"])
            assert operation_schema(operation["result_type"])
    if name == "finishing":
        definitions = {item["name"]: item for item in catalog.payload["capabilities"]}
        assert "printing.surface" not in definitions
        assert "patterns" in definitions["finishing.folding"]["properties"]
        assert "patterns" not in definitions["finishing.binding"]["properties"]


def test_packaged_examples_cover_all_three_verdicts():
    assert set(run_reference_examples().values()) == {
        "compatible",
        "incompatible",
        "indeterminate",
    }


def test_idempotency_is_conservative_and_declarations_are_explicit():
    assert legacy_idempotency(False) == {"state": "unknown"}
    assert legacy_idempotency(True) == {"state": "guaranteed"}
    catalog = load_reference_catalog("job-submission").payload
    submit = catalog["capabilities"][0]["operations"][0]
    assert submit["idempotency"]["state"] == "not_idempotent"
    with pytest.raises(TypeError):
        legacy_idempotency(1)


@pytest.mark.parametrize(
    "contract,payload,valid",
    [
        (
            "submission-request",
            {"request_id": "r1", "document_reference": "document:1"},
            True,
        ),
        (
            "submission-receipt",
            {"request_id": "r1", "status": "accepted", "job_id": "j1"},
            True,
        ),
        ("submission-receipt", {"request_id": "r1", "status": "accepted"}, False),
        (
            "submission-receipt",
            {"request_id": "r1", "status": "unknown", "reason": "Lost acknowledgement"},
            True,
        ),
        (
            "submission-receipt",
            {
                "request_id": "r1",
                "status": "rejected",
                "reason": "Invalid document",
                "job_id": "j1",
            },
            False,
        ),
        ("job-query", {"job_id": "j1"}, True),
        (
            "document-request",
            {"request_id": "r1", "document_reference": "document:1"},
            True,
        ),
        (
            "document-result",
            {
                "request_id": "r1",
                "outcome": "succeeded",
                "output_reference": "report:1",
            },
            True,
        ),
        ("document-result", {"request_id": "r1", "outcome": "unknown"}, False),
    ],
)
def test_operation_contract_shapes(contract, payload, valid):
    contract_type = f"org.cxp:{contract}:1"
    assert (
        jsonschema_rs.Draft202012Validator(operation_schema(contract_type)).is_valid(
            payload
        )
        == valid
    )
    if valid:
        assert validate_operation_payload(contract_type, payload) == payload
    else:
        with pytest.raises(InvalidDocumentError):
            validate_operation_payload(contract_type, payload)


def test_physical_success_requires_explicit_evidence_but_does_not_verify_it():
    observation = {
        "job_id": "j1",
        "outcome": "succeeded",
        "result_scope": "physical_production",
        "observed_at": "2026-09-03T10:00:00Z",
        "source": {"kind": "observed", "reference": "sensor:1"},
    }
    with pytest.raises(InvalidDocumentError):
        validate_operation_payload("org.cxp:job-observation:1", observation)
    observation["evidence_reference"] = "inspection:1"
    result = validate_operation_payload("org.cxp:job-observation:1", observation)
    assert result["evidence_reference"] == "inspection:1"
    result["source"]["reference"] = "changed"
    assert observation["source"]["reference"] == "sensor:1"
