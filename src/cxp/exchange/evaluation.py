"""Evaluación pura y trivaluada de requisitos entendidos y validados."""

from __future__ import annotations

from datetime import datetime
from fractions import Fraction

from cxp.exchange.documents import Document, JsonObject
from cxp.exchange.errors import invalid
from cxp.exchange.registry import CatalogStore, property_value

__all__ = ("EVALUATOR_VERSION", "evaluate_requirements")

EVALUATOR_VERSION = "1.0.0"


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


def _matches(node: JsonObject, value: object, definition: JsonObject) -> bool:
    actual = property_value(value, definition, node["path"])
    operator = node["operator"]
    if operator == "equals":
        return actual == property_value(node["value"], definition, "/value")
    if operator == "one_of":
        return any(
            actual == property_value(item, definition, "/values")
            for item in node["values"]
        )
    if operator == "contains_all":
        return isinstance(actual, frozenset) and frozenset(node["values"]) <= actual
    if actual is None:
        return False
    if isinstance(actual, bool) or not isinstance(actual, (int, Fraction)):
        raise invalid("invalid_range", node["path"], "Expected numeric property")
    numbers: dict[str, int | Fraction] = {}
    for key in ("minimum", "maximum", "step", "origin"):
        if key not in node:
            continue
        expected = property_value(node[key], definition, f"/{key}", allow_null=False)
        if isinstance(expected, bool) or not isinstance(expected, (int, Fraction)):
            raise invalid("invalid_range", f"/{key}", "Expected numeric limit")
        numbers[key] = expected
    if "minimum" in numbers and (
        actual < numbers["minimum"]
        or (actual == numbers["minimum"] and not node["minimum_inclusive"])
    ):
        return False
    if "maximum" in numbers and (
        actual > numbers["maximum"]
        or (actual == numbers["maximum"] and not node["maximum_inclusive"])
    ):
        return False
    return (
        "step" not in numbers
        or (Fraction(actual - numbers["origin"]) / numbers["step"]).denominator == 1
    )


def evaluate_requirements(
    snapshot: Document,
    requirements: Document,
    context: Document,
    *,
    catalogs: CatalogStore,
) -> Document:
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
    findings: list[JsonObject] = []

    def leaf(node: JsonObject) -> tuple[str, str]:
        if context_reason is not None:
            return "indeterminate", context_reason
        capability = observed.get(node["capability"])
        if capability is None:
            return "indeterminate", "capability_unreported"
        if capability["support"] == "unsupported":
            return "incompatible", "unsupported_capability"
        if node["require_effective"] and capability["support"] == "accepted_noop":
            return "incompatible", "effective_support_required"
        operations = {item["name"] for item in capability["operations"]}
        missing_operations = any(name not in operations for name in node["operations"])
        missing_property = False
        if node["operator"] != "support":
            name = node["path"].removeprefix("/properties/")
            if name not in capability["properties"]:
                missing_property = True
            elif not _matches(
                node,
                capability["properties"][name],
                definitions[node["capability"]]["properties"][name],
            ):
                return "incompatible", "property_mismatch"
        if missing_operations:
            return "indeterminate", "operation_unreported"
        if missing_property:
            return "indeterminate", "property_unreported"
        return "compatible", "requirement_satisfied"

    def visit(node: JsonObject, path: str) -> str:
        operator = node["operator"]
        if operator not in ("all", "any"):
            verdict, code = leaf(node)
            snapshot_path = observed_paths.get(node["capability"])
            if snapshot_path is not None and "path" in node:
                snapshot_path += node["path"]
            findings.append(
                {
                    "requirement_id": node["id"],
                    "verdict": verdict,
                    "code": code,
                    "path": path,
                    "snapshot_path": snapshot_path,
                    "message": code.replace("_", " "),
                }
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
    return Document(
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
                "findings": findings,
            },
        },
        expected_type="cxp.evaluation",
    )
