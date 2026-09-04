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

MINIMUM_DEPENDENCIES = (
    "msgspec==0.20.0",
    "jsonschema==4.23.0",
    "referencing==0.35.0",
    "rfc8785==0.1.4",
)
LATEST_DEPENDENCIES = (
    "msgspec>=0.20.0,<1",
    "jsonschema>=4.23,<5",
    "referencing>=0.35,<1",
    "rfc8785>=0.1.4,<1",
)
RUNTIME_DISTRIBUTIONS = (
    "cxp",
    "msgspec",
    "jsonschema",
    "jsonschema-specifications",
    "referencing",
    "rfc8785",
    "rpds-py",
    "attrs",
    "typing-extensions",
)


def run(arguments: list[str], *, cwd: Path, env: dict[str, str]) -> str:
    completed = subprocess.run(
        arguments, cwd=cwd, env=env, check=True, text=True, capture_output=True
    )
    return completed.stdout.strip()


def _python(environment: Path) -> Path:
    return environment / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def _console(environment: Path) -> Path:
    return environment / ("Scripts/cxp.exe" if os.name == "nt" else "bin/cxp")


def _new_environment(
    root: Path, name: str, python: str, env: dict[str, str]
) -> tuple[Path, Path]:
    environment = root / name
    run([python, "-m", "venv", str(environment)], cwd=root, env=env)
    executable = _python(environment)
    run(
        [str(executable), "-m", "pip", "install", "--upgrade", "pip"],
        cwd=root,
        env=env,
    )
    return environment, executable


def _install(
    python: Path,
    requirement: str,
    policy: str,
    *,
    cwd: Path,
    env: dict[str, str],
    include_exchange: bool = True,
) -> None:
    dependencies = MINIMUM_DEPENDENCIES if policy == "minimum" else LATEST_DEPENDENCIES
    if not include_exchange:
        dependencies = dependencies[:1]
    run(
        [
            str(python),
            "-m",
            "pip",
            "install",
            "--upgrade",
            requirement,
            *dependencies,
        ],
        cwd=cwd,
        env=env,
    )
    run([str(python), "-m", "pip", "check"], cwd=cwd, env=env)


def _metadata(python: Path, *, cwd: Path, env: dict[str, str]) -> dict[str, object]:
    names = json.dumps(RUNTIME_DISTRIBUTIONS)
    probe = (
        "import json,platform,sys; "
        "from importlib.metadata import PackageNotFoundError,distribution; "
        f"names={names}; items={{}}; "
        'exec("for name in names:\\n'
        " try:\\n"
        "  item=distribution(name); metadata=item.metadata; "
        "items[name]={'version':item.version,'license':"
        "metadata.get('License-Expression') or metadata.get('License'),"
        "'classifiers':[value for value in metadata.get_all('Classifier',[]) "
        "if value.startswith('License ::')]}\\n"
        " except PackageNotFoundError:\\n"
        '  pass"); '
        "print(json.dumps({'python':sys.version.split()[0],"
        "'platform':platform.platform(),'distributions':items}))"
    )
    return json.loads(run([str(python), "-I", "-c", probe], cwd=cwd, env=env))


def _verify_wheel_resources(wheel_path: Path) -> None:
    required = {
        "cxp/cli.py",
        "cxp/py.typed",
        "cxp/exchange/catalogs/document-processing.json",
        "cxp/exchange/catalogs/finishing.json",
        "cxp/exchange/catalogs/job-submission.json",
        "cxp/exchange/catalogs/physical-printing-1.1.0.json",
        "cxp/exchange/catalogs/physical-printing.json",
        "cxp/exchange/catalogs/software-service.json",
        "cxp/exchange/examples.py",
        "cxp/exchange/schemas/exchange-v1.json",
        "cxp/exchange/schemas/operations-v1.json",
        "cxp/exchange/tutorial.py",
        "cxp/exchange/vectors/exchange-v1.json",
    }
    with zipfile.ZipFile(wheel_path) as wheel:
        names = set(wheel.namelist())
        missing = sorted(required - names)
        if missing:
            raise ValueError(f"Missing wheel resources: {missing}")
        if not any(name.endswith("/licenses/LICENSE") for name in names):
            raise ValueError("Wheel license is missing")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument(
        "--dependencies",
        "--msgspec",
        dest="policy",
        choices=("minimum", "latest"),
        default="latest",
    )
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
        digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
        if manifest["artifacts"].get(artifact.name) != digest:
            raise ValueError("Artifact differs from the candidate manifest")
    _verify_wheel_resources(artifacts[0])

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
            artifact_kind = "wheel" if artifact.suffix == ".whl" else "sdist"
            case = work / artifact_kind
            case.mkdir()

            base_env, base_python = _new_environment(case, "base", args.python, env)
            _install(
                base_python,
                str(artifact),
                args.policy,
                cwd=case,
                env=env,
                include_exchange=False,
            )
            base_probe = run(
                [
                    str(base_python),
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
                [str(base_python), "-I", "-c", "import cxp.exchange"],
                cwd=case,
                env=env,
                capture_output=True,
                text=True,
            )
            if missing.returncode == 0 or "pip install 'cxp[exchange]'" not in (
                missing.stderr
            ):
                raise ValueError("Missing exchange dependencies need a clear error")
            console_version = run(
                [str(_console(base_env)), "--version"], cwd=case, env=env
            )
            run([str(_console(base_env)), "--help"], cwd=case, env=env)
            if console_version != manifest["version"]:
                raise ValueError("Installed CLI has the wrong version")

            exchange_env, exchange_python = _new_environment(
                case, "exchange", args.python, env
            )
            _install(
                exchange_python,
                f"{artifact}[exchange]",
                args.policy,
                cwd=case,
                env=env,
            )
            catalog_output = run(
                [str(_console(exchange_env)), "catalog", "list"],
                cwd=case,
                env=env,
            )
            if len(json.loads(catalog_output)) != 6:
                raise ValueError("Installed CLI did not discover all catalogs")
            tutorial = run(
                [str(exchange_python), "-I", "-m", "cxp.exchange.tutorial"],
                cwd=case,
                env=env,
            )
            if {item["verdict"] for item in json.loads(tutorial).values()} != {
                "compatible",
                "incompatible",
                "indeterminate",
            }:
                raise ValueError("Packaged tutorial does not cover all verdicts")

            dev_env, dev_python = _new_environment(case, "dev", args.python, env)
            _install(
                dev_python,
                f"{artifact}[dev]",
                args.policy,
                cwd=case,
                env=env,
            )
            checks = case / "checks"
            checks.mkdir()
            for name in ("tests", "examples", "scripts"):
                shutil.copytree(unpacked / name, checks / name)
            shutil.copyfile(unpacked / "pyproject.toml", checks / "pyproject.toml")
            origin = run(
                [
                    str(dev_python),
                    "-I",
                    "-c",
                    "import cxp; print(cxp.__file__)",
                ],
                cwd=checks,
                env=env,
            )
            if not Path(origin).resolve().is_relative_to(dev_env.resolve()):
                raise ValueError("CXP was imported outside the clean environment")
            tests = run(
                [str(dev_python), "-I", "-m", "pytest", "-q", "tests"],
                cwd=checks,
                env=env,
            )
            examples = run(
                [str(dev_python), "-I", "-m", "cxp.exchange.examples"],
                cwd=checks,
                env=env,
            )
            if set(json.loads(examples).values()) != {
                "compatible",
                "incompatible",
                "indeterminate",
            }:
                raise ValueError("Packaged examples do not cover all verdicts")

            installations = {
                "base": _metadata(base_python, cwd=case, env=env),
                "exchange": _metadata(exchange_python, cwd=case, env=env),
                "dev": _metadata(dev_python, cwd=case, env=env),
            }
            exchange_distributions = installations["exchange"]["distributions"]
            report = {
                "artifact": artifact.name,
                "base_without_exchange": "passed",
                "cli": "passed",
                "dependencies": {
                    "python": installations["exchange"]["python"],
                    "cxp": exchange_distributions["cxp"]["version"],
                },
                "dependency_policy": args.policy,
                "examples": "passed",
                "installations": installations,
                "pip_check": "passed",
                "sha256": hashlib.sha256(artifact.read_bytes()).hexdigest(),
                "source_sha256": manifest["source_sha256"],
                "tests": tests.splitlines()[-1],
                "tutorial": "passed",
            }
            reports.append(report)
            print(json.dumps(report), flush=True)

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
