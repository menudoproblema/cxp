"""Separamos los artefactos exactos ya acreditados para un upload autorizado."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path

from release_support import (
    git_is_clean,
    project_version,
    revision,
    source_fingerprint,
    tag_revision,
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dist", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(f"Publication output already exists: {args.output}")
    evidence = json.loads((args.dist / "release-evidence.json").read_text())
    version = project_version()
    current_revision = revision()
    if evidence["status"] != "local_release_verified":
        raise ValueError("Candidate does not have closed local release evidence")
    if evidence["version"] != version:
        raise ValueError("Candidate version differs from the checked-out source")
    if evidence["source_sha256"] != source_fingerprint() or not git_is_clean():
        raise ValueError("Publication requires the exact clean candidate source")
    if evidence["base_revision"] != current_revision:
        raise ValueError("Candidate was built from another revision")
    if tag_revision(f"v{version}") != current_revision:
        raise ValueError(f"Tag v{version} must identify the candidate revision")
    artifacts = evidence["artifacts"]
    if len(artifacts) != 2:
        raise ValueError("Expected exactly one wheel and one sdist")
    args.output.mkdir(parents=True)
    for name, expected in artifacts.items():
        source = args.dist / name
        if hashlib.sha256(source.read_bytes()).hexdigest() != expected:
            raise ValueError(f"Candidate artifact changed: {name}")
        shutil.copy2(source, args.output / name)
    print(
        json.dumps(
            {
                "artifacts": artifacts,
                "revision": current_revision,
                "tag": f"v{version}",
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
