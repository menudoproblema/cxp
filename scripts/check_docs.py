"""Comprobamos que todos los enlaces locales de la documentación existan."""

from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parent.parent
LINK = re.compile(r"\[[^]]*\]\(([^)]+)\)")


def documentation_files() -> tuple[Path, ...]:
    roots = sorted(ROOT.glob("*.md"))
    return tuple([*roots, *sorted((ROOT / "docs").rglob("*.md"))])


def main() -> None:
    missing = []
    checked = 0
    for path in documentation_files():
        for raw_target in LINK.findall(path.read_text(encoding="utf-8")):
            target = raw_target.strip().strip("<>")
            if target.startswith(("#", "http://", "https://", "mailto:")):
                continue
            target = unquote(target.split("#", 1)[0])
            if not target:
                continue
            checked += 1
            if not (path.parent / target).resolve().exists():
                missing.append(f"{path.relative_to(ROOT)} -> {target}")
    if missing:
        raise ValueError("Missing local documentation links:\n" + "\n".join(missing))
    print(f"Documentation links: {checked} local targets valid")


if __name__ == "__main__":
    main()
