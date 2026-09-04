"""Construimos una candidata local y registramos su fuente; no publicamos."""

import argparse
import hashlib
import importlib.metadata
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from release_support import (
    ROOT,
    git_is_clean,
    normalize_sdist,
    project_version,
    promote_candidate,
    release_directory,
    revision,
    source_fingerprint,
    tag_revision,
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--replace-unpublished", action="store_true")
    args = parser.parse_args()
    directory = release_directory()
    directory.parent.mkdir(parents=True, exist_ok=True)
    before = source_fingerprint()
    env = os.environ.copy()
    env["SOURCE_DATE_EPOCH"] = subprocess.check_output(
        ["git", "show", "-s", "--format=%ct", "HEAD"], cwd=ROOT, text=True
    ).strip()
    version = project_version()
    if tag_revision(f"v{version}") is not None:
        raise RuntimeError(f"Refusing to rebuild tagged version v{version}")
    artifact_names = (f"cxp-{version}-py3-none-any.whl", f"cxp-{version}.tar.gz")
    hashes = None
    with tempfile.TemporaryDirectory(
        prefix=f".cxp-{version}-build-", dir=directory.parent
    ) as temporary:
        temporary_path = Path(temporary)
        for number in (1, 2):
            output = temporary_path / str(number)
            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "build",
                    "--no-isolation",
                    "--outdir",
                    str(output),
                ],
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
                staged = temporary_path / "candidate"
                staged.mkdir()
                for name in artifact_names:
                    (output / name).replace(staged / name)
        if before != source_fingerprint():
            raise RuntimeError("Source changed during candidate build")
        manifest = {
            "artifacts": hashes,
            "base_revision": revision(),
            "build_environment": {
                "python": sys.version.split()[0],
                "tools": {
                    name: importlib.metadata.version(name)
                    for name in ("build", "setuptools", "twine", "wheel")
                },
            },
            "git_clean": git_is_clean(),
            "published": False,
            "reproducible_builds": 2,
            "source_date_epoch": env["SOURCE_DATE_EPOCH"],
            "source_sha256": before,
            "version": version,
        }
        (staged / "build-manifest.json").write_text(
            json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
        )
        if directory.exists():
            existing_manifest = directory / "build-manifest.json"
            if (
                existing_manifest.exists()
                and json.loads(existing_manifest.read_text(encoding="utf-8"))
                == manifest
            ):
                print(json.dumps(manifest, indent=2))
                return
        backup = promote_candidate(
            staged, directory, replace_unpublished=args.replace_unpublished
        )
        if backup is not None:
            print(
                f"Previous unpublished candidate retained at {backup}",
                file=sys.stderr,
            )
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
