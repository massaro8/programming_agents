"""Bounded repository-local file access shared by portable engineering tools."""

from __future__ import annotations

import json
import re
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path, PureWindowsPath
from typing import Any

MAX_BYTES = 128 * 1024
SECRET = re.compile(
    r"(?i)(?:sk-[a-z0-9_-]{12,}|gh[pousr]_[a-z0-9]{12,}|"
    r"-----BEGIN [A-Z ]*PRIVATE KEY-----|"
    r"(?:password|secret|token|api[_-]?key)\s*[:=]\s*\S+)"
)


def local_path(root: Path, relative: str) -> Path:
    """Reject escaping, symlink and junction paths, including missing destinations."""
    path = Path(relative)
    windows = PureWindowsPath(relative)
    if (
        not relative
        or path.is_absolute()
        or windows.drive
        or windows.root
        or ".." in path.parts
        or "\\" in relative
        or ":" in relative
        or "\x00" in relative
    ):
        raise ValueError("expected a safe repository-relative path")
    current = root.absolute()
    for ancestor in current.parents:
        if ancestor.is_symlink() or ancestor.is_junction():
            raise ValueError("repository root has an unsafe ancestor")
    if current.is_symlink() or current.is_junction() or not current.is_dir():
        raise ValueError("repository root is missing or unsafe")
    for part in path.parts:
        current /= part
        if current.is_symlink() or current.is_junction():
            raise ValueError("repository path is unsafe")
    return current


def read_text(root: Path, relative: str) -> str:
    path = local_path(root, relative)
    if path.stat().st_size > MAX_BYTES:
        raise ValueError("repository artifact exceeds 128 KiB")
    return path.read_text(encoding="utf-8")


def read_json(root: Path, relative: str) -> dict[str, Any]:
    def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate JSON field")
            result[key] = value
        return result

    data = json.loads(read_text(root, relative), object_pairs_hook=unique_object)
    if not isinstance(data, dict):
        raise ValueError("expected a JSON object")
    return data


def write_json(root: Path, relative: str, data: dict[str, Any]) -> None:
    text = json.dumps(data, indent=2, sort_keys=True) + "\n"
    if len(text.encode()) > MAX_BYTES:
        raise ValueError("repository artifact exceeds 128 KiB")
    path = local_path(root, relative)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


@contextmanager
def repository_write(root: Path, relative: str) -> Iterator[None]:
    """Reject competing writers during an artifact's read/modify/write operation."""
    lock_relative = relative + ".lock"
    path = local_path(root, lock_relative)
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        stream = path.open("x", encoding="utf-8")
    except FileExistsError as exc:
        raise ValueError(
            f"repository update in progress: {relative}; retry after the writer finishes. "
            f"If interrupted, remove {lock_relative} only after confirming no writer is running"
        ) from exc
    try:
        yield
    finally:
        stream.close()
        local_path(root, lock_relative).unlink()


def durable_text(value: object) -> str:
    """Accept short summaries; reject recognizable credentials rather than storing them."""
    if not isinstance(value, str) or not value.strip() or len(value) > 2000:
        raise ValueError("expected a nonempty summary of at most 2000 characters")
    if SECRET.search(value):
        raise ValueError("summary contains a secret-like value; remove it before recording")
    return value
