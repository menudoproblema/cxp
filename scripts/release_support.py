"""Identificamos el checkout exacto, incluyendo cambios aún sin commit."""

import gzip
import hashlib
import runpy
import subprocess
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def project_version() -> str:
    return runpy.run_path(str(ROOT / "src/cxp/_version.py"))["__version__"]


def release_directory() -> Path:
    return ROOT / "dist" / project_version()


def normalize_sdist(source: Path, destination: Path, epoch: int) -> None:
    """Fijamos tar y gzip sin modificar fechas ni contenido del checkout."""
    if source.resolve() == destination.resolve():
        raise ValueError("Normalize to a different path before replacing an artifact")
    with tarfile.open(source, "r:gz") as archive:
        members = sorted(archive.getmembers(), key=lambda item: item.name)
        if len({item.name for item in members}) != len(members):
            raise ValueError("Duplicate source archive paths")
        with destination.open("wb") as raw:
            with gzip.GzipFile(
                filename="", mode="wb", fileobj=raw, mtime=epoch, compresslevel=9
            ) as compressed:
                with tarfile.open(
                    fileobj=compressed, mode="w", format=tarfile.PAX_FORMAT
                ) as result:
                    for member in members:
                        if not (member.isfile() or member.isdir()):
                            raise ValueError(
                                f"Unsupported source archive entry: {member.name}"
                            )
                        info = tarfile.TarInfo(member.name)
                        info.type = member.type
                        info.size = member.size if member.isfile() else 0
                        info.mtime = epoch
                        info.mode = (
                            0o755 if member.isdir() or member.mode & 0o111 else 0o644
                        )
                        # TarInfo arranca sin propietarios ni cabeceras PAX heredadas.
                        if member.isfile():
                            data = archive.extractfile(member)
                            if data is None:
                                raise ValueError(f"Missing archive data: {member.name}")
                            with data:
                                result.addfile(info, data)
                        else:
                            result.addfile(info)


def source_fingerprint() -> str:
    names = subprocess.check_output(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        cwd=ROOT,
    ).split(b"\0")
    digest = hashlib.sha256()
    for name in sorted(set(names) - {b""}):
        path = ROOT / name.decode("utf-8")
        digest.update(name + b"\0")
        # El permiso de ejecución también forma parte de la fuente comprobada.
        digest.update(
            str(path.stat().st_mode & 0o777).encode() if path.exists() else b"0"
        )
        digest.update(
            hashlib.sha256(path.read_bytes()).digest() if path.is_file() else b"deleted"
        )
    return digest.hexdigest()


def revision() -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()
