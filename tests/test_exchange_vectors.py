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
    list_reference_catalogs,
    load_document,
    load_reference_catalog,
    negotiate_exchange,
    operation_schema,
    validate_operation_payload,
)
from cxp.exchange.examples import run_reference_examples
from cxp.exchange.tutorial import run_physical_examples

SUITE = json.loads(
    files("cxp.exchange").joinpath("vectors/exchange-v1.json").read_bytes()
)
FROZEN_EVALUATION_HASHES = {
    "effective-support": (
        "2a9946d5f294dbd0d5e865c77d70df0906b59002d257f2b819bba6cd44d161c2"
    ),
    "known-limit": "18e8065950395b615a09e4dc9d5892907b20d97ed28fcf906b2ee56a0b28afb8",
    "missing-property": (
        "33a2170fe998c0b1dd9a0269d288dadfc2092a120038d1ae305760c2f992aeb4"
    ),
    "explicit-null": "1f8e8e57ed88373f4b52d236baacc832f1a72f1c89a8d085c9dac7c4f1fcf40d",
    "discrete-step-mismatch": (
        "4ae2cfddfbff2fc7343ac7b8d0f96803420134e01da99b76b173ffb7e598adf9"
    ),
    "any-known-unknown": (
        "0a72a49d300e6502a16a407d82d43d95757c6500a36b59c7cbb23b58fd7fc0fc"
    ),
    "range-exclusive-minimum": (
        "a7e86315c4b7b8a96be04840d5dae0c1be21e9986be169d66e78b8a4ce5af84c"
    ),
}


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
    if case["id"] in FROZEN_EVALUATION_HASHES:
        assert result.sha256 == FROZEN_EVALUATION_HASHES[case["id"]]


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


def test_reference_catalog_versions_are_explicit_and_defaults_stay_frozen():
    default = load_reference_catalog("physical-printing")
    original = load_reference_catalog("physical-printing", version="1.0.0")
    current = load_reference_catalog("physical-printing", version="1.1.0")
    assert default.to_bytes() == original.to_bytes()
    assert original.sha256 == (
        "3899e78f7b757268bf27d0c6186f4caa4f963eec3ea143dcf324188c1d2d491e"
    )
    assert current.payload["identity"]["version"] == "1.1.0"
    assert CatalogStore([original, current])
    properties = current.payload["capabilities"][0]["properties"]
    assert {
        "max_loaded_mass",
        "max_object_width",
        "max_object_length",
        "print_mode_id",
        "resolution_x",
        "resolution_y",
    } <= properties.keys()
    infos = list_reference_catalogs()
    assert [(item.name, item.version) for item in infos].count(
        ("physical-printing", "1.0.0")
    ) == 1
    assert [(item.name, item.version) for item in infos].count(
        ("physical-printing", "1.1.0")
    ) == 1
    assert all(len(item.sha256) == 64 for item in infos)
    with pytest.raises(ValueError, match="version"):
        load_reference_catalog("physical-printing", version="9.0.0")


def test_packaged_examples_cover_all_three_verdicts():
    assert set(run_reference_examples().values()) == {
        "compatible",
        "incompatible",
        "indeterminate",
    }


def test_physical_tutorial_is_synthetic_deterministic_and_trivalued():
    first = run_physical_examples()
    assert first == run_physical_examples()
    assert {case["verdict"] for case in first.values()} == {
        "compatible",
        "incompatible",
        "indeterminate",
    }
    assert first["any-alternative"]["verdict"] == "compatible"
    assert first["load-4kg"]["finding_reasons"] == ["below_minimum"]


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
