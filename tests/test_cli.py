"""La CLI conserva contratos, salidas y códigos aptos para automatización."""

from __future__ import annotations

import json
import subprocess
import sys
from importlib.resources import files
from pathlib import Path

import pytest

from cxp.exchange import load_reference_catalog

SUITE = json.loads(
    files("cxp.exchange").joinpath("vectors/exchange-v1.json").read_bytes()
)


def run_cli(*arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "cxp.cli", *arguments],
        capture_output=True,
        check=False,
        text=True,
    )


def write_json(path: Path, value: object) -> Path:
    path.write_text(json.dumps(value), encoding="utf-8")
    return path


def test_cli_help_version_schemas_and_catalog_discovery():
    assert run_cli("--help").returncode == 0
    version = run_cli("--version")
    assert version.returncode == 0
    assert version.stdout.strip()

    schema = run_cli("schema", "document")
    assert schema.returncode == 0
    assert json.loads(schema.stdout)["$id"] == "urn:cxp:schema:exchange:1"

    catalogs = run_cli("catalog", "list")
    assert catalogs.returncode == 0
    listed = json.loads(catalogs.stdout)
    assert ("physical-printing", "1.0.0") in {
        (item["name"], item["version"]) for item in listed
    }
    assert ("physical-printing", "1.1.0") in {
        (item["name"], item["version"]) for item in listed
    }
    shown = run_cli("catalog", "show", "physical-printing", "--version", "1.1.0")
    assert shown.returncode == 0
    assert json.loads(shown.stdout)["payload"]["identity"]["version"] == "1.1.0"


@pytest.mark.parametrize(
    "case_id,return_code",
    [("effective-support", 0), ("known-limit", 1), ("missing-property", 3)],
)
def test_cli_evaluate_preserves_all_three_verdicts(
    tmp_path: Path, case_id: str, return_code: int
):
    case = next(item for item in SUITE["evaluations"] if item["id"] == case_id)
    catalog = load_reference_catalog(case["catalog"])
    catalog_path = tmp_path / "catalog.json"
    catalog_path.write_bytes(catalog.to_bytes())
    paths = {
        name: write_json(tmp_path / f"{name}.json", case[name])
        for name in ("snapshot", "requirements", "context")
    }
    result = run_cli(
        "--diagnostics",
        "json",
        "evaluate",
        "--catalog",
        str(catalog_path),
        "--snapshot",
        str(paths["snapshot"]),
        "--requirements",
        str(paths["requirements"]),
        "--context",
        str(paths["context"]),
        "--explain",
    )
    assert result.returncode == return_code
    assert (
        json.loads(result.stdout)["payload"]["verdict"] == case["expected"]["verdict"]
    )
    explanation = json.loads(result.stderr)
    assert explanation["kind"] == "evaluation_explanation"
    assert explanation["format_version"] == 1


def test_cli_validate_reports_its_scope_and_structured_errors(tmp_path: Path):
    case = SUITE["evaluations"][0]
    snapshot_path = write_json(tmp_path / "snapshot.json", case["snapshot"])
    catalog = load_reference_catalog(case["catalog"])
    catalog_path = tmp_path / "catalog.json"
    catalog_path.write_bytes(catalog.to_bytes())
    result = run_cli(
        "validate",
        str(snapshot_path),
        "--type",
        "cxp.snapshot",
        "--catalog",
        str(catalog_path),
    )
    assert result.returncode == 0
    assert json.loads(result.stdout)["scope"] == "catalog"

    invalid_path = tmp_path / "invalid.json"
    invalid_path.write_text("{", encoding="utf-8")
    invalid = run_cli(
        "--diagnostics",
        "json",
        "validate",
        str(invalid_path),
        "--type",
        "cxp.snapshot",
    )
    assert invalid.returncode == 4
    assert invalid.stdout == ""
    diagnostic = json.loads(invalid.stderr)
    assert diagnostic["category"] == "invalid_document"
    assert diagnostic["issues"][0]["code"] == "invalid_json"
