"""Temporary warning helper for the legacy migration window."""

from __future__ import annotations

from warnings import warn


def warn_legacy_import(module: str) -> None:
    warn(
        f"{module} belongs to the legacy component protocol; "
        "use cxp.exchange and owner-authored catalogs instead",
        DeprecationWarning,
        stacklevel=3,
    )
