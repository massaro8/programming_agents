#!/usr/bin/env python3
"""Maintain the repository-local, standard-library work registry."""

from __future__ import annotations

import argparse
import os
import re
import sys
import tempfile
import unicodedata
from dataclasses import dataclass
from pathlib import Path

TYPES = ("FEATURE", "BUGFIX", "REFACTOR", "MAINTENANCE", "DOCS", "SECURITY")
STATUSES = ("BACKLOG", "READY", "IN_PROGRESS", "BLOCKED", "DONE")
TRANSITIONS = {
    "READY": {"IN_PROGRESS"},
    "IN_PROGRESS": {"DONE", "BLOCKED"},
    "BLOCKED": {"IN_PROGRESS"},
}
FILE = re.compile(r"^W(?P<number>[0-9]{3,})-(?P<slug>[a-z0-9]+(?:-[a-z0-9]+)*)\.md$")
HEADER = re.compile(r"^# (?P<id>W[0-9]+) — (?P<title>.+)$")


class RegistryError(ValueError):
    """Invalid work item or registry state."""


@dataclass(frozen=True)
class Work:
    number: int
    work_id: str
    title: str
    kind: str
    status: str
    filename: str
    text: str


def canonical_id(number: int) -> str:
    return f"W{number:03d}"


def slugify(title: str) -> str:
    ascii_title = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", ascii_title).strip("-").lower()
    if not slug:
        raise RegistryError("title does not produce a non-empty ASCII slug")
    return slug


def _field(text: str, name: str) -> str | None:
    match = re.search(rf"^{re.escape(name)}: ?(.*)$", text, re.MULTILINE)
    if match:
        return match.group(1).strip()
    match = re.search(rf"^### {re.escape(name)}\s*\n([^#\n].*)$", text, re.MULTILINE)
    return match.group(1).strip() if match else None


def _section(text: str, heading: str) -> str:
    match = re.search(rf"^## {re.escape(heading)}\s*$([\s\S]*?)(?=^## |\Z)", text, re.MULTILINE)
    return match.group(1) if match else ""


def parse(path: Path) -> Work:
    match = FILE.fullmatch(path.name)
    if not match:
        raise RegistryError(f"invalid work filename: {path.name}")
    number = int(match.group("number"))
    work_id = canonical_id(number)
    if number <= 0 or match.group("number") != work_id[1:]:
        raise RegistryError(f"noncanonical work ID: {path.name}")
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise RegistryError(f"cannot read {path.name}: {exc}") from exc
    lines = text.splitlines()
    header = HEADER.fullmatch(lines[0]) if lines else None
    if len(lines) < 4 or lines[1] or not header or header.group("id") != work_id:
        raise RegistryError(f"malformed work header: {path.name}")
    title = header.group("title").strip()
    if not title or slugify(title) != match.group("slug"):
        raise RegistryError(f"filename/title mismatch: {path.name}")
    metadata = lines[2:4]
    if (
        len(metadata) != 2
        or not metadata[0].startswith("Type: ")
        or not metadata[1].startswith("Status: ")
    ):
        raise RegistryError(f"malformed work metadata in {path.name}")
    kind, status = metadata[0][6:], metadata[1][8:]
    if len(re.findall(r"^(?:Type|Status):", text, re.MULTILINE)) != 2:
        raise RegistryError(f"duplicate or malformed work metadata in {path.name}")
    if kind not in TYPES:
        raise RegistryError(f"invalid work type in {path.name}")
    if status not in STATUSES:
        raise RegistryError(f"invalid work status in {path.name}")
    work = Work(number, work_id, title, kind, status, path.name, text)
    if status == "DONE":
        validate_done(work)
    return work


def validate_done(work: Work) -> None:
    record = _section(work.text, "Implementation record")
    changelog = _section(work.text, "Changelog")
    impact_section = _section(work.text, "Documentation impact")
    for label in (
        "Result",
        "Files changed",
        "Dependencies added/changed",
        "Verification performed",
        "Design decisions",
        "Deviations or blockers",
        "Follow-up candidates",
        "AgentReady observations",
    ):
        value = _field(record, label)
        if not value or value in {"NOT_STARTED", "BLOCKED", "TODO"} or value.startswith("<"):
            raise RegistryError(
                f"DONE item {work.work_id} has incomplete implementation record: {label}"
            )
    if _field(record, "Result") != "COMPLETE":
        raise RegistryError(f"DONE item {work.work_id} result must be COMPLETE")
    if work.kind == "BUGFIX" and any(
        not (value := _field(record, label)) or value.startswith("<")
        for label in ("Confirmed root cause", "Regression test")
    ):
        raise RegistryError(f"DONE bugfix {work.work_id} requires root cause and regression test")
    summary = _field(changelog, "Summary")
    impact = _field(changelog, "User impact")
    breaking = _field(changelog, "Breaking")
    migration = _field(changelog, "Migration")
    if not summary or summary in {"TODO", "<...>"} or summary.startswith("<"):
        raise RegistryError(f"DONE item {work.work_id} requires a changelog summary")
    if impact not in {"NONE", "INTERNAL", "USER_VISIBLE"}:
        raise RegistryError(f"DONE item {work.work_id} has invalid user impact")
    if breaking not in {"NO", "YES"} or not migration or migration.startswith("<"):
        raise RegistryError(f"DONE item {work.work_id} requires breaking and migration values")
    for label in ("README", "ARCHITECTURE", "ADR", "OTHER"):
        value = _field(impact_section, label)
        allowed = {"UPDATED", "NOT_REQUIRED"} if label != "OTHER" else {"UPDATED", "NONE"}
        adr_path = (
            label == "ADR"
            and value is not None
            and re.fullmatch(
                r"(?:CREATED|UPDATED) docs/adr/[0-9]{4}-[a-z0-9]+(?:-[a-z0-9]+)*\.md",
                value,
            )
            is not None
        )
        if value not in allowed and not adr_path:
            raise RegistryError(
                f"DONE item {work.work_id} has unevaluated documentation impact: {label}"
            )


def read_work(root: Path) -> list[Work]:
    directory = root / "docs" / "work"
    if (root / "docs").is_symlink() or directory.is_symlink() or not directory.is_dir():
        raise RegistryError("docs/work directory is missing or unsafe")
    works, seen = [], set()
    for path in sorted(directory.iterdir(), key=lambda p: p.name):
        if path.is_symlink():
            raise RegistryError(f"unsafe work entry: {path.name}")
        if path.is_dir() or path.name == "index.md" or path.suffix.lower() != ".md":
            continue
        item = parse(path)
        if item.number in seen:
            raise RegistryError(f"duplicate work ID: {item.work_id}")
        seen.add(item.number)
        works.append(item)
    return sorted(works, key=lambda item: item.number)


def render_index(items: list[Work]) -> str:
    lines = ["# Work Registry", "", "> Generated file. Do not edit manually.", ""]
    if not items:
        return "\n".join([*lines, "No work items registered.", ""])
    lines += ["| ID | Type | Title | Status | Specification |", "| --- | --- | --- | --- | --- |"]
    for work in items:
        escaped_title = work.title.replace("|", "\\|")
        lines.append(
            f"| {work.work_id} | {work.kind} | {escaped_title} | {work.status} | "
            f"[{work.filename}]({work.filename}) |"
        )
    return "\n".join([*lines, ""])


def render_changelog(items: list[Work]) -> str:
    lines = [
        "# Changelog",
        "",
        "> Generated from completed work items. Do not edit manually.",
        "",
        "## Completed work",
        "",
    ]
    done = [w for w in reversed(items) if w.status == "DONE"]
    if not done:
        lines.append("No completed work items.")
    for w in done:
        summary = _field(_section(w.text, "Changelog"), "Summary") or ""
        breaking = (
            "; BREAKING" if _field(_section(w.text, "Changelog"), "Breaking") == "YES" else ""
        )
        lines.append(f"- {w.work_id} [{w.kind}] **{w.title}** — {summary}{breaking}")
    return "\n".join([*lines, ""])


def _write(path: Path, text: str) -> None:
    if path.is_symlink() or path.parent.is_symlink() or not path.parent.is_dir():
        raise RegistryError(f"unsafe generated path: {path}")
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", newline="\n", dir=path.parent, delete=False
        ) as stream:
            stream.write(text)
            temporary_path = Path(stream.name)
        os.replace(temporary_path, path)
    except OSError as exc:
        raise RegistryError(f"cannot write {path}: {exc}") from exc
    finally:
        if temporary_path and temporary_path.exists():
            temporary_path.unlink(missing_ok=True)


def sync(root: Path) -> None:
    items = read_work(root)
    _write(root / "docs/work/index.md", render_index(items))
    _write(root / "docs/changelog/index.md", render_changelog(items))


def check(root: Path) -> None:
    items = read_work(root)
    for rel, expected in (
        ("docs/work/index.md", render_index(items)),
        ("docs/changelog/index.md", render_changelog(items)),
    ):
        path = root / rel
        if path.is_symlink() or not path.is_file() or path.read_text(encoding="utf-8") != expected:
            raise RegistryError(
                f"{rel} is missing, unsafe, or out of date; "
                "run: python scripts/work_registry.py sync"
            )


def next_id(root: Path) -> str:
    return canonical_id(max((w.number for w in read_work(root)), default=0) + 1)


def next_ready(root: Path) -> str:
    return next((w.work_id for w in read_work(root) if w.status == "READY"), "NO_READY_WORK")


def new_work(root: Path, kind: str, title: str) -> str:
    if kind not in TYPES:
        raise RegistryError(f"invalid type; choose one of: {', '.join(TYPES)}")
    if not title.strip() or "\n" in title or "\r" in title:
        raise RegistryError("title must be a non-empty single line")
    work_id, title = next_id(root), title.strip()
    path = root / "docs/work" / f"{work_id}-{slugify(title)}.md"
    if path.exists():
        raise RegistryError(f"refusing to overwrite {path.name}")
    template_name = "documentation" if kind == "DOCS" else kind.lower()
    template = root / "docs/work/templates" / f"{template_name}.md"
    if template.is_symlink() or not template.is_file():
        raise RegistryError(f"work template missing or unsafe: {template.name}")
    content = template.read_text(encoding="utf-8")
    placeholder = "# WNNN — Work title"
    if not content.startswith(f"{placeholder}\n\nType: {kind}\nStatus: BACKLOG\n"):
        raise RegistryError(f"unsupported work template header: {template.name}")
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(content.replace(placeholder, f"# {work_id} — {title}", 1))
    sync(root)
    return work_id


def transition(root: Path, work_id: str, status: str) -> None:
    items = read_work(root)
    item = next((w for w in items if w.work_id == work_id), None)
    if item is None:
        raise RegistryError(f"unknown work ID: {work_id}")
    if status not in TRANSITIONS.get(item.status, set()):
        raise RegistryError(f"illegal transition: {item.status} -> {status}")
    path = root / "docs/work" / item.filename
    text = re.sub(r"^Status: [A-Z_]+$", f"Status: {status}", item.text, count=1, flags=re.MULTILINE)
    candidate = Work(item.number, item.work_id, item.title, item.kind, status, item.filename, text)
    if status == "DONE":
        validate_done(candidate)
    path.write_text(text, encoding="utf-8", newline="\n")
    sync(root)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for command in ("sync", "check", "next-id", "next-ready"):
        sub.add_parser(command)
    listing = sub.add_parser("list")
    listing.add_argument("--status", choices=STATUSES)
    listing.add_argument("--type", choices=TYPES)
    create = sub.add_parser("new")
    create.add_argument("--type", required=True, choices=TYPES)
    create.add_argument("title")
    change = sub.add_parser("transition")
    change.add_argument("work_id")
    change.add_argument("status", choices=STATUSES)
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
            print(new_work(root, args.type, args.title))
        elif args.command == "transition":
            transition(root, args.work_id, args.status)
        elif args.command == "list":
            for w in read_work(root):
                if (not args.status or w.status == args.status) and (
                    not args.type or w.kind == args.type
                ):
                    print(f"{w.work_id} [{w.kind}] {w.status} {w.title}")
    except (RegistryError, OSError, UnicodeError) as exc:
        print(f"work registry: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
