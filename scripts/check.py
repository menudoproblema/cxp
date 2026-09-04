"""Gates propios de CXP; no requieren otros repositorios."""

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main() -> None:
    env = os.environ.copy()
    env["PATH"] = str(Path(sys.executable).parent) + os.pathsep + env.get("PATH", "")
    for arguments in (
        ["scripts/check_docs.py"],
        ["pre_commit", "run", "--all-files"],
        ["mypy", "src"],
        ["pytest", "-q", "tests"],
    ):
        command = (
            [sys.executable, *arguments]
            if arguments[0].endswith(".py")
            else [sys.executable, "-m", *arguments]
        )
        subprocess.run(command, cwd=ROOT, env=env, check=True)


if __name__ == "__main__":
    main()
