"""Probamos wheel, consola, recursos y rutas reales en una instalación aislada."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


def run(arguments: list[str], *, cwd: Path, env: dict[str, str]) -> str:
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
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument("--dist", type=Path, required=True)
    args = parser.parse_args()
    wheels = list(args.dist.resolve().glob("cxp-*.whl"))
    if len(wheels) != 1:
        raise ValueError("Expected exactly one wheel")
    env = os.environ.copy()
    env.pop("PYTHONPATH", None)
    env.pop("PYTHONHOME", None)
    env["PYTHONNOUSERSITE"] = "1"
    with tempfile.TemporaryDirectory(prefix="cxp-smoke-") as temporary:
        work = Path(temporary) / "ruta con espacios ñ"
        work.mkdir()
        environment = work / "venv"
        run([args.python, "-m", "venv", str(environment)], cwd=work, env=env)
        python = environment / (
            "Scripts/python.exe" if os.name == "nt" else "bin/python"
        )
        console = environment / ("Scripts/cxp.exe" if os.name == "nt" else "bin/cxp")
        run(
            [str(python), "-m", "pip", "install", f"{wheels[0]}[exchange]"],
            cwd=work,
            env=env,
        )
        run([str(python), "-m", "pip", "check"], cwd=work, env=env)
        version = run([str(console), "--version"], cwd=work, env=env)
        catalogs = json.loads(run([str(console), "catalog", "list"], cwd=work, env=env))
        output = work / "catálogo físico 1.1.json"
        shown = run(
            [
                str(console),
                "catalog",
                "show",
                "physical-printing",
                "--version",
                "1.1.0",
            ],
            cwd=work,
            env=env,
        )
        output.write_text(shown + "\n", encoding="utf-8")
        receipt = json.loads(
            run(
                [
                    str(console),
                    "validate",
                    str(output),
                    "--type",
                    "cxp.catalog",
                ],
                cwd=work,
                env=env,
            )
        )
        print(
            json.dumps(
                {
                    "catalogs": len(catalogs),
                    "path": output.name,
                    "status": receipt["status"],
                    "version": version,
                },
                sort_keys=True,
            )
        )


if __name__ == "__main__":
    main()
