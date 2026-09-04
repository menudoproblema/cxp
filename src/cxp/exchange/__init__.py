"""Intercambio enriquecido explícito, independiente de las APIs heredadas."""

from cxp.exchange.documents import Document, document_schema, load_document
from cxp.exchange.errors import InvalidDocumentError, UnsupportedContractError
from cxp.exchange.evaluation import (
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
