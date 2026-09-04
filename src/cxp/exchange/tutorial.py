"""Recorrido autocontenido del intercambio físico sin equipo ni red."""

from __future__ import annotations

import json

from cxp.exchange.documents import Document
from cxp.exchange.evaluation import evaluate_requirements_detailed
from cxp.exchange.reference import load_reference_catalog
from cxp.exchange.registry import CatalogStore, catalog_reference


def _document(document_type: str, payload: dict[str, object]) -> Document:
    return Document(
        {
            "document_type": document_type,
            "spec_version": 1,
            "payload": payload,
        },
        expected_type=document_type,
    )


def _snapshot(catalog: Document, subject_id: str, mass: str | None) -> Document:
    properties: dict[str, object] = {
        "ink_channels": ["cmyk", "white"],
        "max_width": {"value": "610", "unit": "mm"},
        "max_height": {"value": "458", "unit": "mm"},
    }
    if mass is not None:
        properties["max_loaded_mass"] = {"value": mass, "unit": "kg"}
    return _document(
        "cxp.snapshot",
        {
            "provider_id": "synthetic-adapter",
            "subject_id": subject_id,
            "catalog": catalog_reference(catalog),
            "configuration_revision": "synthetic-config-1",
            "observed_at": "2026-09-04T10:00:00Z",
            "source": {
                "kind": "declared",
                "reference": "synthetic-example",
            },
            "capabilities": [
                {
                    "name": "printing.surface",
                    "support": "supported",
                    "properties": properties,
                }
            ],
        },
    )


def _requirements(catalog: Document, requirement: dict[str, object]) -> Document:
    return _document(
        "cxp.requirements",
        {"catalog": catalog_reference(catalog), "requirement": requirement},
    )


def _context(subject_id: str) -> Document:
    return _document(
        "cxp.context",
        {
            "subject_id": subject_id,
            "configuration_revision": "synthetic-config-1",
        },
    )


def run_physical_examples() -> dict[str, dict[str, object]]:
    catalog = load_reference_catalog("physical-printing", version="1.1.0")
    store = CatalogStore([catalog])
    minimum_mass: dict[str, object] = {
        "id": "minimum-load",
        "operator": "range",
        "capability": "printing.surface",
        "path": "/properties/max_loaded_mass",
        "minimum": {"value": "5", "unit": "kg"},
    }
    cases: dict[str, tuple[Document, dict[str, object]]] = {
        "load-8kg": (_snapshot(catalog, "surface-8", "8"), minimum_mass),
        "load-4kg": (_snapshot(catalog, "surface-4", "4"), minimum_mass),
        "load-unreported": (
            _snapshot(catalog, "surface-unknown", None),
            minimum_mass,
        ),
        "any-alternative": (
            _snapshot(catalog, "surface-any", "8"),
            {
                "id": "one-route",
                "operator": "any",
                "conditions": [
                    {
                        **minimum_mass,
                        "id": "minimum-9kg",
                        "minimum": {"value": "9", "unit": "kg"},
                    },
                    {
                        "id": "white-channel",
                        "operator": "contains_all",
                        "capability": "printing.surface",
                        "path": "/properties/ink_channels",
                        "values": ["white"],
                    },
                ],
            },
        ),
    }
    results: dict[str, dict[str, object]] = {}
    for name, (snapshot, requirement) in cases.items():
        result = evaluate_requirements_detailed(
            snapshot,
            _requirements(catalog, requirement),
            _context(snapshot.payload["subject_id"]),
            catalogs=store,
        )
        results[name] = {
            "catalog_sha256": catalog.sha256,
            "evaluation_sha256": result.document.sha256,
            "finding_reasons": [finding.reason for finding in result.findings],
            "input_sha256": snapshot.sha256,
            "verdict": result.verdict,
        }
    return results


def main() -> None:
    print(json.dumps(run_physical_examples(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
