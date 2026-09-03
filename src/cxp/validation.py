"""Diagnósticos compartidos sin dependencias del registro de catálogos."""

from __future__ import annotations

from collections.abc import Iterable

import msgspec

__all__ = (
    "ContractValidationError",
    "ValidationIssue",
    "ValidationResult",
)


class ValidationIssue(msgspec.Struct, frozen=True):
    code: str
    path: str
    message: str
    expected: str | None = None
    observed: str | None = None
    cause: str | None = None


class ValidationResult(msgspec.Struct, frozen=True):
    issues: tuple[ValidationIssue, ...] = ()

    def is_valid(self) -> bool:
        return not self.issues

    def messages(self) -> tuple[str, ...]:
        return tuple(issue.message for issue in self.issues)


class ContractValidationError(ValueError):
    def __init__(self, issues: Iterable[ValidationIssue]) -> None:
        self.issues = tuple(issues)
        super().__init__("; ".join(issue.message for issue in self.issues))


def duplicate_issues(
    names: Iterable[str], *, path: str, code: str
) -> tuple[ValidationIssue, ...]:
    seen: set[str] = set()
    issues: list[ValidationIssue] = []
    for index, name in enumerate(names):
        # Rechazamos identidades vacías incluso en objetos construidos en Python.
        if not isinstance(name, str) or not name:
            issues.append(
                ValidationIssue(
                    code="invalid_identifier",
                    path=f"{path}/{index}",
                    message="Declaration name must be a non-empty string",
                    observed=repr(name)[:512],
                )
            )
            continue
        # Señalamos cada repetición sin ocultar la primera declaración.
        if name in seen:
            issues.append(
                ValidationIssue(
                    code=code,
                    path=f"{path}/{index}",
                    message=f"Duplicate declaration: {name!r}",
                    observed=name,
                )
            )
        seen.add(name)
    return tuple(issues)


def validate_typed_metadata(
    value: object, schema: type[msgspec.Struct] | None, *, path: str
) -> ValidationResult:
    # Un catálogo sin esquema no impone una forma adicional a los metadatos.
    if schema is None:
        return ValidationResult()
    try:
        # Revalidamos también los Struct: su constructor no comprueba tipos.
        normalized = msgspec.to_builtins(value)
        msgspec.convert(normalized, type=schema, strict=True)
    except (TypeError, ValueError, msgspec.ValidationError, RecursionError) as error:
        return ValidationResult(
            issues=(
                ValidationIssue(
                    code="invalid_metadata",
                    path=path,
                    message="Metadata does not satisfy its declared schema",
                    expected=schema.__name__,
                    observed=repr(value)[:512],
                    cause=str(error)[:1024],
                ),
            )
        )
    return ValidationResult()
