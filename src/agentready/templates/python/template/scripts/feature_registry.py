#!/usr/bin/env python3
"""Maintain the repository-local feature specification registry.

This file intentionally uses only the Python standard library.  Feature
specifications are the source of truth; ``index.md`` is a deterministic view.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import tempfile
import unicodedata
from dataclasses import dataclass
from pathlib import Path

STATUSES = ("BACKLOG", "READY", "IN_PROGRESS", "BLOCKED", "DONE")
_FILENAME = re.compile(r"^F(?P<number>[0-9]{3,})-(?P<slug>[a-z0-9]+(?:-[a-z0-9]+)*)\.md$")
_HEADER = re.compile(r"^# (?P<id>F[0-9]+) — (?P<title>.+)$")


class RegistryError(ValueError):
    """A malformed feature registry or invalid command argument."""


@dataclass(frozen=True)
class Feature:
    number: int
    feature_id: str
    slug: str
    title: str
    status: str
    filename: str


def _canonical_id(number: int) -> str:
    return f"F{number:03d}"


def title_slug(title: str) -> str:
    """Return a deterministic lowercase ASCII slug for a feature title."""

    ascii_title = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", ascii_title).strip("-").lower()
    if not slug:
        raise RegistryError("title does not produce a non-empty ASCII slug")
    return slug


def _parse_feature(path: Path) -> Feature:
    match = _FILENAME.fullmatch(path.name)
    if match is None:
        raise RegistryError(f"invalid feature filename: {path.name}")
    number = int(match.group("number"))
    if number <= 0:
        raise RegistryError(f"feature ID must be positive: {path.name}")
    feature_id = _canonical_id(number)
    if match.group("number") != feature_id[1:]:
        raise RegistryError(f"feature ID is not canonically padded: {path.name}")
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        raise RegistryError(f"cannot read {path.name}: {exc}") from exc
    if len(lines) < 3 or lines[1] != "":
        raise RegistryError(f"{path.name} must start with a title, blank line, and status")
    header = _HEADER.fullmatch(lines[0])
    if header is None or header.group("id") != feature_id:
        raise RegistryError(f"filename/header ID mismatch: {path.name}")
    title = header.group("title").strip()
    if not title:
        raise RegistryError(f"feature title is empty: {path.name}")
    if title_slug(title) != match.group("slug"):
        raise RegistryError(f"filename slug does not match title: {path.name}")
    status_line = lines[2]
    status = status_line.removeprefix("Status: ")
    if status_line != f"Status: {status}" or status not in STATUSES:
        raise RegistryError(f"invalid feature status in {path.name}")
    return Feature(number, feature_id, match.group("slug"), title, status, path.name)


def read_features(root: Path) -> list[Feature]:
    docs = root / "docs"
    directory = root / "docs" / "features"
    if docs.is_symlink() or not docs.is_dir() or not directory.is_dir() or directory.is_symlink():
        raise RegistryError("docs/features directory is missing or unsafe")
    features: list[Feature] = []
    seen: set[int] = set()
    try:
        entries = sorted(directory.iterdir(), key=lambda item: item.name)
    except OSError as exc:
        raise RegistryError(f"cannot inspect docs/features: {exc}") from exc
    for path in entries:
        if path.is_symlink():
            raise RegistryError(f"unsafe feature entry: {path.name}")
        if path.is_dir():
            continue
        if path.suffix.lower() != ".md" or path.name in {"index.md", "template.md"}:
            continue
        feature = _parse_feature(path)
        if feature.number in seen:
            raise RegistryError(f"duplicate feature ID: {feature.feature_id}")
        seen.add(feature.number)
        features.append(feature)
    return sorted(features, key=lambda feature: feature.number)


def render_index(features: list[Feature]) -> str:
    lines = ["# Feature Registry", "", "> Generated file. Do not edit manually.", ""]
    if not features:
        return "\n".join([*lines, "No features registered.", ""])
    lines.extend(
        [
            "| ID | Feature | Status | Specification |",
            "| --- | --- | --- | --- |",
        ]
    )
    for feature in features:
        escaped_title = feature.title.replace("|", "\\|")
        lines.append(
            f"| {feature.feature_id} | {escaped_title} | {feature.status} | "
            f"[{feature.filename}]({feature.filename}) |"
        )
    return "\n".join([*lines, ""])


def _index_path(root: Path) -> Path:
    path = root / "docs" / "features" / "index.md"
    if path.is_symlink() or not path.is_file():
        raise RegistryError("docs/features/index.md is missing or unsafe")
    return path


def sync(root: Path) -> None:
    features = read_features(root)
    path = root / "docs" / "features" / "index.md"
    if path.is_symlink() or path.parent.is_symlink() or not path.parent.is_dir():
        raise RegistryError("docs/features/index.md location is missing or unsafe")
    content = render_index(features)
    try:
        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", newline="\n", dir=path.parent, prefix=".index.", delete=False
        ) as temporary:
            temporary.write(content)
            temporary_path = Path(temporary.name)
        os.replace(temporary_path, path)
    except OSError as exc:
        raise RegistryError(f"cannot rewrite index: {exc}") from exc
    finally:
        if "temporary_path" in locals() and temporary_path.exists():
            temporary_path.unlink(missing_ok=True)


def check(root: Path) -> None:
    features = read_features(root)
    expected = render_index(features)
    try:
        actual = _index_path(root).read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise RegistryError(f"cannot read index: {exc}") from exc
    if actual != expected:
        raise RegistryError(
            "feature index is out of date; run: python scripts/feature_registry.py sync"
        )


def next_id(root: Path) -> str:
    features = read_features(root)
    return _canonical_id(max((feature.number for feature in features), default=0) + 1)


def next_ready(root: Path) -> str:
    features = read_features(root)
    for feature in features:
        if feature.status == "READY":
            return feature.feature_id
    return "NO_READY_FEATURE"


def new_feature(root: Path, title: str) -> str:
    if not title.strip() or "\n" in title or "\r" in title:
        raise RegistryError("title must be a non-empty single line")
    feature_id = next_id(root)
    slug = title_slug(title.strip())
    path = root / "docs" / "features" / f"{feature_id}-{slug}.md"
    if path.exists():
        raise RegistryError(f"refusing to overwrite existing feature: {path.name}")
    template = root / "docs" / "features" / "template.md"
    if template.is_symlink() or not template.is_file():
        raise RegistryError("feature template is missing or unsafe")
    try:
        scaffold = template.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise RegistryError(f"cannot read feature template: {exc}") from exc
    placeholder = "# FNNN — Feature title"
    if not scaffold.startswith(f"{placeholder}\n\nStatus: BACKLOG\n"):
        raise RegistryError("feature template has an unsupported metadata header")
    content = scaffold.replace(placeholder, f"# {feature_id} — {title.strip()}", 1)
    try:
        with path.open("x", encoding="utf-8", newline="\n") as feature_file:
            feature_file.write(content)
    except OSError as exc:
        raise RegistryError(f"cannot create feature: {exc}") from exc
    sync(root)
    return feature_id


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("sync", "check", "next-id", "next-ready", "new"))
    parser.add_argument("title", nargs="?")
    args = parser.parse_args(argv)
    root = Path(__file__).resolve().parent.parent
    try:
        if args.command == "sync":
            sync(root)
        elif args.command == "check":
            check(root)
        elif args.command == "next-id":
            print(next_id(root))
        elif args.command == "next-ready":
            print(next_ready(root))
        elif args.command == "new":
            if args.title is None:
                raise RegistryError("new requires TITLE")
            print(new_feature(root, args.title))
    except RegistryError as exc:
        print(f"feature registry: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
