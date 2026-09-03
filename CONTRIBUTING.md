# Contributing to CXP

CXP is autonomous. Clone only this repository; no `_standards`, ecosystem RFC
registry, sibling project or internal service is needed. Python 3.12 is the
minimum. The exchange specification, schemas and vectors are owned here.

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -e '.[dev]'
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

## Candidate checks

```bash
python scripts/build_candidate.py
python scripts/verify_artifacts.py --msgspec minimum --dist dist/4.0.0
python scripts/verify_artifacts.py --msgspec latest --dist dist/4.0.0
```

Repeat artifact checks with `--python` for 3.12, 3.13 and 3.14, saving each report
with `--report dist/4.0.0/reports/<python>-<policy>.json`. These install both wheel and
sdist in clean environments, copy tests/examples/scripts from the sdist, and run
without editable installs, source injection or a sibling checkout.

Builds use a fixed SOURCE_DATE_EPOCH from the base revision. The builder normalizes
tar/gzip metadata and checks two independent consecutive builds byte for byte.
Source mtimes are never modified. Different Python/build-tool versions still
require rebuilding and verification; reproducibility is not promised across
arbitrary toolchains. Reports record actual
versions, hashes and source fingerprints; a changed source invalidates evidence.
Artifacts are version-scoped under `dist/<version>`; prior rc1 artifacts remain
untouched. Each matrix cell tests the base install without exchange dependencies
and the full dev/exchange install, for both wheel and sdist.
Run `python scripts/release_evidence.py` to check the complete local matrix.
See [release procedure](docs/release.md) for the separate publication decision.
