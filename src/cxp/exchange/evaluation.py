"""Evaluación pura y trivaluada de requisitos entendidos y validados."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from fractions import Fraction
from typing import Literal, cast

from cxp.exchange.documents import Document, JsonObject
from cxp.exchange.errors import invalid
from cxp.exchange.registry import CatalogStore, property_value

__all__ = (
    "EVALUATOR_VERSION",
    "EvaluationFinding",
    "EvaluationOperand",
    "EvaluationResult",
    "evaluate_requirements",
    "evaluate_requirements_detailed",
)

EVALUATOR_VERSION = "1.0.0"
type EvaluationVerdict = Literal["compatible", "incompatible", "indeterminate"]
type OperandValue = str | bool | int | None


@dataclass(frozen=True, slots=True)
class EvaluationOperand:
    role: str
    value: OperandValue
    unit: str | None = None


@dataclass(frozen=True, slots=True)
class EvaluationFinding:
    requirement_id: str
    verdict: EvaluationVerdict
    code: str
    path: str
    snapshot_path: str | None
    message: str
    reason: str
    actual_reported: bool
    operands: tuple[EvaluationOperand, ...]


@dataclass(frozen=True, slots=True)
class EvaluationResult:
    document: Document
    verdict: EvaluationVerdict
    findings: tuple[EvaluationFinding, ...]

    @property
    def is_compatible(self) -> bool:
        return self.verdict == "compatible"


def _context_reason(snapshot: JsonObject, context: JsonObject) -> str | None:
    if snapshot["subject_id"] != context["subject_id"]:
        return "subject_mismatch"
    if snapshot["configuration_revision"] != context["configuration_revision"]:
        return "configuration_mismatch"
    if "as_of" not in context:
        return None
    observed = datetime.fromisoformat(snapshot["observed_at"])
    reference = datetime.fromisoformat(context["as_of"])
    if observed > reference:
        return "future_observation"
    if "max_age_seconds" in context:
        age = reference - observed
        exact_age = (
            age.days * 86400 + age.seconds + Fraction(age.microseconds, 1_000_000)
        )
        if exact_age > context["max_age_seconds"]:
            return "stale_observation"
    return None


def _operands(role: str, value: object) -> tuple[EvaluationOperand, ...]:
    if isinstance(value, list):
        return tuple(_operands(role, item)[0] for item in value)
    if isinstance(value, dict):
        return (EvaluationOperand(role, value["value"], unit=value["unit"]),)
    if value is None or type(value) in (str, bool, int):
        return (EvaluationOperand(role, cast(OperandValue, value)),)
    raise TypeError(f"Unexpected evaluation operand: {type(value).__name__}")


def _compare(
    node: JsonObject, value: object, definition: JsonObject
) -> tuple[bool, str, tuple[EvaluationOperand, ...]]:
    actual = property_value(value, definition, node["path"])
    operands = _operands("actual", value)
    operator = node["operator"]
    if operator == "equals":
        expected_value = property_value(node["value"], definition, "/value")
        matches = actual == expected_value
        reason = "requirement_satisfied" if matches else "value_not_equal"
        return matches, reason, operands + _operands("expected", node["value"])
    if operator == "one_of":
        allowed_values = tuple(
            property_value(item, definition, "/values") for item in node["values"]
        )
        matches = actual in allowed_values
        reason = "requirement_satisfied" if matches else "value_not_in_set"
        allowed = tuple(
            operand for item in node["values"] for operand in _operands("allowed", item)
        )
        return matches, reason, operands + allowed
    if operator == "contains_all":
        required = frozenset(node["values"])
        matches = isinstance(actual, frozenset) and required <= actual
        reason = "requirement_satisfied" if matches else "missing_set_elements"
        missing = sorted(required - actual) if isinstance(actual, frozenset) else []
        required_operands = tuple(
            EvaluationOperand("required", item) for item in node["values"]
        )
        missing_operands = tuple(EvaluationOperand("missing", item) for item in missing)
        return matches, reason, operands + required_operands + missing_operands
    if actual is None:
        return False, "null_not_comparable", operands
    if isinstance(actual, bool) or not isinstance(actual, (int, Fraction)):
        raise invalid("invalid_range", node["path"], "Expected numeric property")
    numbers: dict[str, int | Fraction] = {}
    limits: tuple[EvaluationOperand, ...] = ()
    for key in ("minimum", "maximum", "step", "origin"):
        if key not in node:
            continue
        expected = property_value(node[key], definition, f"/{key}", allow_null=False)
        if isinstance(expected, bool) or not isinstance(expected, (int, Fraction)):
            raise invalid("invalid_range", f"/{key}", "Expected numeric limit")
        numbers[key] = expected
        limits += _operands(key, node[key])
    if "minimum" in numbers and (
        actual < numbers["minimum"]
        or (actual == numbers["minimum"] and not node["minimum_inclusive"])
    ):
        reason = "minimum_excluded" if actual == numbers["minimum"] else "below_minimum"
        return False, reason, operands + limits
    if "maximum" in numbers and (
        actual > numbers["maximum"]
        or (actual == numbers["maximum"] and not node["maximum_inclusive"])
    ):
        reason = "maximum_excluded" if actual == numbers["maximum"] else "above_maximum"
        return False, reason, operands + limits
    matches = (
        "step" not in numbers
        or (Fraction(actual - numbers["origin"]) / numbers["step"]).denominator == 1
    )
    reason = "requirement_satisfied" if matches else "step_mismatch"
    return matches, reason, operands + limits


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
    """Validamos todas las ramas antes de obtener cualquier veredicto."""
    context.require_type("cxp.context")
    catalog = catalogs.validate_snapshot(snapshot)
    requirement_catalog = catalogs.validate_requirements(requirements)
    if catalog.sha256 != requirement_catalog.sha256:
        raise invalid(
            "catalog_mismatch",
            "/payload/catalog",
            "Snapshot and requirements must use the same exact catalog",
        )
    snapshot_data = snapshot.payload
    definitions = {item["name"]: item for item in catalog.payload["capabilities"]}
    observed = {item["name"]: item for item in snapshot_data["capabilities"]}
    observed_paths = {
        item["name"]: f"/payload/capabilities/{index}"
        for index, item in enumerate(snapshot_data["capabilities"])
    }
    context_reason = _context_reason(snapshot_data, context.payload)
    document_findings: list[JsonObject] = []
    detailed_findings: list[EvaluationFinding] = []

    def leaf(
        node: JsonObject,
    ) -> tuple[EvaluationVerdict, str, str, bool, tuple[EvaluationOperand, ...]]:
        if context_reason is not None:
            return "indeterminate", context_reason, context_reason, False, ()
        capability = observed.get(node["capability"])
        if capability is None:
            code = "capability_unreported"
            return "indeterminate", code, code, False, ()
        if capability["support"] == "unsupported":
            code = "unsupported_capability"
            return "incompatible", code, code, False, ()
        if node["require_effective"] and capability["support"] == "accepted_noop":
            code = "effective_support_required"
            return "incompatible", code, code, False, ()
        operations = {item["name"] for item in capability["operations"]}
        missing_operations = any(name not in operations for name in node["operations"])
        missing_property = False
        reason = "requirement_satisfied"
        actual_reported = False
        operands: tuple[EvaluationOperand, ...] = ()
        if node["operator"] != "support":
            name = node["path"].removeprefix("/properties/")
            if name not in capability["properties"]:
                missing_property = True
            else:
                actual_reported = True
                matches, reason, operands = _compare(
                    node,
                    capability["properties"][name],
                    definitions[node["capability"]]["properties"][name],
                )
                if not matches:
                    return (
                        "incompatible",
                        "property_mismatch",
                        reason,
                        actual_reported,
                        operands,
                    )
        if missing_operations:
            code = "operation_unreported"
            return "indeterminate", code, code, actual_reported, operands
        if missing_property:
            code = "property_unreported"
            return "indeterminate", code, code, False, ()
        return "compatible", "requirement_satisfied", reason, actual_reported, operands

    def visit(node: JsonObject, path: str) -> EvaluationVerdict:
        operator = node["operator"]
        if operator not in ("all", "any"):
            verdict, code, reason, actual_reported, operands = leaf(node)
            snapshot_path = observed_paths.get(node["capability"])
            if snapshot_path is not None and "path" in node:
                snapshot_path += node["path"]
            message = code.replace("_", " ")
            finding = {
                "requirement_id": node["id"],
                "verdict": verdict,
                "code": code,
                "path": path,
                "snapshot_path": snapshot_path,
                "message": message,
            }
            document_findings.append(finding)
            detailed_findings.append(
                EvaluationFinding(
                    requirement_id=node["id"],
                    verdict=verdict,
                    code=code,
                    path=path,
                    snapshot_path=snapshot_path,
                    message=message,
                    reason=reason,
                    actual_reported=actual_reported,
                    operands=operands,
                )
            )
            return verdict
        results = [
            visit(child, f"{path}/conditions/{index}")
            for index, child in enumerate(node["conditions"])
        ]
        dominant = "incompatible" if operator == "all" else "compatible"
        if dominant in results:
            return dominant
        if "indeterminate" in results:
            return "indeterminate"
        return "compatible" if operator == "all" else "incompatible"

    verdict = visit(requirements.payload["requirement"], "/payload/requirement")
    document = Document(
        {
            "document_type": "cxp.evaluation",
            "spec_version": 1,
            "payload": {
                "verdict": verdict,
                "evaluator_version": EVALUATOR_VERSION,
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
        findings=tuple(detailed_findings),
    )
