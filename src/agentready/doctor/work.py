"""Read-only internal validation of the generated project's work registry."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path

from agentready.core.project import Project, ProjectPath

TYPES = ("FEATURE", "BUGFIX", "REFACTOR", "MAINTENANCE", "DOCS", "SECURITY")
STATUSES = ("BACKLOG", "READY", "IN_PROGRESS", "BLOCKED", "DONE")
FILENAME = re.compile(r"^W(?P<number>[0-9]{3,})-(?P<slug>[a-z0-9]+(?:-[a-z0-9]+)*)\.md$")


@dataclass(frozen=True, slots=True)
class _Work:
    number: int
    work_id: str
    title: str
    kind: str
    status: str
    filename: str
    text: str


def _slug(value: str) -> str:
    ascii_value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-zA-Z0-9]+", "-", ascii_value).strip("-").lower()


def _field(text: str, name: str) -> str | None:
    match = re.search(rf"^{re.escape(name)}: ?(.*)$", text, re.MULTILINE)
    if match:
        return match.group(1).strip()
    match = re.search(rf"^### {re.escape(name)}\s*\n([^#\n].*)$", text, re.MULTILINE)
    return match.group(1).strip() if match else None


def _section(text: str, heading: str) -> str:
    match = re.search(rf"^## {re.escape(heading)}\s*$([\s\S]*?)(?=^## |\Z)", text, re.MULTILINE)
    return match.group(1) if match else ""


def _parse(path: Path) -> _Work:
    match = FILENAME.fullmatch(path.name)
    if match is None:
        raise ValueError(f"invalid work filename: {path.name}")
    number = int(match.group("number"))
    work_id = f"W{number:03d}"
    if number <= 0 or match.group("number") != work_id[1:]:
        raise ValueError(f"noncanonical work ID: {path.name}")
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise ValueError(f"cannot read {path.name}: {exc}") from exc
    lines = text.splitlines()
    header = re.fullmatch(r"# (W[0-9]+) — (.+)", lines[0]) if lines else None
    if len(lines) < 4 or lines[1] or header is None or header.group(1) != work_id:
        raise ValueError(f"malformed work header: {path.name}")
    title = header.group(2).strip()
    if not title or _slug(title) != match.group("slug"):
        raise ValueError(f"filename/title mismatch: {path.name}")
    metadata = lines[2:4]
    if (
        len(metadata) != 2
        or not metadata[0].startswith("Type: ")
        or not metadata[1].startswith("Status: ")
    ):
        raise ValueError(f"malformed work metadata in {path.name}")
    if len(re.findall(r"^(?:Type|Status):", text, re.MULTILINE)) != 2:
        raise ValueError(f"duplicate or malformed work metadata in {path.name}")
    kind, status = metadata[0][6:], metadata[1][8:]
    if kind not in TYPES:
        raise ValueError(f"invalid work type in {path.name}")
    if status not in STATUSES:
        raise ValueError(f"invalid work status in {path.name}")
    work = _Work(number, work_id, title, kind, status, path.name, text)
    if status == "DONE":
        _validate_done(work)
    return work


def _validate_done(work: _Work) -> None:
    record = _section(work.text, "Implementation record")
    changelog = _section(work.text, "Changelog")
    impact_section = _section(work.text, "Documentation impact")
    for name in (
        "Result",
        "Files changed",
        "Dependencies added/changed",
        "Verification performed",
        "Design decisions",
        "Deviations or blockers",
        "Follow-up candidates",
        "AgentReady observations",
    ):
        value = _field(record, name)
        if not value or value in {"NOT_STARTED", "BLOCKED", "TODO"} or value.startswith("<"):
            raise ValueError(
                f"DONE item {work.work_id} has incomplete implementation record: {name}"
            )
    if _field(record, "Result") != "COMPLETE":
        raise ValueError(f"DONE item {work.work_id} result must be COMPLETE")
    if work.kind == "BUGFIX" and any(
        not (value := _field(record, name)) or value.startswith("<")
        for name in ("Confirmed root cause", "Regression test")
    ):
        raise ValueError(f"DONE bugfix {work.work_id} requires root cause and regression test")
    if not (summary := _field(changelog, "Summary")) or summary.startswith("<"):
        raise ValueError(f"DONE item {work.work_id} requires changelog summary")
    if _field(changelog, "User impact") not in {"NONE", "INTERNAL", "USER_VISIBLE"}:
        raise ValueError(f"DONE item {work.work_id} has invalid user impact")
    migration = _field(changelog, "Migration")
    if (
        _field(changelog, "Breaking") not in {"NO", "YES"}
        or not migration
        or migration.startswith("<")
    ):
        raise ValueError(f"DONE item {work.work_id} requires breaking and migration fields")
    for name in ("README", "ARCHITECTURE", "ADR", "OTHER"):
        value = _field(impact_section, name)
        allowed = {"UPDATED", "NOT_REQUIRED"} if name != "OTHER" else {"UPDATED", "NONE"}
        adr_path = (
            name == "ADR"
            and value is not None
            and re.fullmatch(
                r"(?:CREATED|UPDATED) docs/adr/[0-9]{4}-[a-z0-9]+(?:-[a-z0-9]+)*\.md",
                value,
            )
            is not None
        )
        if value not in allowed and not adr_path:
            raise ValueError(
                f"DONE item {work.work_id} has unevaluated documentation impact: {name}"
            )


def _render_index(items: list[_Work]) -> str:
    lines = ["# Work Registry", "", "> Generated file. Do not edit manually.", ""]
    if not items:
        return "\n".join([*lines, "No work items registered.", ""])
    lines.extend(
        ("| ID | Type | Title | Status | Specification |", "| --- | --- | --- | --- | --- |")
    )
    for item in items:
        escaped_title = item.title.replace("|", "\\|")
        lines.append(
            f"| {item.work_id} | {item.kind} | {escaped_title} | {item.status} | "
            f"[{item.filename}]({item.filename}) |"
        )
    return "\n".join([*lines, ""])


def _render_changelog(items: list[_Work]) -> str:
    lines = [
        "# Changelog",
        "",
        "> Generated from completed work items. Do not edit manually.",
        "",
        "## Completed work",
        "",
    ]
    done = [item for item in reversed(items) if item.status == "DONE"]
    if not done:
        lines.append("No completed work items.")
    for item in done:
        summary = _field(_section(item.text, "Changelog"), "Summary") or ""
        breaking = (
            "; BREAKING" if _field(_section(item.text, "Changelog"), "Breaking") == "YES" else ""
        )
        lines.append(f"- {item.work_id} [{item.kind}] **{item.title}** — {summary}{breaking}")
    return "\n".join([*lines, ""])


def validate(project: Project) -> tuple[bool, str, ProjectPath | None]:
    """Validate work metadata and exact generated indexes without executing project code."""
    directory = project.path / "docs" / "work"
    if (project.path / "docs").is_symlink() or directory.is_symlink() or not directory.is_dir():
        return False, "work registry directory is missing or unsafe", ProjectPath(Path("docs/work"))
    templates = ("feature", "bugfix", "refactor", "maintenance", "documentation", "security")
    for name in templates:
        path = directory / "templates" / f"{name}.md"
        if path.is_symlink() or not path.is_file():
            return (
                False,
                "work templates are missing or unsafe",
                ProjectPath(Path("docs/work/templates") / f"{name}.md"),
            )
    items: list[_Work] = []
    seen: set[int] = set()
    try:
        for path in sorted(directory.iterdir(), key=lambda entry: entry.name):
            if path.is_symlink():
                return (
                    False,
                    f"unsafe work entry: {path.name}",
                    ProjectPath(Path("docs/work") / path.name),
                )
            if path.is_dir() or path.name == "index.md" or path.suffix.lower() != ".md":
                continue
            item = _parse(path)
            if item.number in seen:
                return (
                    False,
                    f"duplicate work ID: {item.work_id}",
                    ProjectPath(Path("docs/work") / path.name),
                )
            seen.add(item.number)
            items.append(item)
    except (OSError, ValueError) as exc:
        name = str(exc).rsplit(": ", 1)[-1]
        candidate = ProjectPath(Path("docs/work") / name) if name.endswith(".md") else None
        return False, str(exc), candidate
    items.sort(key=lambda item: item.number)
    for relative, expected in (
        ("docs/work/index.md", _render_index(items)),
        ("docs/changelog/index.md", _render_changelog(items)),
    ):
        path = project.path / relative
        project_path = ProjectPath(Path(relative))
        if path.is_symlink() or not path.is_file():
            return False, f"{relative} is missing or unsafe", project_path
        try:
            actual = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            return False, f"cannot read {relative}: {exc}", project_path
        if actual != expected:
            return False, f"{relative} is out of date", project_path
    return True, "work registry is valid", None
