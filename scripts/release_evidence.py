"""Cerramos evidencia local exacta sin convertirla en autorización de publicación."""

import hashlib
import json
import re

from release_support import (
    git_is_clean,
    project_version,
    release_directory,
    revision,
    source_fingerprint,
)


def main() -> None:
    candidate = release_directory()
    manifest = json.loads((candidate / "build-manifest.json").read_text())
    if manifest["source_sha256"] != source_fingerprint():
        raise ValueError("Source changed: rebuild and rerun the matrix")
    if not git_is_clean() or not manifest.get("git_clean"):
        raise ValueError("Release evidence requires a clean committed checkout")
    if manifest["base_revision"] != revision():
        raise ValueError("Candidate base revision is not the current commit")
    if manifest["version"] != project_version() or manifest["reproducible_builds"] != 2:
        raise ValueError("The target release has not passed reproducible builds")
    for name, expected in manifest["artifacts"].items():
        if hashlib.sha256((candidate / name).read_bytes()).hexdigest() != expected:
            raise ValueError(f"Artifact changed: {name}")
    reports = []
    for path in sorted((candidate / "reports").glob("*.json")):
        reports.extend(json.loads(path.read_text()))
    keys = set()
    for report in reports:
        if report["source_sha256"] != manifest["source_sha256"]:
            raise ValueError("A matrix report belongs to another source")
        if manifest["artifacts"].get(report["artifact"]) != report["sha256"]:
            raise ValueError("A matrix report belongs to another artifact")
        if re.fullmatch(r"[0-9]+ passed in .+", report["tests"]) is None:
            raise ValueError("A matrix report has incomplete tests")
        if (
            report["examples"] != "passed"
            or report["dependencies"]["cxp"] != manifest["version"]
            or report["base_without_exchange"] != "passed"
            or report["cli"] != "passed"
            or report["pip_check"] != "passed"
            or report["tutorial"] != "passed"
        ):
            raise ValueError("A matrix report did not pass the target release checks")
        if set(report["installations"]) != {"base", "exchange", "dev"}:
            raise ValueError("A matrix report lacks an isolated installation")
        base = report["installations"]["base"]["distributions"]
        exchange = report["installations"]["exchange"]["distributions"]
        if set(base) != {"cxp", "msgspec"}:
            raise ValueError("The base installation contains exchange dependencies")
        if not {"cxp", "msgspec", "jsonschema", "referencing", "rfc8785"} <= set(
            exchange
        ):
            raise ValueError("The exchange installation lacks runtime dependencies")
        if report["dependency_policy"] == "minimum" and {
            name: exchange[name]["version"]
            for name in ("msgspec", "jsonschema", "referencing", "rfc8785")
        } != {
            "msgspec": "0.20.0",
            "jsonschema": "4.23.0",
            "referencing": "0.35.0",
            "rfc8785": "0.1.4",
        }:
            raise ValueError("Minimum dependency versions were not preserved")
        python = ".".join(report["dependencies"]["python"].split(".")[:2])
        keys.add((python, report["dependency_policy"], report["artifact"]))
    required = {
        (python, policy, artifact)
        for python in ("3.12", "3.13", "3.14")
        for policy in ("minimum", "latest")
        for artifact in manifest["artifacts"]
    }
    if keys != required:
        raise ValueError(f"Incomplete matrix: missing {sorted(required - keys)}")
    evidence = {
        **manifest,
        "status": "local_release_verified",
        "matrix": reports,
        "runtime_dependency_license_metadata": {
            "source": "isolated artifact verification reports",
            "matrix": [
                {
                    "artifact": report["artifact"],
                    "dependency_policy": report["dependency_policy"],
                    "python": report["dependencies"]["python"],
                    "distributions": report["installations"]["exchange"][
                        "distributions"
                    ],
                }
                for report in reports
            ],
        },
        "publication_authorized": False,
        "publication_conditions": [
            "Explicit maintainer authorization for exact artifacts and destination",
            "Consumer owners confirm constraints and integration evidence",
            "Rerun gates after any source or artifact change",
            "Post-publication clean installation from the authorized destination",
        ],
    }
    path = candidate / "release-evidence.json"
    path.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
    print(path)


if __name__ == "__main__":
    main()
