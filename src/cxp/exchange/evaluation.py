"""Validated public entry points for exchange evaluation."""

from __future__ import annotations

from dataclasses import dataclass

from cxp.exchange.core import (
    EvaluationFinding,
    EvaluationOperand,
    EvaluationVerdict,
    evaluate_validated,
)
from cxp.exchange.documents import Document
from cxp.exchange.errors import invalid
from cxp.exchange.registry import CatalogStore

__all__ = (
    "EVALUATOR_VERSION",
    "CONTEXT_V2_EVALUATOR_VERSION",
    "EvaluationFinding",
    "EvaluationOperand",
    "EvaluationResult",
    "evaluate_requirements",
    "evaluate_requirements_detailed",
)

EVALUATOR_VERSION = "1.0.0"
CONTEXT_V2_EVALUATOR_VERSION = "1.1.0"


@dataclass(frozen=True, slots=True)
class EvaluationResult:
    document: Document
    verdict: EvaluationVerdict
    findings: tuple[EvaluationFinding, ...]

    @property
    def is_compatible(self) -> bool:
        return self.verdict == "compatible"


def evaluate_requirements(
    snapshot: Document,
    requirements: Document,
    context: Document,
    *,
    catalogs: CatalogStore,
) -> Document:
    return evaluate_requirements_detailed(
        snapshot, requirements, context, catalogs=catalogs
    ).document


def evaluate_requirements_detailed(
    snapshot: Document,
    requirements: Document,
    context: Document,
    *,
    catalogs: CatalogStore,
) -> EvaluationResult:
    """Validate every document and catalog branch before evaluating."""
    context.require_type("cxp.context")
    catalog = catalogs.validate_snapshot(snapshot)
    requirement_catalog = catalogs.validate_requirements(requirements)
    if catalog.sha256 != requirement_catalog.sha256:
        raise invalid(
            "catalog_mismatch",
            "/payload/catalog",
            "Snapshot and requirements must use the same exact catalog",
        )
    verdict, document_findings, detailed_findings = evaluate_validated(
        snapshot.payload, requirements.payload, context.payload, catalog.payload
    )
    document = Document(
        {
            "document_type": "cxp.evaluation",
            "spec_version": 1,
            "payload": {
                "verdict": verdict,
                "evaluator_version": (
                    CONTEXT_V2_EVALUATOR_VERSION
                    if context.spec_version == 2
                    else EVALUATOR_VERSION
                ),
                "inputs": {
                    "catalog": catalog.sha256,
                    "snapshot": snapshot.sha256,
                    "requirements": requirements.sha256,
                    "context": context.sha256,
                },
                "findings": document_findings,
            },
        },
        expected_type="cxp.evaluation",
    )
    return EvaluationResult(
        document=document,
        verdict=verdict,
        findings=detailed_findings,
    )
