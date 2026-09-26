"""The migration minor warns on the public legacy entrypoint."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def test_root_legacy_export_warns_without_warning_for_shared_validation() -> None:
    source = Path(__file__).resolve().parents[1] / "src"
    environment = os.environ.copy()
    environment["PYTHONPATH"] = os.pathsep.join(
        part for part in (str(source), environment.get("PYTHONPATH", "")) if part
    )
    script = """
import warnings
with warnings.catch_warnings(record=True) as observed:
    warnings.simplefilter('always', DeprecationWarning)
    from cxp import CapabilityDescriptor, ValidationIssue
assert CapabilityDescriptor.__name__ == 'CapabilityDescriptor'
assert ValidationIssue.__name__ == 'ValidationIssue'
assert len(observed) == 1
assert observed[0].category is DeprecationWarning
assert 'legacy component protocol' in str(observed[0].message)
"""
    result = subprocess.run(
        (sys.executable, "-c", script),
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
