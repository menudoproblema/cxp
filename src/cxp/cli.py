"""Interfaz de consola fina sobre los contratos públicos de CXP."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Callable, Sequence
from dataclasses import asdict
from pathlib import Path
from typing import Any

from cxp._version import __version__

DOCUMENT_TYPES = (
    "cxp.catalog",
    "cxp.snapshot",
    "cxp.requirements",
    "cxp.context",
    "cxp.evaluation",
    "cxp.exchange_request",
    "cxp.exchange_response",
)
OPTIONAL_DEPENDENCIES = {"jsonschema", "referencing", "rfc8785"}
MAX_DOCUMENT_BYTES = 1024 * 1024


def _json_bytes(value: object) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, separators=(",", ":"), sort_keys=True
    ).encode("utf-8")


def _write_stdout(value: bytes) -> None:
    sys.stdout.buffer.write(value + b"\n")


def _read_document(path: Path, expected_type: str) -> Any:
    from cxp.exchange import load_document

    with path.open("rb") as stream:
        content = stream.read(MAX_DOCUMENT_BYTES + 1)
    return load_document(content, expected_type=expected_type)


def _load_store(paths: Sequence[Path]) -> Any:
    from cxp.exchange import CatalogStore

    return CatalogStore(_read_document(path, "cxp.catalog") for path in paths)


def _validate(args: argparse.Namespace) -> int:
    document = _read_document(args.path, args.document_type)
    scope = "document"
    if args.catalog:
        if args.document_type not in ("cxp.snapshot", "cxp.requirements"):
            raise ValueError(
                "Catalog validation only applies to snapshots and requirements"
            )
        store = _load_store(args.catalog)
        if args.document_type == "cxp.snapshot":
            store.validate_snapshot(document)
        else:
            store.validate_requirements(document)
        scope = "catalog"
    receipt = {
        "document_type": document.document_type,
        "format_version": 1,
        "scope": scope,
        "sha256": document.sha256,
        "spec_version": document.spec_version,
        "status": "valid",
    }
    _write_stdout(_json_bytes(receipt))
    return 0


def _explanation_bytes(result: Any) -> bytes:
    return _json_bytes(
        {
            "findings": [asdict(finding) for finding in result.findings],
            "format_version": 1,
            "kind": "evaluation_explanation",
            "verdict": result.verdict,
        }
    )


def _write_explanation(result: Any, diagnostics: str) -> None:
    if diagnostics == "json":
        sys.stderr.buffer.write(_explanation_bytes(result) + b"\n")
        return
    for finding in result.findings:
        location = (
            f"; snapshot={finding.snapshot_path}"
            if finding.snapshot_path is not None
            else ""
        )
        print(
            f"{finding.requirement_id}: {finding.verdict}; "
            f"{finding.code}/{finding.reason}{location}",
            file=sys.stderr,
        )


def _evaluate(args: argparse.Namespace) -> int:
    from cxp.exchange import evaluate_requirements_detailed

    catalogs = _load_store(args.catalog)
    result = evaluate_requirements_detailed(
        _read_document(args.snapshot, "cxp.snapshot"),
        _read_document(args.requirements, "cxp.requirements"),
        _read_document(args.context, "cxp.context"),
        catalogs=catalogs,
    )
    _write_stdout(result.document.to_bytes())
    if args.explain:
        _write_explanation(result, args.diagnostics)
    return {"compatible": 0, "incompatible": 1, "indeterminate": 3}[result.verdict]


def _schema_document(args: argparse.Namespace) -> int:
    from cxp.exchange import document_schema

    _write_stdout(_json_bytes(document_schema()))
    return 0


def _schema_operation(args: argparse.Namespace) -> int:
    from cxp.exchange import operation_schema

    _write_stdout(_json_bytes(operation_schema(args.contract_type)))
    return 0


def _catalog_list(args: argparse.Namespace) -> int:
    from cxp.exchange import list_reference_catalogs

    _write_stdout(_json_bytes([asdict(item) for item in list_reference_catalogs()]))
    return 0


def _catalog_show(args: argparse.Namespace) -> int:
    from cxp.exchange import load_reference_catalog

    document = load_reference_catalog(args.name, version=args.version)
    _write_stdout(document.to_bytes())
    return 0


def _add_diagnostics(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--diagnostics",
        choices=("text", "json"),
        default=argparse.SUPPRESS,
        help="presentation of diagnostics written to stderr",
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cxp", description=__doc__)
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument(
        "--diagnostics",
        choices=("text", "json"),
        default="text",
        help="presentation of diagnostics written to stderr",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    validate = commands.add_parser("validate", help="validate one CXP document")
    validate.add_argument("path", type=Path)
    validate.add_argument(
        "--type", dest="document_type", choices=DOCUMENT_TYPES, required=True
    )
    validate.add_argument("--catalog", action="append", type=Path, default=[])
    _add_diagnostics(validate)
    validate.set_defaults(handler=_validate)

    evaluate = commands.add_parser("evaluate", help="evaluate CXP requirements")
    evaluate.add_argument("--catalog", action="append", type=Path, required=True)
    evaluate.add_argument("--snapshot", type=Path, required=True)
    evaluate.add_argument("--requirements", type=Path, required=True)
    evaluate.add_argument("--context", type=Path, required=True)
    evaluate.add_argument("--explain", action="store_true")
    _add_diagnostics(evaluate)
    evaluate.set_defaults(handler=_evaluate)

    schema = commands.add_parser("schema", help="print a packaged schema")
    schema_commands = schema.add_subparsers(dest="schema_command", required=True)
    schema_document = schema_commands.add_parser("document")
    _add_diagnostics(schema_document)
    schema_document.set_defaults(handler=_schema_document)
    schema_operation = schema_commands.add_parser("operation")
    schema_operation.add_argument("contract_type")
    _add_diagnostics(schema_operation)
    schema_operation.set_defaults(handler=_schema_operation)

    catalog = commands.add_parser("catalog", help="inspect reference catalogs")
    catalog_commands = catalog.add_subparsers(dest="catalog_command", required=True)
    catalog_list = catalog_commands.add_parser("list")
    _add_diagnostics(catalog_list)
    catalog_list.set_defaults(handler=_catalog_list)
    catalog_show = catalog_commands.add_parser("show")
    catalog_show.add_argument("name")
    catalog_show.add_argument("--version")
    _add_diagnostics(catalog_show)
    catalog_show.set_defaults(handler=_catalog_show)
    return parser


def _error_payload(category: str, error: BaseException) -> dict[str, Any]:
    issues = getattr(error, "issues", ())
    return {
        "category": category,
        "format_version": 1,
        "issues": [
            {
                "code": issue.code,
                "message": issue.message,
                "path": issue.path,
            }
            for issue in issues
        ]
        or [{"code": category, "message": str(error), "path": ""}],
        "status": "error",
    }


def _write_error(category: str, error: BaseException, diagnostics: str) -> None:
    payload = _error_payload(category, error)
    if diagnostics == "json":
        sys.stderr.buffer.write(_json_bytes(payload) + b"\n")
        return
    for issue in payload["issues"]:
        path = f" at {issue['path']}" if issue["path"] else ""
        print(f"{issue['code']}{path}: {issue['message']}", file=sys.stderr)


def main(argv: Sequence[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    handler: Callable[[argparse.Namespace], int] = args.handler
    try:
        return handler(args)
    except ModuleNotFoundError as error:
        if error.name not in OPTIONAL_DEPENDENCIES:
            raise
        _write_error("optional_dependency_missing", error, args.diagnostics)
        return 2
    except Exception as error:
        from cxp.exchange import InvalidDocumentError, UnsupportedContractError

        if isinstance(error, UnsupportedContractError):
            category, return_code = "unsupported_contract", 5
        elif isinstance(error, InvalidDocumentError):
            category, return_code = "invalid_document", 4
        elif isinstance(error, OSError):
            category, return_code = "io_error", 6
        elif isinstance(error, ValueError):
            category, return_code = "invalid_input", 4
        else:
            category, return_code = "internal_error", 70
        _write_error(category, error, args.diagnostics)
        return return_code


if __name__ == "__main__":
    raise SystemExit(main())
