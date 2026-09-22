"""Read-only validation of a generated project's feature registry."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path

from agentready.core.project import Project, ProjectPath

STATUSES = ("BACKLOG", "READY", "IN_PROGRESS", "BLOCKED", "DONE")
_FILENAME = re.compile(r"^F(?P<number>[0-9]{3,})-(?P<slug>[a-z0-9]+(?:-[a-z0-9]+)*)\.md$")
_HEADER = re.compile(r"^# (?P<id>F[0-9]+) — (?P<title>.+)$")


@dataclass(frozen=True, slots=True)
class _Feature:
    number: int
    feature_id: str
    slug: str
    title: str
    status: str
    filename: str


def _slug(title: str) -> str:
    ascii_title = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-zA-Z0-9]+", "-", ascii_title).strip("-").lower()


def _canonical_id(number: int) -> str:
    return f"F{number:03d}"


def _parse(path: Path) -> _Feature:
    match = _FILENAME.fullmatch(path.name)
    if match is None:
        raise ValueError(f"invalid feature filename: {path.name}")
    number = int(match.group("number"))
    feature_id = _canonical_id(number)
    if number <= 0 or match.group("number") != feature_id[1:]:
        raise ValueError(f"feature ID is not canonically padded: {path.name}")
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        raise ValueError(f"cannot read {path.name}: {exc}") from exc
    if len(lines) < 3 or lines[1] != "":
        raise ValueError(f"{path.name} must start with a title, blank line, and status")
    header = _HEADER.fullmatch(lines[0])
    if header is None or header.group("id") != feature_id:
        raise ValueError(f"filename/header ID mismatch: {path.name}")
    title = header.group("title").strip()
    if not title or _slug(title) != match.group("slug"):
        raise ValueError(f"filename slug does not match title: {path.name}")
    status_line = lines[2]
    status = status_line.removeprefix("Status: ")
    if status_line != f"Status: {status}" or status not in STATUSES:
        raise ValueError(f"invalid feature status in {path.name}")
    return _Feature(number, feature_id, match.group("slug"), title, status, path.name)


def _render(features: list[_Feature]) -> str:
    lines = ["# Feature Registry", "", "> Generated file. Do not edit manually.", ""]
    if not features:
        return "\n".join([*lines, "No features registered.", ""])
    lines.extend(("| ID | Feature | Status | Specification |", "| --- | --- | --- | --- |"))
    for feature in features:
        title = feature.title.replace("|", "\\|")
        lines.append(
            f"| {feature.feature_id} | {title} | {feature.status} | "
            f"[{feature.filename}]({feature.filename}) |"
        )
    return "\n".join([*lines, ""])


def validate(project: Project) -> tuple[bool, str, ProjectPath | None]:
    """Validate specs and exact index content without executing repository code."""

    docs = project.path / "docs"
    directory = project.path / "docs" / "features"
    index_pp = ProjectPath(Path("docs/features/index.md"))
    if docs.is_symlink() or not docs.is_dir() or directory.is_symlink() or not directory.is_dir():
        return (
            False,
            "feature registry directory is missing or unsafe",
            ProjectPath(Path("docs/features")),
        )
    features: list[_Feature] = []
    seen: set[int] = set()
    try:
        entries = sorted(directory.iterdir(), key=lambda item: item.name)
    except OSError as exc:
        return False, f"cannot inspect feature registry: {exc}", ProjectPath(Path("docs/features"))
    try:
        for path in entries:
            if path.is_symlink():
                return (
                    False,
                    f"unsafe feature entry: {path.name}",
                    ProjectPath(Path("docs/features") / path.name),
                )
            if (
                path.is_dir()
                or path.suffix.lower() != ".md"
                or path.name in {"index.md", "template.md"}
            ):
                continue
            feature = _parse(path)
            if feature.number in seen:
                return (
                    False,
                    f"duplicate feature ID: {feature.feature_id}",
                    ProjectPath(Path("docs/features") / path.name),
                )
            seen.add(feature.number)
            features.append(feature)
    except ValueError as exc:
        name = str(exc).rsplit(": ", 1)[-1]
        candidate = ProjectPath(Path("docs/features") / name) if name.endswith(".md") else None
        return False, str(exc), candidate
    features.sort(key=lambda feature: feature.number)
    index = directory / "index.md"
    if index.is_symlink() or not index.is_file():
        return False, "feature index is missing or unsafe", index_pp
    try:
        actual = index.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        return False, f"cannot read feature index: {exc}", index_pp
    if actual != _render(features):
        return False, "feature index is out of date", index_pp
    return True, "feature registry is valid", None
