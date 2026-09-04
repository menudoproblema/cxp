# Contributing to CXP

CXP is autonomous. Clone only this repository; no `_standards`, ecosystem RFC
registry, sibling project or internal service is needed. Python 3.12 is the
minimum. The exchange specification, schemas and vectors are owned here.

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -c requirements/release.txt -e '.[dev]'
python scripts/check.py
```

The dev extra includes the exchange dependencies needed by the complete suite.
The check runs `pre-commit run --all-files` (Ruff lint and formatting), mypy and
all pytest tests, without repeating the lint pass outside the hooks.
The local pre-commit hook checks the entire checkout, including untracked Python
files, rather than hiding new work from validation. The whole Python tree is
formatted and `ruff format --check .` is mandatory. Do not disable gates or
weaken global lint rules to close a fix.

New contracts need documented semantics, independent JSON Schema, positive and
negative vectors and explicit migration impact. Unknown critical extensions must
never produce a partial verdict. Catalog identifiers never authorize network
fetches or Python imports. Keep legacy behavior unless a change is documented.

`tests/fixtures/legacy-3.1-*` freeze evidence from the named MIT-licensed revision;
do not regenerate them from current code to make regressions pass. Portable
exchange vectors are under `src/cxp/exchange/vectors`; expected semantic outcomes
are authored from the specification, not captured blindly from the evaluator.
Tests run both Python jsonschema (runtime) and Rust jsonschema-rs (independent
test validator). Schema success does not replace semantic validation.

## Dependency policy

Runtime dependencies use reviewed compatible ranges because CXP is a library.
Every direct lower bound is installed together in the release matrix; the latest
allowed resolution is tested separately. Adding a runtime dependency requires a
clear owner, license review, bounded version range and an artifact-level test.
Development-only tools do not become runtime requirements.

GitHub Actions are pinned to full commit hashes and updated through reviewed
Dependabot changes. Pull requests changing dependency manifests run dependency
review and fail on newly introduced high-severity findings. Release evidence
records versions and license metadata from the isolated artifact environments,
not from the maintainer's active virtual environment.

## Candidate checks

```bash
python scripts/build_candidate.py
python scripts/verify_artifacts.py --dependencies minimum --dist dist/4.1.0
python scripts/verify_artifacts.py --dependencies latest --dist dist/4.1.0
```

Repeat artifact checks with `--python` for 3.12, 3.13 and 3.14, saving each report
with `--report dist/4.1.0/reports/<python>-<policy>.json`. These install both
wheel and sdist in separate base, exchange and development environments, copy
tests/examples/scripts from the sdist, and run without editable installs, source
injection or a sibling checkout. The minimum policy fixes every direct runtime
dependency at its declared floor; both policies run `pip check`.

Builds use a fixed SOURCE_DATE_EPOCH from the base revision. The builder normalizes
tar/gzip metadata and checks two independent consecutive builds byte for byte.
Source mtimes are never modified. An existing candidate is never overwritten;
an intentional `--replace-unpublished` keeps the prior directory as a recoverable
backup. Different Python/build-tool versions still
require rebuilding and verification; reproducibility is not promised across
arbitrary toolchains. Reports record actual
versions, hashes and source fingerprints; a changed source invalidates evidence.
Artifacts are version-scoped under `dist/<version>`; prior rc1 artifacts remain
untouched. Each matrix cell tests the base install without exchange dependencies
and the full dev/exchange install, for both wheel and sdist.
Run `python scripts/release_evidence.py` from a clean committed checkout to check
the complete local matrix. Publishing is a separate, manually dispatched GitHub
workflow protected by the `pypi` environment. It uses Trusted Publishing and the
same verified artifacts; it never rebuilds them in the privileged job.
See [release procedure](docs/release.md) for the separate publication decision.
