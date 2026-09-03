"""Integridad de definiciones y relaciones de los catálogos heredados."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

import msgspec

from cxp.validation import ValidationIssue, duplicate_issues

if TYPE_CHECKING:
    from cxp.catalogs.base import CapabilityCatalog


def definition_is_immutable(catalog: CapabilityCatalog) -> bool:
    """Un Struct congelado puede contener listas: no memorizamos esos árboles."""
    pending: list[object] = [catalog]
    seen: set[int] = set()
    while pending:
        value = pending.pop()
        if (
            value is None
            or type(value) in (str, bool, int, float)
            or isinstance(value, type)
        ):
            continue
        if id(value) in seen:
            continue
        seen.add(id(value))
        if type(value) is tuple:
            pending.extend(value)
        elif (
            isinstance(value, msgspec.Struct)
            and value.__struct_config__.frozen
            and type(value).__module__ == "cxp.catalogs.base"
        ):
            pending.extend(getattr(value, field) for field in value.__struct_fields__)
        else:
            return False
    return True


def catalog_definition_issues(
    catalog: CapabilityCatalog,
) -> tuple[ValidationIssue, ...]:
    issues = list(
        duplicate_issues(
            catalog.capability_names(),
            path="/capabilities",
            code="duplicate_capability",
        )
    )
    issues.extend(
        duplicate_issues(
            (tier.name for tier in catalog.tiers),
            path="/tiers",
            code="duplicate_tier",
        )
    )
    issues.extend(
        duplicate_issues(
            catalog.satisfies_interfaces,
            path="/satisfies_interfaces",
            code="duplicate_interface",
        )
    )
    names = {name for name in catalog.capability_names() if isinstance(name, str)}
    for index, tier in enumerate(catalog.tiers):
        path = f"/tiers/{index}/required_capabilities"
        issues.extend(
            duplicate_issues(
                tier.required_capabilities, path=path, code="duplicate_tier_capability"
            )
        )
        for offset, name in enumerate(tier.required_capabilities):
            # La identidad inválida ya tiene diagnóstico; no la usamos como clave.
            if not isinstance(name, str):
                continue
            # Un tier debe nombrar capacidades del propio catálogo.
            if name not in names:
                issues.append(
                    ValidationIssue(
                        code="unknown_tier_capability",
                        path=f"{path}/{offset}",
                        message=(
                            f"Tier {tier.name!r} references unknown capability {name!r}"
                        ),
                        observed=name,
                    )
                )
    for index, capability in enumerate(catalog.capabilities):
        path = f"/capabilities/{index}"
        issues.extend(
            duplicate_issues(
                capability.operation_names(),
                path=f"{path}/operations",
                code="duplicate_operation",
            )
        )
        schemas = [(f"{path}/metadata_schema", capability.metadata_schema)]
        for offset, operation in enumerate(capability.operations):
            operation_path = f"{path}/operations/{offset}"
            schemas.extend(
                (
                    (f"{operation_path}/input_schema", operation.input_schema),
                    (f"{operation_path}/result_schema", operation.result_schema),
                )
            )
            # Un tiempo recomendado debe ser una duración positiva finita.
            timeout = operation.timeout_seconds
            try:
                valid_timeout = timeout is None or (
                    not isinstance(timeout, bool)
                    and math.isfinite(timeout)
                    and timeout > 0
                )
            except (TypeError, OverflowError):
                valid_timeout = False
            if not valid_timeout:
                issues.append(
                    ValidationIssue(
                        code="invalid_timeout",
                        path=f"{operation_path}/timeout_seconds",
                        message="Operation timeout must be positive and finite",
                    )
                )
        for schema_path, schema in schemas:
            # Conservamos None como ausencia de esquema, no como clase importable.
            if schema is not None and (
                not isinstance(schema, type) or not issubclass(schema, msgspec.Struct)
            ):
                issues.append(
                    ValidationIssue(
                        code="invalid_schema",
                        path=schema_path,
                        message="Metadata schema must be a msgspec.Struct type",
                    )
                )
        telemetry = capability.telemetry
        # Las definiciones repetidas entre capacidades pueden ser coherentes.
        if telemetry is None:
            continue
        families = (
            (
                "spans",
                [(value.name, value.required_attributes) for value in telemetry.spans],
            ),
            (
                "metrics",
                [(value.name, value.required_labels) for value in telemetry.metrics],
            ),
            (
                "events",
                [
                    (value.event_type, value.required_payload_keys)
                    for value in telemetry.events
                ],
            ),
        )
        for family, declarations in families:
            signal_path = f"{path}/telemetry/{family}"
            issues.extend(
                duplicate_issues(
                    (name for name, _ in declarations),
                    path=signal_path,
                    code="duplicate_telemetry_definition",
                )
            )
            for offset, (_, fields) in enumerate(declarations):
                issues.extend(
                    duplicate_issues(
                        (field.name for field in fields),
                        path=f"{signal_path}/{offset}/fields",
                        code="duplicate_telemetry_field",
                    )
                )
    return tuple(issues)


def catalog_relation_issues(
    catalog: CapabilityCatalog, parent: CapabilityCatalog
) -> tuple[ValidationIssue, ...]:
    issues: list[ValidationIssue] = []
    for index, capability in enumerate(catalog.capabilities):
        inherited = parent.get_capability(capability.name)
        # La relación no exige copiar capacidades ni inventa sus operaciones.
        if inherited is None:
            continue
        # Dos esquemas explícitos de una misma capacidad no son intercambiables.
        if (
            capability.metadata_schema is not None
            and inherited.metadata_schema is not None
            and capability.metadata_schema != inherited.metadata_schema
        ):
            issues.append(
                ValidationIssue(
                    code="conflicting_metadata_schema",
                    path=f"/capabilities/{index}/metadata_schema",
                    message=(
                        f"Capability {capability.name!r} has a conflicting "
                        f"metadata schema in {parent.interface!r}"
                    ),
                )
            )
        for offset, operation in enumerate(capability.operations):
            other = inherited.get_operation(operation.name)
            # Solo comparamos contratos que declaran la misma operación.
            if other is None:
                continue
            for field in ("result_type", "input_schema", "result_schema"):
                left = getattr(operation, field)
                right = getattr(other, field)
                # La ausencia de esquema en una familia permite especializarlo.
                if left is not None and right is not None and left != right:
                    issues.append(
                        ValidationIssue(
                            code="conflicting_operation_contract",
                            path=f"/capabilities/{index}/operations/{offset}/{field}",
                            message=(
                                f"Operation {operation.name!r} "
                                f"conflicts with {parent.interface!r}"
                            ),
                            expected=str(right),
                            observed=str(left),
                        )
                    )
    return tuple(issues)
