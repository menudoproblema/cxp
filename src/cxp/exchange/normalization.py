"""Semántica intrínseca previa a la resolución de referencias de catálogo."""

from __future__ import annotations

import re
from datetime import UTC, datetime
from fractions import Fraction
from typing import Any

from cxp.exchange.errors import invalid, unsupported
from cxp.exchange.property_values import property_value
from cxp.exchange.quantities import Quantity
from cxp.validation import ValidationIssue


def catalog_v2_shape_issues(content: dict[str, Any]) -> list[ValidationIssue]:
    """Report duplicate authored domain members before schema oneOf errors."""
    if (content.get("document_type"), content.get("spec_version")) != (
        "cxp.catalog",
        2,
    ):
        return []
    payload = content.get("payload")
    if not isinstance(payload, dict) or not isinstance(
        payload.get("capabilities"), list
    ):
        return []
    issues: list[ValidationIssue] = []
    for capability_index, capability in enumerate(payload["capabilities"]):
        if not isinstance(capability, dict) or not isinstance(
            capability.get("properties"), dict
        ):
            continue
        for name, definition in capability["properties"].items():
            if not isinstance(definition, dict) or not isinstance(
                definition.get("domain"), dict
            ):
                continue
            domain = definition["domain"]
            if domain.get("mode") != "closed" or not isinstance(
                domain.get("values"), list
            ):
                continue
            seen: set[str] = set()
            for index, value in enumerate(domain["values"]):
                if not isinstance(value, str):
                    continue
                if value in seen:
                    issues.append(
                        ValidationIssue(
                            "duplicate_domain_value",
                            f"/payload/capabilities/{capability_index}/properties/{name}/domain/values/{index}",
                            "Domain values must be unique",
                        )
                    )
                seen.add(value)
    return sorted(issues, key=lambda issue: (issue.path, issue.code))[:100]


def requirement_shape_issues(content: dict[str, Any]) -> list[ValidationIssue]:
    """Precisamos errores conocidos antes del oneOf, sin interpretar datos opacos."""
    payload = content.get("payload")
    if content.get("document_type") != "cxp.requirements" or not isinstance(
        payload, dict
    ):
        return []
    issues: list[ValidationIssue] = []

    def visit(node: object, path: str) -> None:
        if not isinstance(node, dict):
            return
        operator = node.get("operator")
        if operator in ("all", "any"):
            children = node.get("conditions")
            if isinstance(children, list):
                for index, child in enumerate(children):
                    visit(child, f"{path}/conditions/{index}")
        elif operator == "range":
            for field, other, code in (
                ("step", "origin", "step_requires_origin"),
                ("origin", "step", "origin_requires_step"),
            ):
                if field in node and other not in node:
                    issues.append(
                        ValidationIssue(
                            code, f"{path}/{other}", f"{field} requires {other}"
                        )
                    )
        elif operator == "contains_all":
            values = node.get("values")
            if not isinstance(values, list) or not all(
                isinstance(item, str) for item in values
            ):
                return
            seen: set[str] = set()
            for index, value in enumerate(values):
                if value in seen:
                    issues.append(
                        ValidationIssue(
                            "duplicate_set_value",
                            f"{path}/values/{index}",
                            "Set values must be unique",
                        )
                    )
                seen.add(value)

    visit(payload.get("requirement"), "/payload/requirement")
    return sorted(issues, key=lambda issue: (issue.path, issue.code))[:100]


def unique(values: list[str], path: str, code: str = "duplicate_identifier") -> None:
    seen: set[str] = set()
    for index, value in enumerate(values):
        if value in seen:
            raise invalid(code, f"{path}/{index}", f"Duplicate identifier: {value!r}")
        seen.add(value)


def timestamp(value: str, path: str) -> str:
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as error:
        raise invalid("invalid_timestamp", path, "Invalid UTC timestamp") from error
    return (
        parsed.astimezone(UTC).isoformat(timespec="microseconds").replace("+00:00", "Z")
    )


def _extensions(node: dict[str, Any], path: str) -> None:
    extensions = node.setdefault("extensions", {})
    critical = node.setdefault("critical_extensions", [])
    for index, name in enumerate(critical):
        if name not in extensions:
            raise invalid(
                "missing_critical_extension",
                f"{path}/critical_extensions/{index}",
                "Critical extension has no value",
            )
    if critical:
        raise unsupported(
            "unknown_critical_extension",
            f"{path}/critical_extensions",
            "Document requires an extension this evaluator does not implement",
        )


def _value(value: Any) -> Any:
    if isinstance(value, dict):
        return Quantity(value["value"], value["unit"]).as_dict()
    if isinstance(value, list):
        return sorted(value)
    return value


def _identity(identity: dict[str, Any], path: str) -> None:
    # SemVer no permite ceros iniciales en identificadores prerelease numéricos.
    version = identity["version"].split("+", 1)[0]
    if "-" in version:
        for part in version.split("-", 1)[1].split("."):
            if re.fullmatch("[0-9]+", part) and len(part) > 1 and part.startswith("0"):
                raise invalid(
                    "invalid_version",
                    f"{path}/version",
                    "Invalid numeric prerelease identifier",
                )


def normalize_payload(content: dict[str, Any]) -> None:
    _extensions(content, "")
    kind = content["document_type"]
    payload = content["payload"]
    if kind == "cxp.catalog":
        _identity(payload["identity"], "/payload/identity")
        unique(
            [item["name"] for item in payload["capabilities"]],
            "/payload/capabilities",
        )
        for index, capability in enumerate(payload["capabilities"]):
            path = f"/payload/capabilities/{index}"
            unique(
                [item["name"] for item in capability["operations"]],
                f"{path}/operations",
            )
            for name, definition in capability["properties"].items():
                definition.setdefault("nullable", False)
                if content["spec_version"] == 2:
                    property_path = f"{path}/properties/{name}"
                    domain = definition.get("domain")
                    if domain is not None and domain["mode"] == "closed":
                        unique(
                            domain["values"],
                            f"{property_path}/domain/values",
                            "duplicate_domain_value",
                        )
                        domain["values"].sort()
                    bounds = definition.get("bounds")
                    if bounds is not None:
                        numbers: dict[str, int | Fraction] = {}
                        for key in ("minimum", "maximum"):
                            if key not in bounds:
                                continue
                            number = property_value(
                                bounds[key],
                                definition,
                                f"{property_path}/bounds/{key}",
                                allow_null=False,
                                check_constraints=False,
                            )
                            if isinstance(number, bool) or not isinstance(
                                number, (int, Fraction)
                            ):
                                raise invalid(
                                    "invalid_catalog_bounds",
                                    f"{property_path}/bounds/{key}",
                                    "Catalog bounds require numeric values",
                                )
                            numbers[key] = number
                        for key in numbers:
                            bounds.setdefault(f"{key}_inclusive", True)
                        if "minimum" in numbers and "maximum" in numbers:
                            minimum, maximum = numbers["minimum"], numbers["maximum"]
                            if minimum > maximum or (
                                minimum == maximum
                                and not (
                                    bounds["minimum_inclusive"]
                                    and bounds["maximum_inclusive"]
                                )
                            ):
                                raise invalid(
                                    "invalid_catalog_bounds",
                                    f"{property_path}/bounds",
                                    "Catalog bounds are empty or inverted",
                                )
            for operation in capability["operations"]:
                operation.setdefault("idempotency", {"state": "unknown"})
    elif kind == "cxp.snapshot":
        _identity(payload["catalog"], "/payload/catalog")
        payload["observed_at"] = timestamp(
            payload["observed_at"], "/payload/observed_at"
        )
        unique(
            [item["name"] for item in payload["capabilities"]],
            "/payload/capabilities",
        )
        for index, capability in enumerate(payload["capabilities"]):
            operations = capability.setdefault("operations", [])
            unique(
                [item["name"] for item in operations],
                f"/payload/capabilities/{index}/operations",
            )
            capability["properties"] = {
                key: _value(value) for key, value in capability["properties"].items()
            }
    elif kind == "cxp.context":
        if content["spec_version"] == 2:
            payload["accepted_sources"].sort()
        if "as_of" in payload:
            payload["as_of"] = timestamp(payload["as_of"], "/payload/as_of")
    elif kind == "cxp.requirements":
        _identity(payload["catalog"], "/payload/catalog")
        identifiers: set[str] = set()

        def visit(node: dict[str, Any], path: str) -> None:
            _extensions(node, path)
            if node["id"] in identifiers:
                raise invalid(
                    "duplicate_requirement", f"{path}/id", "Duplicate requirement id"
                )
            identifiers.add(node["id"])
            if len(identifiers) > 1000:
                raise invalid("resource_limit", path, "Too many requirement nodes")
            if node["operator"] in ("all", "any"):
                for index, child in enumerate(node["conditions"]):
                    visit(child, f"{path}/conditions/{index}")
                return
            node.setdefault("require_effective", True)
            node.setdefault("operations", [])
            for field in ("value", "minimum", "maximum", "step", "origin"):
                if field in node:
                    node[field] = _value(node[field])
            if node["operator"] == "range":
                node.setdefault("minimum_inclusive", True)
                node.setdefault("maximum_inclusive", True)
            if "values" in node:
                node["values"] = [_value(item) for item in node["values"]]
                if node["operator"] == "contains_all":
                    node["values"].sort()

        visit(payload["requirement"], "/payload/requirement")
    elif kind in ("cxp.exchange_request", "cxp.exchange_response"):
        unique(
            [item["document_type"] for item in payload["formats"]],
            "/payload/formats",
        )
    elif kind == "cxp.evaluation":
        unique(
            [item["requirement_id"] for item in payload["findings"]],
            "/payload/findings",
        )
