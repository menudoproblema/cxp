"""Contrastamos PyPI y una instalación limpia tras una publicación autorizada."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

from release_support import project_version, revision


def _release(version: str) -> dict[str, object]:
    url = f"https://pypi.org/pypi/cxp/{version}/json"
    last_error = None
    for attempt in range(6):
        try:
            with urllib.request.urlopen(url, timeout=30) as response:
                return json.load(response)
        except urllib.error.HTTPError as error:
            last_error = error
            if error.code != 404 or attempt == 5:
                raise
            time.sleep(10)
    raise RuntimeError("PyPI release did not become visible") from last_error


def _run(arguments: list[str], *, cwd: Path, env: dict[str, str]) -> str:
    return subprocess.run(
        arguments,
        cwd=cwd,
        env=env,
        capture_output=True,
        check=True,
        text=True,
    ).stdout.strip()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dist", type=Path, required=True)
    parser.add_argument("--python", default=sys.executable)
    args = parser.parse_args()
    evidence = json.loads((args.dist / "release-evidence.json").read_text())
    version = project_version()
    if evidence["version"] != version:
        raise ValueError("Publication evidence and checked-out version differ")
    payload = _release(version)
    remote_files = {item["filename"]: item for item in payload["urls"]}
    for name, expected in evidence["artifacts"].items():
        remote = remote_files.get(name)
        if remote is None or remote["digests"]["sha256"] != expected:
            raise ValueError(f"PyPI artifact hash mismatch: {name}")
        with urllib.request.urlopen(remote["url"], timeout=60) as response:
            if hashlib.sha256(response.read()).hexdigest() != expected:
                raise ValueError(f"Downloaded PyPI artifact differs: {name}")

    env = os.environ.copy()
    env.pop("PYTHONPATH", None)
    env.pop("PYTHONHOME", None)
    env["PYTHONNOUSERSITE"] = "1"
    with tempfile.TemporaryDirectory(prefix="cxp-pypi-") as temporary:
        work = Path(temporary)
        environment = work / "venv"
        _run([args.python, "-m", "venv", str(environment)], cwd=work, env=env)
        python = environment / (
            "Scripts/python.exe" if os.name == "nt" else "bin/python"
        )
        console = environment / ("Scripts/cxp.exe" if os.name == "nt" else "bin/cxp")
        _run(
            [
                str(python),
                "-m",
                "pip",
                "install",
                "--no-cache-dir",
                f"cxp[exchange]=={version}",
            ],
            cwd=work,
            env=env,
        )
        _run([str(python), "-m", "pip", "check"], cwd=work, env=env)
        installed = _run([str(console), "--version"], cwd=work, env=env)
        catalogs = json.loads(
            _run([str(console), "catalog", "list"], cwd=work, env=env)
        )
        tutorial = json.loads(
            _run(
                [str(python), "-I", "-m", "cxp.exchange.tutorial"],
                cwd=work,
                env=env,
            )
        )
    if installed != version or len(catalogs) != 6:
        raise ValueError("Clean PyPI installation did not expose this release")
    if {item["verdict"] for item in tutorial.values()} != {
        "compatible",
        "incompatible",
        "indeterminate",
    }:
        raise ValueError("Published tutorial did not preserve all verdicts")
    publication = {
        "artifacts": evidence["artifacts"],
        "base_revision": revision(),
        "pypi_project_url": payload["info"]["project_url"],
        "status": "published_verified",
        "tag": f"v{version}",
        "version": version,
    }
    path = args.dist / "publication-evidence.json"
    path.write_text(json.dumps(publication, indent=2) + "\n", encoding="utf-8")
    print(path)


if __name__ == "__main__":
    main()
