"""Acuerdo explícito de familias: sin fallback al protocolo heredado."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType

from cxp.exchange.documents import DOCUMENT_TYPES, Document, JsonObject, load_document
from cxp.exchange.errors import invalid, unsupported

__all__ = ("ExchangeAgreement", "SUPPORTED_FORMATS", "negotiate_exchange")

SUPPORTED_FORMATS: Mapping[str, tuple[int, ...]] = MappingProxyType(
    dict.fromkeys(DOCUMENT_TYPES, (1,))
)


def negotiate_exchange(
    request: Document,
    *,
    supported_formats: Mapping[str, tuple[int, ...]] = SUPPORTED_FORMATS,
) -> Document:
    request.require_type("cxp.exchange_request")
    # Solo permitimos restringir la implementación real, no inventar soporte.
    for name, versions in supported_formats.items():
        if name not in SUPPORTED_FORMATS or any(
            type(version) is not int or version not in SUPPORTED_FORMATS[name]
            for version in versions
        ):
            raise ValueError("Cannot advertise an unimplemented document format")
    payload = request.payload
    formats: list[JsonObject] = []
    reason = None
    if payload["protocol_version"] != 2:
        reason = "Unsupported exchange protocol version"
    else:
        for requested in payload["formats"]:
            name = requested["document_type"]
            common = set(requested["spec_versions"]) & set(
                supported_formats.get(name, ())
            )
            if not common:
                reason = f"No supported version for {name}"
                break
            formats.append({"document_type": name, "spec_version": max(common)})
    response: JsonObject = {
        "protocol_version": 2,
        "request_sha256": request.sha256,
        "status": "rejected" if reason else "accepted",
        "formats": [] if reason else formats,
    }
    if reason:
        response["reason"] = reason
    return Document(
        {
            "document_type": "cxp.exchange_response",
            "spec_version": 1,
            "payload": response,
        },
        expected_type="cxp.exchange_response",
    )


@dataclass(frozen=True, slots=True, init=False)
class ExchangeAgreement:
    _formats: tuple[tuple[str, int], ...]

    def __init__(self, request: Document, response: Document) -> None:
        request.require_type("cxp.exchange_request")
        response.require_type("cxp.exchange_response")
        requested, accepted = request.payload, response.payload
        if accepted["request_sha256"] != request.sha256:
            raise invalid(
                "request_mismatch",
                "/payload/request_sha256",
                "Response belongs to another request",
            )
        if (
            requested["protocol_version"] != 2
            or accepted["protocol_version"] != 2
            or accepted["status"] != "accepted"
        ):
            raise unsupported(
                "exchange_rejected", "/payload/status", "No accepted exchange agreement"
            )
        offers = {
            item["document_type"]: item["spec_versions"]
            for item in requested["formats"]
        }
        selected = {
            item["document_type"]: item["spec_version"] for item in accepted["formats"]
        }
        if set(offers) != set(selected):
            raise invalid(
                "format_mismatch",
                "/payload/formats",
                "Response dropped or added document families",
            )
        for name, version in selected.items():
            if version not in offers[name] or version not in SUPPORTED_FORMATS.get(
                name, ()
            ):
                raise invalid(
                    "format_mismatch",
                    "/payload/formats",
                    "Response selected an unoffered or unimplemented format",
                )
        object.__setattr__(self, "_formats", tuple(sorted(selected.items())))

    def _require_format(self, document_type: str, spec_version: int) -> None:
        if (document_type, spec_version) not in self._formats:
            raise unsupported(
                "format_not_negotiated",
                "/document_type",
                "Document family/version was not negotiated",
            )

    def encode(self, document: Document) -> bytes:
        self._require_format(document.document_type, document.spec_version)
        return document.to_bytes()

    def decode(self, data: bytes | str, *, expected_type: str) -> Document:
        if not any(name == expected_type for name, _ in self._formats):
            raise unsupported(
                "format_not_negotiated",
                "/document_type",
                "Document family was not negotiated",
            )
        document = load_document(data, expected_type=expected_type)
        self._require_format(document.document_type, document.spec_version)
        return document
