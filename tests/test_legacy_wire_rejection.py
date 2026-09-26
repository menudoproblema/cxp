"""Historical wire bytes remain evidence of deliberate protocol separation."""

import json
from pathlib import Path

import pytest

from cxp.exchange import (
    Document,
    ExchangeAgreement,
    InvalidDocumentError,
    load_document,
    negotiate_exchange,
)

FIXTURE = json.loads(
    Path(__file__)
    .with_name("fixtures")
    .joinpath("legacy-3.1-wire.json")
    .read_text(encoding="utf-8")
)


@pytest.mark.parametrize("case", FIXTURE["cases"], ids=lambda case: case["type"])
def test_old_wire_is_not_an_exchange_snapshot(case: dict[str, object]) -> None:
    with pytest.raises(InvalidDocumentError):
        load_document(str(case["wire"]), expected_type="cxp.snapshot")


def test_negotiated_exchange_reader_rejects_old_wire() -> None:
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
    with pytest.raises(InvalidDocumentError):
        agreement.decode(
            FIXTURE["cases"][1]["wire"],
            expected_type="cxp.snapshot",
        )
