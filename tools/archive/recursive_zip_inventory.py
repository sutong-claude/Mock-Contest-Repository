#!/usr/bin/env python3
"""Read-only recursive ZIP inventory.

Never extracts members to user-visible paths and never executes archive content.
Nested ZIPs are opened through SpooledTemporaryFile so large members spill to a
private temporary file instead of unbounded RAM.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import tempfile
import zipfile
from pathlib import Path
from typing import BinaryIO

CHUNK = 1024 * 1024
SPOOL_LIMIT = 64 * 1024 * 1024


def ext_of(name: str) -> str:
    base = name.rstrip("/").rsplit("/", 1)[-1]
    return Path(base).suffix.lower()


def sha256_path(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(CHUNK), b""):
            h.update(chunk)
    return h.hexdigest()


def copy_member_to_spool(
    src: BinaryIO, limit: int
) -> tuple[tempfile.SpooledTemporaryFile, str, int]:
    tmp = tempfile.SpooledTemporaryFile(max_size=SPOOL_LIMIT, mode="w+b")
    h = hashlib.sha256()
    total = 0
    try:
        while True:
            chunk = src.read(CHUNK)
            if not chunk:
                break
            total += len(chunk)
            if total > limit:
                raise ValueError(f"nested member exceeds limit: {total} > {limit}")
            h.update(chunk)
            tmp.write(chunk)
        tmp.seek(0)
        return tmp, h.hexdigest(), total
    except Exception:
        tmp.close()
        raise


class Inventory:
    def __init__(
        self,
        writer: csv.DictWriter,
        max_depth: int,
        max_entries: int,
        nested_max_bytes: int,
    ):
        self.writer = writer
        self.max_depth = max_depth
        self.max_entries = max_entries
        self.nested_max_bytes = nested_max_bytes
        self.entries = 0

    def add_row(self, **row: object) -> None:
        self.entries += 1
        if self.entries > self.max_entries:
            raise RuntimeError(f"entry limit exceeded: {self.max_entries}")
        self.writer.writerow(row)

    def walk(self, zf: zipfile.ZipFile, root: str, chain: str, depth: int) -> None:
        for info in zf.infolist():
            is_dir = info.is_dir()
            is_zip = (not is_dir) and ext_of(info.filename) == ".zip"
            note = ""
            nested_sha = ""
            nested_entries = ""
            nested_tmp = None
            nested_zf = None

            if is_zip:
                if depth >= self.max_depth:
                    note = "nested-skip:max-depth"
                elif info.file_size > self.nested_max_bytes:
                    note = "nested-skip:size-limit"
                else:
                    try:
                        with zf.open(info, "r") as src:
                            nested_tmp, nested_sha, _ = copy_member_to_spool(
                                src, self.nested_max_bytes
                            )
                        nested_zf = zipfile.ZipFile(nested_tmp, "r")
                        nested_entries = str(len(nested_zf.infolist()))
                        note = "nested-opened"
                    except (
                        zipfile.BadZipFile,
                        RuntimeError,
                        ValueError,
                        OSError,
                    ) as exc:
                        note = f"nested-error:{type(exc).__name__}"
                        if nested_tmp is not None:
                            nested_tmp.close()
                            nested_tmp = None

            self.add_row(
                root_archive=root,
                archive_chain=chain,
                depth=depth,
                name=info.filename,
                is_dir=int(is_dir),
                size=info.file_size,
                compressed_size=info.compress_size,
                crc32=f"{info.CRC:08x}",
                extension=ext_of(info.filename),
                is_zip=int(is_zip),
                nested_sha256=nested_sha,
                nested_entries=nested_entries,
                note=note,
            )

            if nested_zf is not None and nested_tmp is not None:
                try:
                    self.walk(
                        nested_zf,
                        root,
                        f"{chain}!{info.filename}",
                        depth + 1,
                    )
                finally:
                    nested_zf.close()
                    nested_tmp.close()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("archives", nargs="+", type=Path)
    ap.add_argument("-o", "--output", type=Path, required=True)
    ap.add_argument("--max-depth", type=int, default=8)
    ap.add_argument("--max-entries", type=int, default=200_000)
    ap.add_argument("--nested-max-bytes", type=int, default=2 * 1024**3)
    args = ap.parse_args()

    fields = [
        "root_archive",
        "archive_chain",
        "depth",
        "name",
        "is_dir",
        "size",
        "compressed_size",
        "crc32",
        "extension",
        "is_zip",
        "nested_sha256",
        "nested_entries",
        "note",
    ]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8-sig", newline="") as out:
        writer = csv.DictWriter(out, fieldnames=fields)
        writer.writeheader()
        inv = Inventory(
            writer,
            args.max_depth,
            args.max_entries,
            args.nested_max_bytes,
        )
        for path in args.archives:
            root = path.name
            inv.add_row(
                root_archive=root,
                archive_chain=root,
                depth=-1,
                name="__ROOT_ARCHIVE__",
                is_dir=0,
                size=path.stat().st_size,
                compressed_size="",
                crc32="",
                extension=path.suffix.lower(),
                is_zip=1,
                nested_sha256=sha256_path(path),
                nested_entries="",
                note="root",
            )
            with zipfile.ZipFile(path, "r") as zf:
                inv.walk(zf, root, root, 0)

    print(f"wrote {inv.entries} rows -> {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
