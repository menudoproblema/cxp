"""Construimos una candidata local y registramos su fuente; no publicamos."""

import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from release_support import (
    ROOT,
    normalize_sdist,
    project_version,
    release_directory,
    revision,
    source_fingerprint,
)


def main() -> None:
    directory = release_directory()
    directory.mkdir(parents=True, exist_ok=True)
    before = source_fingerprint()
    env = os.environ.copy()
    env["SOURCE_DATE_EPOCH"] = subprocess.check_output(
        ["git", "show", "-s", "--format=%ct", "HEAD"], cwd=ROOT, text=True
    ).strip()
    version = project_version()
    artifact_names = (f"cxp-{version}-py3-none-any.whl", f"cxp-{version}.tar.gz")
    hashes = None
    with tempfile.TemporaryDirectory(prefix="cxp-build-") as temporary:
        for number in (1, 2):
            output = Path(temporary) / str(number)
            subprocess.run(
                [sys.executable, "-m", "build", "--outdir", str(output)],
                cwd=ROOT,
                env=env,
                check=True,
            )
            sdist = output / artifact_names[1]
            normalized = output / "normalized.tar.gz"
            normalize_sdist(sdist, normalized, int(env["SOURCE_DATE_EPOCH"]))
            normalized.replace(sdist)
            current = {
                name: hashlib.sha256((output / name).read_bytes()).hexdigest()
                for name in artifact_names
            }
            if hashes is not None and hashes != current:
                raise RuntimeError("Consecutive builds are not byte-reproducible")
            hashes = current
            if number == 2:
                subprocess.run(
                    [
                        sys.executable,
                        "-m",
                        "twine",
                        "check",
                        *(str(output / name) for name in artifact_names),
                    ],
                    check=True,
                )
                if before != source_fingerprint():
                    raise RuntimeError("Source changed during candidate build")
                for name in artifact_names:
                    (output / name).replace(directory / name)
    if before != source_fingerprint():
        raise RuntimeError("Source changed during candidate build")
    manifest = {
        "base_revision": revision(),
        "version": version,
        "reproducible_builds": 2,
        "source_sha256": before,
        "source_date_epoch": env["SOURCE_DATE_EPOCH"],
        "published": False,
        "artifacts": hashes,
    }
    (directory / "build-manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
