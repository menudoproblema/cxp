"""Evaluate synthetic resource claims from an external catalog JSON file.

The report is a local, trusted example input. Its digest is checked by the
consumer; a real integrator must establish its own report authority and live
handle correspondence before admitting an operation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from cxp.exchange import (
    CatalogStore,
    Document,
    InvalidDocumentError,
    UnsupportedContractError,
    catalog_reference,
    evaluate_requirements_detailed,
    load_document,
)

CATALOG_FILE = Path(__file__).parent / "data" / "resource-catalog.json"
OBSERVED_AT = "2026-09-26T10:00:00.000000Z"


def _document(kind: str, payload: dict[str, Any], version: int = 1) -> Document:
    return Document(
        {"document_type": kind, "spec_version": version, "payload": payload},
        expected_type=kind,
    )


def _report_reference(report: dict[str, Any]) -> str:
    # This is the synthetic report owner's byte convention, separate from JCS.
    content = json.dumps(
        report, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return f"sha256:{hashlib.sha256(content).hexdigest()}"


def _snapshot(
    catalog: Document,
    value: object,
    *,
    source: str = "observed",
    subject: str = "resource-1",
    revision: str = "generation-1",
) -> tuple[Document, dict[str, Any]]:
    properties = {} if value is None else {"confirmed": value}
    report = {
        "method": "synthetic-confirmation-probe",
        "verifier_version": "1",
        "subject_id": subject,
        "configuration_revision": revision,
        "observed_at": OBSERVED_AT,
        "source_kind": source,
        "covered_properties": sorted(properties),
        "values": properties,
    }
    snapshot = _document(
        "cxp.snapshot",
        {
            "provider_id": "synthetic-resource-owner",
            "subject_id": subject,
            "catalog": catalog_reference(catalog),
            "configuration_revision": revision,
            "observed_at": OBSERVED_AT,
            "source": {"kind": source, "reference": _report_reference(report)},
            "capabilities": [
                {
                    "name": "storage.write",
                    "support": "supported",
                    "properties": properties,
                }
            ],
        },
    )
    return snapshot, report


def _context(
    *,
    subject: str = "resource-1",
    revision: str = "generation-1",
    as_of: str = "2026-09-26T10:00:30Z",
) -> Document:
    return _document(
        "cxp.context",
        {
            "subject_id": subject,
            "configuration_revision": revision,
            "accepted_sources": ["observed"],
            "as_of": as_of,
            "max_age_seconds": 60,
        },
        version=2,
    )


def _report_matches(snapshot: Document, report: dict[str, Any]) -> bool:
    """Example owner check; CXP does not read or authenticate this report."""
    payload = snapshot.payload
    capability = payload["capabilities"][0]
    claimed = capability["properties"]
    return (
        payload["source"]["reference"] == _report_reference(report)
        and payload["source"]["kind"] == report["source_kind"]
        and payload["subject_id"] == report["subject_id"]
        and payload["configuration_revision"] == report["configuration_revision"]
        and payload["observed_at"] == report["observed_at"]
        and set(claimed) <= set(report["covered_properties"])
        and all(report["values"].get(key) == value for key, value in claimed.items())
    )


def _write_case(
    directory: Path,
    name: str,
    snapshot: Document,
    context: Document,
    report: dict[str, Any],
) -> None:
    target = directory / name
    target.mkdir(parents=True, exist_ok=True)
    (target / "snapshot.json").write_bytes(snapshot.to_bytes())
    (target / "context.json").write_bytes(context.to_bytes())
    (target / "report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def run_resource_examples(write_documents: Path | None = None) -> dict[str, Any]:
    catalog = load_document(CATALOG_FILE.read_bytes(), expected_type="cxp.catalog")
    requirements = _document(
        "cxp.requirements",
        {
            "catalog": catalog_reference(catalog),
            "requirement": {
                "id": "confirmed-write",
                "operator": "equals",
                "capability": "storage.write",
                "path": "/properties/confirmed",
                "value": True,
            },
        },
    )
    store = CatalogStore([catalog])
    compatible, true_report = _snapshot(catalog, True)
    incompatible, false_report = _snapshot(catalog, False)
    missing, missing_report = _snapshot(catalog, None)
    declared, declared_report = _snapshot(catalog, True, source="declared")
    malformed, malformed_report = _snapshot(catalog, "yes")
    cases = {
        "compatible": (compatible, _context(), true_report),
        "incompatible": (incompatible, _context(), false_report),
        "missing": (missing, _context(), missing_report),
        "source-excluded": (declared, _context(), declared_report),
        "wrong-subject": (compatible, _context(subject="resource-2"), true_report),
        "wrong-revision": (
            compatible,
            _context(revision="generation-2"),
            true_report,
        ),
        "expired": (
            compatible,
            _context(as_of="2026-09-26T10:02:00Z"),
            true_report,
        ),
        "wrong-report": (compatible, _context(), false_report),
        "invalid-document": (malformed, _context(), malformed_report),
    }
    if write_documents is not None:
        write_documents.mkdir(parents=True, exist_ok=True)
        (write_documents / "catalog.json").write_bytes(catalog.to_bytes())
        (write_documents / "requirements.json").write_bytes(requirements.to_bytes())
    results: dict[str, Any] = {}
    for name, (snapshot, context, report) in cases.items():
        if write_documents is not None:
            _write_case(write_documents, name, snapshot, context, report)
        try:
            result = evaluate_requirements_detailed(
                snapshot, requirements, context, catalogs=store
            )
        except (InvalidDocumentError, UnsupportedContractError) as error:
            results[name] = {
                "outcome": "invalid",
                "codes": [issue.code for issue in error.issues],
                "admitted": False,
            }
            continue
        results[name] = {
            "outcome": result.verdict,
            "codes": [finding.code for finding in result.findings],
            "admitted": result.is_compatible and _report_matches(snapshot, report),
        }
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-documents", type=Path)
    args = parser.parse_args()
    print(
        json.dumps(
            run_resource_examples(args.write_documents),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
