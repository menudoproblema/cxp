"""Errores de entrada separados de los veredictos de compatibilidad."""

from cxp.validation import ContractValidationError, ValidationIssue

__all__ = ("InvalidDocumentError", "UnsupportedContractError")


class InvalidDocumentError(ContractValidationError):
    """El documento incumple su forma, integridad o límites de recursos."""


class UnsupportedContractError(ContractValidationError):
    """No comprendemos una versión, familia o extensión obligatoria."""


def invalid(code: str, path: str, message: str) -> InvalidDocumentError:
    return InvalidDocumentError((ValidationIssue(code, path, message),))


def unsupported(code: str, path: str, message: str) -> UnsupportedContractError:
    return UnsupportedContractError((ValidationIssue(code, path, message),))
