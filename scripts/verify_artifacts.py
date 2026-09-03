"""Instalamos wheel y sdist aislados y probamos el contenido distribuido."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import zipfile
from pathlib import Path

from release_support import release_directory, source_fingerprint


def run(arguments: list[str], *, cwd: Path, env: dict[str, str]) -> str:
    completed = subprocess.run(
        arguments, cwd=cwd, env=env, check=True, text=True, capture_output=True
    )
    return completed.stdout.strip()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--msgspec", choices=("minimum", "latest"), default="latest")
    parser.add_argument("--dist", type=Path, default=release_directory())
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    manifest = json.loads((args.dist / "build-manifest.json").read_text())
    if manifest["source_sha256"] != source_fingerprint():
        raise ValueError("Source changed since candidate build; rebuild first")
    artifacts = sorted(args.dist.resolve().glob("cxp-*.whl")) + sorted(
        args.dist.resolve().glob("cxp-*.tar.gz")
    )
    if len(artifacts) != 2:
        raise ValueError("Use a directory containing exactly one wheel and one sdist")
    for artifact in artifacts:
        if (
            manifest["artifacts"].get(artifact.name)
            != hashlib.sha256(artifact.read_bytes()).hexdigest()
        ):
            raise ValueError("Artifact differs from the candidate manifest")
    required = (
        "cxp/py.typed",
        "cxp/exchange/schemas/exchange-v1.json",
        "cxp/exchange/schemas/operations-v1.json",
        "cxp/exchange/vectors/exchange-v1.json",
        "cxp/exchange/examples.py",
    )
    with zipfile.ZipFile(artifacts[0]) as wheel:
        names = wheel.namelist()
        for name in required:
            if name not in names:
                raise ValueError(f"Missing wheel resource: {name}")
        if (
            len([name for name in names if name.startswith("cxp/exchange/catalogs/")])
            != 5
        ):
            raise ValueError("Wheel must include all five reference catalogs")
        if not any(name.endswith("/licenses/LICENSE") for name in names):
            raise ValueError("Wheel license is missing")
    env = os.environ.copy()
    env.pop("PYTHONPATH", None)
    env.pop("PYTHONHOME", None)
    env["PYTHONNOUSERSITE"] = "1"
    reports = []
    with tempfile.TemporaryDirectory(prefix="cxp-artifacts-") as temporary:
        work = Path(temporary)
        source = work / "source"
        source.mkdir()
        with tarfile.open(artifacts[1]) as archive:
            archive.extractall(source, filter="data")
        roots = list(source.iterdir())
        if len(roots) != 1:
            raise ValueError("Expected a single sdist root")
        unpacked = roots[0]
        for artifact in artifacts:
            case = work / ("wheel" if artifact.suffix == ".whl" else "sdist")
            case.mkdir()
            environment = case / "venv"
            run([args.python, "-m", "venv", str(environment)], cwd=case, env=env)
            python = environment / (
                "Scripts/python.exe" if os.name == "nt" else "bin/python"
            )
            constraint = (
                "msgspec==0.20.0" if args.msgspec == "minimum" else "msgspec>=0.20.0,<1"
            )
            run(
                [
                    str(python),
                    "-m",
                    "pip",
                    "install",
                    "--upgrade",
                    str(artifact),
                    constraint,
                ],
                cwd=case,
                env=env,
            )
            # Probamos primero el paquete base sin instalar ningún extra.
            base_probe = run(
                [
                    str(python),
                    "-I",
                    "-c",
                    (
                        "import cxp,sys; from importlib.util import find_spec; "
                        "assert 'cxp.exchange' not in sys.modules; "
                        "assert all(find_spec(name) is None for name in "
                        "('jsonschema','rfc8785','referencing','rpds')); "
                        "assert cxp.CapabilityMatrix().capabilities == (); "
                        "print(cxp.__version__)"
                    ),
                ],
                cwd=case,
                env=env,
            )
            if base_probe != manifest["version"]:
                raise ValueError("Wrong base package version")
            missing = subprocess.run(
                [str(python), "-I", "-c", "import cxp.exchange"],
                cwd=case,
                env=env,
                capture_output=True,
                text=True,
            )
            if (
                missing.returncode == 0
                or "pip install 'cxp[exchange]'" not in missing.stderr
            ):
                raise ValueError(
                    "Missing exchange dependencies must have a clear error"
                )
            run(
                [str(python), "-m", "pip", "install", f"{artifact}[dev]", constraint],
                cwd=case,
                env=env,
            )
            checks = case / "checks"
            checks.mkdir()
            for name in ("tests", "examples", "scripts"):
                shutil.copytree(unpacked / name, checks / name)
            shutil.copyfile(unpacked / "pyproject.toml", checks / "pyproject.toml")
            # No copiamos src: incluso los tests recorren el paquete instalado.
            probe = run(
                [
                    str(python),
                    "-I",
                    "-c",
                    (
                        "import json,sys,cxp,msgspec; "
                        "from importlib.metadata import version; "
                        "from importlib.resources import files; "
                        "assert files('cxp').joinpath('py.typed').is_file(); "
                        "print(json.dumps({'python':sys.version.split()[0],"
                        "'cxp':cxp.__version__,'msgspec':msgspec.__version__,"
                        "'jsonschema':version('jsonschema'),'rfc8785':version('rfc8785'),"
                        "'referencing':version('referencing'),"
                        "'origin':cxp.__file__}))"
                    ),
                ],
                cwd=checks,
                env=env,
            )
            details = json.loads(probe)
            if (
                not Path(details["origin"])
                .resolve()
                .is_relative_to(environment.resolve())
            ):
                raise ValueError("CXP was imported outside the clean environment")
            result = run(
                [str(python), "-I", "-m", "pytest", "-q", "tests"], cwd=checks, env=env
            )
            examples = run(
                [str(python), "-I", "-m", "cxp.exchange.examples"], cwd=checks, env=env
            )
            if set(json.loads(examples).values()) != {
                "compatible",
                "incompatible",
                "indeterminate",
            }:
                raise ValueError("Packaged examples do not cover all verdicts")
            details.pop("origin")
            reports.append(
                {
                    "artifact": artifact.name,
                    "source_sha256": manifest["source_sha256"],
                    "sha256": hashlib.sha256(artifact.read_bytes()).hexdigest(),
                    "dependencies": details,
                    "msgspec_policy": args.msgspec,
                    "base_without_exchange": "passed",
                    "tests": result.splitlines()[-1],
                    "examples": "passed",
                }
            )
            print(json.dumps(reports[-1]), flush=True)
    if source_fingerprint() != manifest["source_sha256"]:
        raise ValueError("Source changed during verification; evidence is stale")
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(reports, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as error:
        print(error.stdout, file=sys.stderr)
        print(error.stderr, file=sys.stderr)
        raise
