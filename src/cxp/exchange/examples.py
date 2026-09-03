"""Ejemplos reproducibles disponibles también en una instalación del wheel."""

from __future__ import annotations

import json
from importlib.resources import files

from cxp.exchange.documents import Document
from cxp.exchange.evaluation import evaluate_requirements
from cxp.exchange.reference import load_reference_catalog
from cxp.exchange.registry import CatalogStore


def run_reference_examples() -> dict[str, str]:
    suite = json.loads(
        files("cxp.exchange").joinpath("vectors/exchange-v1.json").read_bytes()
    )
    results = {}
    for case in suite["evaluations"]:
        result = evaluate_requirements(
            Document(case["snapshot"], expected_type="cxp.snapshot"),
            Document(case["requirements"], expected_type="cxp.requirements"),
            Document(case["context"], expected_type="cxp.context"),
            catalogs=CatalogStore([load_reference_catalog(case["catalog"])]),
        )
        results[case["id"]] = result.payload["verdict"]
    return results


if __name__ == "__main__":
    print(json.dumps(run_reference_examples(), indent=2))
