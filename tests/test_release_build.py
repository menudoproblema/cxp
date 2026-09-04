"""Verificamos archivos reproducibles sin cambiar el checkout ni sus fechas."""

import gzip
import importlib.util
import io
import json
import tarfile
from pathlib import Path

import pytest

SPEC = importlib.util.spec_from_file_location(
    "cxp_release_support",
    Path(__file__).resolve().parent.parent / "scripts/release_support.py",
)
assert SPEC is not None and SPEC.loader is not None
SUPPORT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SUPPORT)


def write_archive(path, *, reverse, timestamp):
    with path.open("wb") as raw:
        with gzip.GzipFile(
            filename=path.name, fileobj=raw, mode="wb", mtime=timestamp
        ) as stream:
            with tarfile.open(
                fileobj=stream, mode="w", format=tarfile.PAX_FORMAT
            ) as archive:
                names = [
                    "cxp-4.0.0/",
                    "cxp-4.0.0/script.sh",
                    "cxp-4.0.0/" + "ñ" * 70 + ".txt",
                ]
                for name in reversed(names) if reverse else names:
                    info = tarfile.TarInfo(name)
                    info.type = (
                        tarfile.DIRTYPE if name.endswith("/") else tarfile.REGTYPE
                    )
                    data = b"payload\n"
                    info.size = len(data) if info.isfile() else 0
                    info.mode = 0o775 if name.endswith(".sh") else 0o664
                    info.uid = timestamp
                    info.uname = f"builder-{timestamp}"
                    info.mtime = timestamp + 0.123
                    info.pax_headers = {
                        "mtime": str(info.mtime),
                        "atime": str(timestamp),
                    }
                    archive.addfile(info, io.BytesIO(data) if info.isfile() else None)


def test_sdist_bytes_ignore_mtime_owners_order_and_gzip_filename(tmp_path):
    outputs = []
    for index in range(2):
        source, output = (
            tmp_path / f"source-{index}.tar.gz",
            tmp_path / f"out-{index}.tar.gz",
        )
        write_archive(source, reverse=bool(index), timestamp=1000 + index * 1000)
        original = source.read_bytes()
        SUPPORT.normalize_sdist(source, output, 12345)
        assert source.read_bytes() == original
        outputs.append(output.read_bytes())
        with tarfile.open(output) as archive:
            for member in archive:
                assert member.mtime == 12345
                assert member.uid == member.gid == 0
                assert member.uname == member.gname == ""
                assert "atime" not in member.pax_headers
                if member.isfile():
                    assert archive.extractfile(member).read() == b"payload\n"
                if member.name.endswith("script.sh"):
                    assert member.mode == 0o755
    assert outputs[0] == outputs[1]
    assert int.from_bytes(outputs[0][4:8], "little") == 12345


def test_sdist_normalization_cannot_truncate_its_source(tmp_path):
    source = tmp_path / "source.tar.gz"
    write_archive(source, reverse=False, timestamp=1000)
    original = source.read_bytes()
    with pytest.raises(ValueError, match="different path"):
        SUPPORT.normalize_sdist(source, source, 1)
    assert source.read_bytes() == original


def test_candidate_promotion_never_overwrites_silently(tmp_path):
    destination = tmp_path / "4.1.0"
    destination.mkdir()
    (destination / "old.txt").write_text("old", encoding="utf-8")
    staged = tmp_path / "staged"
    staged.mkdir()
    (staged / "new.txt").write_text("new", encoding="utf-8")
    with pytest.raises(FileExistsError):
        SUPPORT.promote_candidate(staged, destination, replace_unpublished=False)
    assert (destination / "old.txt").read_text(encoding="utf-8") == "old"
    assert (staged / "new.txt").read_text(encoding="utf-8") == "new"


def test_candidate_replacement_is_recoverable_and_published_is_immutable(tmp_path):
    destination = tmp_path / "4.1.0"
    destination.mkdir()
    (destination / "old.txt").write_text("old", encoding="utf-8")
    staged = tmp_path / "staged"
    staged.mkdir()
    (staged / "new.txt").write_text("new", encoding="utf-8")
    backup = SUPPORT.promote_candidate(staged, destination, replace_unpublished=True)
    assert backup is not None
    assert (backup / "old.txt").read_text(encoding="utf-8") == "old"
    assert (destination / "new.txt").read_text(encoding="utf-8") == "new"

    replacement = tmp_path / "replacement"
    replacement.mkdir()
    (destination / "publication-evidence.json").write_text(
        json.dumps({"status": "published_verified"}), encoding="utf-8"
    )
    with pytest.raises(RuntimeError, match="published"):
        SUPPORT.promote_candidate(replacement, destination, replace_unpublished=True)
