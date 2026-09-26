"""The standalone resource example exercises the public API and CLI."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

EXAMPLE = Path(__file__).resolve().parents[1] / "examples" / "resource_guarantees.py"


def test_resource_example_and_cli_from_external_catalog(tmp_path: Path) -> None:
    process = subprocess.run(
        [sys.executable, str(EXAMPLE), "--write-documents", str(tmp_path)],
        check=True,
        capture_output=True,
        text=True,
    )
    results = json.loads(process.stdout)
    assert results == {
        "compatible": {
            "outcome": "compatible",
            "codes": ["requirement_satisfied"],
            "admitted": True,
        },
        "incompatible": {
            "outcome": "incompatible",
            "codes": ["property_mismatch"],
            "admitted": False,
        },
        "missing": {
            "outcome": "indeterminate",
            "codes": ["property_unreported"],
            "admitted": False,
        },
        "source-excluded": {
            "outcome": "indeterminate",
            "codes": ["source_not_accepted"],
            "admitted": False,
        },
        "wrong-subject": {
            "outcome": "indeterminate",
            "codes": ["subject_mismatch"],
            "admitted": False,
        },
        "wrong-revision": {
            "outcome": "indeterminate",
            "codes": ["configuration_mismatch"],
            "admitted": False,
        },
        "expired": {
            "outcome": "indeterminate",
            "codes": ["stale_observation"],
            "admitted": False,
        },
        "wrong-report": {
            "outcome": "compatible",
            "codes": ["requirement_satisfied"],
            "admitted": False,
        },
        "invalid-document": {
            "outcome": "invalid",
            "codes": ["property_type_mismatch"],
            "admitted": False,
        },
    }

    for name, expected_exit in {
        "compatible": 0,
        "incompatible": 1,
        "missing": 3,
        "source-excluded": 3,
        "wrong-report": 0,
        "invalid-document": 4,
    }.items():
        case = tmp_path / name
        cli = subprocess.run(
            [
                sys.executable,
                "-m",
                "cxp.cli",
                "evaluate",
                "--catalog",
                str(tmp_path / "catalog.json"),
                "--snapshot",
                str(case / "snapshot.json"),
                "--requirements",
                str(tmp_path / "requirements.json"),
                "--context",
                str(case / "context.json"),
            ],
            capture_output=True,
            text=True,
        )
        assert cli.returncode == expected_exit, (name, cli.stderr)
        if expected_exit == 4:
            assert "property_type_mismatch" in cli.stderr
        else:
            assert (
                json.loads(cli.stdout)["payload"]["verdict"] == results[name]["outcome"]
            )
