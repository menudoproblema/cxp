from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _run_example(path: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    return subprocess.run(
        [sys.executable, str(ROOT / path)],
        check=True,
        capture_output=True,
        text=True,
        env=env,
        cwd=ROOT,
    )


def test_sync_example_runs_successfully() -> None:
    completed = _run_example("examples/sync_provider.py")

    assert "accepted" in completed.stdout
    assert "TelemetrySnapshot(" in completed.stdout


def test_async_example_runs_successfully() -> None:
    completed = _run_example("examples/async_provider.py")

    assert "accepted" in completed.stdout
    assert "TelemetrySnapshot(" in completed.stdout


def test_async_stream_example_runs_successfully() -> None:
    completed = _run_example("examples/async_telemetry_stream.py")

    assert completed.stdout.count("TelemetrySnapshot(") == 2


def test_component_descriptors_example_runs_successfully() -> None:
    completed = _run_example("examples/component_descriptors.py")

    assert "CapabilityMatrix(" in completed.stdout
    assert "ComponentCapabilitySnapshot(" in completed.stdout
    assert "ComponentDependencyRule(" in completed.stdout
