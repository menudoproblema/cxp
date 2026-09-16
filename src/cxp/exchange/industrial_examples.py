"""Ejemplos sintéticos de los catálogos industriales, sin equipo ni red."""

from __future__ import annotations

import json

from cxp.exchange.documents import Document
from cxp.exchange.evaluation import evaluate_requirements
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


def _evaluate(
    catalog: Document,
    capabilities: list[dict[str, object]],
    requirement: dict[str, object],
) -> str:
    snapshot = _document(
        "cxp.snapshot",
        {
            "provider_id": "synthetic-industrial-example",
            "subject_id": "synthetic-subject",
            "catalog": catalog_reference(catalog),
            "configuration_revision": "synthetic-configuration",
            "observed_at": "2026-09-16T10:00:00Z",
            "source": {"kind": "declared", "reference": "synthetic-example"},
            "capabilities": capabilities,
        },
    )
    requirements = _document(
        "cxp.requirements",
        {"catalog": catalog_reference(catalog), "requirement": requirement},
    )
    context = _document(
        "cxp.context",
        {
            "subject_id": "synthetic-subject",
            "configuration_revision": "synthetic-configuration",
        },
    )
    return evaluate_requirements(
        snapshot,
        requirements,
        context,
        catalogs=CatalogStore([catalog]),
    ).payload["verdict"]


def run_industrial_examples() -> dict[str, str]:
    """Evalúa declaraciones sintéticas sin inferir un proceso compuesto."""
    positioning = load_reference_catalog("positioning")
    identification = load_reference_catalog("identification")
    return {
        "fixture-without-camera": _evaluate(
            positioning,
            [
                {
                    "name": "positioning.physical_referencing",
                    "support": "supported",
                    "properties": {"acquisition_methods": ["mechanical_constraint"]},
                }
            ],
            {
                "id": "fixture",
                "operator": "contains_all",
                "capability": "positioning.physical_referencing",
                "path": "/properties/acquisition_methods",
                "values": ["mechanical_constraint"],
            },
        ),
        "marks-without-application": _evaluate(
            positioning,
            [
                {
                    "name": "positioning.feature_detection",
                    "support": "supported",
                    "properties": {},
                },
                {
                    "name": "positioning.compensation_application",
                    "support": "unsupported",
                    "properties": {},
                },
            ],
            {
                "id": "both",
                "operator": "all",
                "conditions": [
                    {
                        "id": "detect",
                        "operator": "support",
                        "capability": "positioning.feature_detection",
                    },
                    {
                        "id": "apply",
                        "operator": "support",
                        "capability": "positioning.compensation_application",
                    },
                ],
            },
        ),
        "unreported-qr-reading": _evaluate(
            identification,
            [
                {
                    "name": "identification.symbol_reading",
                    "support": "supported",
                    "properties": {},
                }
            ],
            {
                "id": "read-qr",
                "operator": "contains_all",
                "capability": "identification.symbol_reading",
                "path": "/properties/symbologies",
                "values": ["qr_code"],
            },
        ),
    }


def main() -> None:
    print(json.dumps(run_industrial_examples(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
