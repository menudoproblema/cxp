"""Public imports resolved on demand to keep the exchange core isolated."""

from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cxp.exchange.documents import Document, document_schema, load_document
    from cxp.exchange.errors import InvalidDocumentError, UnsupportedContractError
    from cxp.exchange.evaluation import (
        CONTEXT_V2_EVALUATOR_VERSION,
        EVALUATOR_VERSION,
        EvaluationFinding,
        EvaluationOperand,
        EvaluationResult,
        evaluate_requirements,
        evaluate_requirements_detailed,
    )
    from cxp.exchange.negotiation import (
        SUPPORTED_FORMATS,
        ExchangeAgreement,
        negotiate_exchange,
    )
    from cxp.exchange.quantities import Quantity, normalize_decimal, quantity_from_input
    from cxp.exchange.reference import (
        REFERENCE_CATALOGS,
        ReferenceCatalogInfo,
        legacy_idempotency,
        list_reference_catalogs,
        load_reference_catalog,
        operation_schema,
        validate_operation_payload,
    )
    from cxp.exchange.registry import CatalogStore, catalog_reference

_EXPORT_MODULES = {
    "CONTEXT_V2_EVALUATOR_VERSION": "cxp.exchange.evaluation",
    "CatalogStore": "cxp.exchange.registry",
    "Document": "cxp.exchange.documents",
    "EVALUATOR_VERSION": "cxp.exchange.evaluation",
    "EvaluationFinding": "cxp.exchange.evaluation",
    "EvaluationOperand": "cxp.exchange.evaluation",
    "EvaluationResult": "cxp.exchange.evaluation",
    "ExchangeAgreement": "cxp.exchange.negotiation",
    "InvalidDocumentError": "cxp.exchange.errors",
    "Quantity": "cxp.exchange.quantities",
    "REFERENCE_CATALOGS": "cxp.exchange.reference",
    "ReferenceCatalogInfo": "cxp.exchange.reference",
    "SUPPORTED_FORMATS": "cxp.exchange.negotiation",
    "UnsupportedContractError": "cxp.exchange.errors",
    "catalog_reference": "cxp.exchange.registry",
    "document_schema": "cxp.exchange.documents",
    "evaluate_requirements": "cxp.exchange.evaluation",
    "evaluate_requirements_detailed": "cxp.exchange.evaluation",
    "legacy_idempotency": "cxp.exchange.reference",
    "list_reference_catalogs": "cxp.exchange.reference",
    "load_document": "cxp.exchange.documents",
    "load_reference_catalog": "cxp.exchange.reference",
    "negotiate_exchange": "cxp.exchange.negotiation",
    "normalize_decimal": "cxp.exchange.quantities",
    "operation_schema": "cxp.exchange.reference",
    "quantity_from_input": "cxp.exchange.quantities",
    "validate_operation_payload": "cxp.exchange.reference",
}

__all__ = (
    "REFERENCE_CATALOGS",
    "ReferenceCatalogInfo",
    "legacy_idempotency",
    "load_reference_catalog",
    "operation_schema",
    "validate_operation_payload",
    "CatalogStore",
    "Document",
    "EVALUATOR_VERSION",
    "CONTEXT_V2_EVALUATOR_VERSION",
    "EvaluationFinding",
    "EvaluationOperand",
    "EvaluationResult",
    "ExchangeAgreement",
    "InvalidDocumentError",
    "Quantity",
    "SUPPORTED_FORMATS",
    "UnsupportedContractError",
    "catalog_reference",
    "document_schema",
    "evaluate_requirements",
    "evaluate_requirements_detailed",
    "list_reference_catalogs",
    "load_document",
    "negotiate_exchange",
    "normalize_decimal",
    "quantity_from_input",
)


def __getattr__(name: str):
    module_name = _EXPORT_MODULES.get(name)
    if module_name is None:
        raise AttributeError(name)
    value = getattr(import_module(module_name), name)
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    return sorted({*globals(), *__all__})
