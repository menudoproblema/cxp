"""Compatibilidad contra wire generado con el checkout 3.1.0 archivado."""

import importlib
import json
from pathlib import Path

import msgspec
import pytest

import cxp
from cxp.exchange import (
    Document,
    ExchangeAgreement,
    InvalidDocumentError,
    load_document,
    negotiate_exchange,
)

FIXTURE = json.loads(
    Path(__file__).with_name("fixtures").joinpath("legacy-3.1-wire.json").read_text()
)


@pytest.mark.parametrize("case", FIXTURE["cases"], ids=lambda case: case["type"])
def test_legacy_wire_roundtrip(case):
    model = getattr(importlib.import_module(case["module"]), case["type"])
    decoded = msgspec.json.decode(case["wire"], type=model)
    assert msgspec.json.encode(decoded).decode() == case["wire"]
    with pytest.raises(InvalidDocumentError):
        load_document(case["wire"], expected_type="cxp.snapshot")


@pytest.mark.parametrize(
    "case", FIXTURE["old_reader_results"], ids=lambda case: case["type"]
)
def test_preserved_old_readers_match_recorded_permissiveness(case):
    model = getattr(cxp, case["type"])
    if case["status"] == "accepted":
        decoded = msgspec.json.decode(FIXTURE["new_document"], type=model)
        assert msgspec.json.decode(msgspec.json.encode(decoded)) == case["value"]
    else:
        with pytest.raises(msgspec.ValidationError) as error:
            msgspec.json.decode(FIXTURE["new_document"], type=model)
        assert str(error.value) == case["error"]


def test_agreement_never_routes_legacy_payload_to_permissive_reader():
    request = Document(
        {
            "document_type": "cxp.exchange_request",
            "spec_version": 1,
            "payload": {
                "protocol_version": 2,
                "formats": [
                    {"document_type": "cxp.snapshot", "spec_versions": [1]},
                ],
            },
        },
        expected_type="cxp.exchange_request",
    )
    agreement = ExchangeAgreement(request, negotiate_exchange(request))
    legacy_snapshot = FIXTURE["cases"][1]["wire"]
    with pytest.raises(InvalidDocumentError):
        agreement.decode(legacy_snapshot, expected_type="cxp.snapshot")
    identity = cxp.ComponentIdentity(
        interface="database/sql", provider="test", version="1"
    )
    assert (
        cxp.negotiate_capabilities(
            cxp.HandshakeRequest(client_identity=identity, protocol_version=2),
            identity,
            cxp.CapabilityMatrix(),
        ).status
        == "rejected"
    )


def test_legacy_handshake_and_noop_projection_keep_their_meaning():
    cases = {case["type"]: case for case in FIXTURE["cases"]}
    request = msgspec.json.decode(
        cases["HandshakeRequest"]["wire"], type=cxp.HandshakeRequest
    )
    matrix = msgspec.json.decode(
        cases["CapabilityMatrix"]["wire"], type=cxp.CapabilityMatrix
    )
    response = cxp.negotiate_capabilities(request, request.client_identity, matrix)
    assert msgspec.json.encode(response).decode() == cases["HandshakeResponse"]["wire"]
    snapshot = msgspec.json.decode(
        cases["ComponentCapabilitySnapshot"]["wire"],
        type=cxp.ComponentCapabilitySnapshot,
    )
    assert snapshot.as_capability_matrix_with_noop().has_capability("write")
    assert not snapshot.as_negotiated_capability_matrix().has_capability("write")
