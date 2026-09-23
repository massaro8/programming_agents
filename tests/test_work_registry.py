from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from agentready.detach.service import detach_project
from agentready.doctor.inspector import FindingStatus, inspect
from agentready.render.generator import generate_project


def project(tmp_path: Path) -> Path:
    root = tmp_path / "sample"
    generate_project(root)
    return root


def run(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(root / "scripts/work_registry.py"), *args],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )


def test_empty_registry_and_mixed_work_lifecycle(tmp_path: Path) -> None:
    root = project(tmp_path)
    assert run(root, "check").returncode == 0
    assert run(root, "next-id").stdout.strip() == "W001"
    assert run(root, "next-ready").stdout.strip() == "NO_READY_WORK"
    assert run(root, "new", "--type", "FEATURE", "One capability").stdout.strip() == "W001"
    assert run(root, "new", "--type", "BUGFIX", "Fix a defect").stdout.strip() == "W002"
    assert (root / "docs/work/W001-one-capability.md").is_file()
    assert "Status: BACKLOG" in (root / "docs/work/W002-fix-a-defect.md").read_text()
    assert run(root, "list").stdout.splitlines() == [
        "W001 [FEATURE] BACKLOG One capability",
        "W002 [BUGFIX] BACKLOG Fix a defect",
    ]
    assert run(root, "sync").returncode == 0
    assert run(root, "check").returncode == 0
    assert "No completed work items." in (root / "docs/changelog/index.md").read_text()


@pytest.mark.parametrize(
    "kind", ("FEATURE", "BUGFIX", "REFACTOR", "MAINTENANCE", "DOCS", "SECURITY")
)
def test_all_types_have_templates(tmp_path: Path, kind: str) -> None:
    root = project(tmp_path)
    result = run(root, "new", "--type", kind, "A task")
    assert result.returncode == 0
    assert f"Type: {kind}" in (root / "docs/work/W001-a-task.md").read_text()


def test_invalid_type_and_index_drift_report(tmp_path: Path) -> None:
    root = project(tmp_path)
    assert run(root, "new", "--type", "NOPE", "Invalid").returncode != 0
    index = root / "docs/work/index.md"
    index.write_text(index.read_text() + "drift\n")
    assert run(root, "check").returncode != 0
    finding = next(f for f in inspect(root).findings if f.check_id == "work.registry")
    assert finding.status is FindingStatus.FAIL


def test_done_requires_complete_record_documentation_and_changelog(tmp_path: Path) -> None:
    root = project(tmp_path)
    assert run(root, "new", "--type", "FEATURE", "Completed work").returncode == 0
    item = root / "docs/work/W001-completed-work.md"
    text = item.read_text()
    item.write_text(text.replace("Status: BACKLOG", "Status: READY", 1))
    assert run(root, "sync").returncode == 0
    assert run(root, "transition", "W001", "IN_PROGRESS").returncode == 0
    assert run(root, "transition", "W001", "DONE").returncode != 0
    assert "Status: IN_PROGRESS" in item.read_text()

    text = item.read_text()
    text = text.replace("README: NOT_EVALUATED", "README: NOT_REQUIRED")
    text = text.replace("ARCHITECTURE: NOT_EVALUATED", "ARCHITECTURE: NOT_REQUIRED")
    text = text.replace("ADR: NOT_EVALUATED", "ADR: NOT_REQUIRED")
    text = text.replace("### Result\nNOT_STARTED", "### Result\nCOMPLETE")
    for placeholder, value in (
        ("<None yet>", "Updated feature implementation"),
        ("<None>", "None"),
    ):
        text = text.replace(placeholder, value)
    text = text.replace(
        "### Verification performed\nNone", "### Verification performed\nTargeted tests passed"
    )
    text = text.replace(
        "### Design decisions\nNone", "### Design decisions\nKept existing boundaries"
    )
    text = text.replace("Summary: <Concise summary>", "Summary: Added completed work")
    item.write_text(text)
    assert run(root, "transition", "W001", "DONE").returncode == 0
    assert run(root, "check").returncode == 0
    assert "W001 [FEATURE]" in (root / "docs/changelog/index.md").read_text()


def test_registry_survives_detach(tmp_path: Path) -> None:
    root = project(tmp_path)
    assert run(root, "new", "--type", "DOCS", "Detached documentation").returncode == 0
    detach_project(root)
    assert not (root / ".agentready").exists()
    assert run(root, "check").returncode == 0
    assert (root / "docs/work/W001-detached-documentation.md").is_file()


def test_ready_selection_filters_and_monotonic_ids_across_types(tmp_path: Path) -> None:
    root = project(tmp_path)
    for kind, title in (("BUGFIX", "First"), ("DOCS", "Second"), ("FEATURE", "Third")):
        assert run(root, "new", "--type", kind, title).returncode == 0
    first = root / "docs/work/W001-first.md"
    third = root / "docs/work/W003-third.md"
    first.write_text(first.read_text().replace("Status: BACKLOG", "Status: READY", 1))
    third.write_text(third.read_text().replace("Status: BACKLOG", "Status: READY", 1))
    assert run(root, "sync").returncode == 0
    assert run(root, "next-ready").stdout.strip() == "W001"
    assert run(root, "next-id").stdout.strip() == "W004"
    assert run(root, "list", "--status", "READY").stdout.splitlines() == [
        "W001 [BUGFIX] READY First",
        "W003 [FEATURE] READY Third",
    ]
    assert run(root, "list", "--type", "DOCS").stdout.strip() == "W002 [DOCS] BACKLOG Second"
    assert run(root, "transition", "W001", "IN_PROGRESS").returncode == 0
    assert run(root, "next-ready").stdout.strip() == "W003"
    assert run(root, "transition", "W002", "IN_PROGRESS").returncode != 0


@pytest.mark.parametrize(
    ("filename", "mutation"),
    (
        ("W001-duplicate.md", "# W001 — Duplicate\n\nType: FEATURE\nStatus: BACKLOG\n"),
        ("W002-invalid.md", "# W002 — Invalid\n\nType: UNKNOWN\nStatus: BACKLOG\n"),
        ("W002-invalid.md", "# W002 — Invalid\n\nType: FEATURE\nStatus: UNKNOWN\n"),
        ("W002-invalid.md", "# W002 — Invalid\n\nStatus: BACKLOG\nType: FEATURE\n"),
    ),
)
def test_invalid_work_metadata_fails_registry_and_doctor(
    tmp_path: Path, filename: str, mutation: str
) -> None:
    root = project(tmp_path)
    assert run(root, "new", "--type", "FEATURE", "Original").returncode == 0
    (root / "docs/work" / filename).write_text(mutation)
    assert run(root, "check").returncode != 0
    finding = next(f for f in inspect(root).findings if f.check_id == "work.registry")
    assert finding.status is FindingStatus.FAIL


@pytest.mark.parametrize("relative", ("docs/work/index.md", "docs/changelog/index.md"))
def test_both_generated_indexes_detect_drift(tmp_path: Path, relative: str) -> None:
    root = project(tmp_path)
    path = root / relative
    path.write_text(path.read_text() + "drift\n")
    assert run(root, "check").returncode != 0
    finding = next(f for f in inspect(root).findings if f.check_id == "work.registry")
    assert finding.status is FindingStatus.FAIL
    assert finding.path is not None and finding.path.path == Path(relative)


@pytest.mark.parametrize(
    ("original", "replacement"),
    (
        ("### Result\nCOMPLETE", "### Result\nNOT_STARTED"),
        ("### Verification performed\nTargeted tests passed", "### Verification performed\n<None>"),
        ("README: NOT_REQUIRED", "README: NOT_EVALUATED"),
        ("Summary: Added completed work", "Summary: "),
        ("Breaking: NO", "Breaking: "),
        ("Migration: NOT_REQUIRED", "Migration: "),
    ),
)
def test_done_missing_fields_are_rejected_without_status_change(
    tmp_path: Path, original: str, replacement: str
) -> None:
    root = project(tmp_path)
    assert run(root, "new", "--type", "FEATURE", "Completed work").returncode == 0
    item = root / "docs/work/W001-completed-work.md"
    text = item.read_text()
    text = text.replace("Status: BACKLOG", "Status: READY", 1)
    text = text.replace("README: NOT_EVALUATED", "README: NOT_REQUIRED")
    text = text.replace("ARCHITECTURE: NOT_EVALUATED", "ARCHITECTURE: NOT_REQUIRED")
    text = text.replace("ADR: NOT_EVALUATED", "ADR: NOT_REQUIRED")
    text = text.replace("### Result\nNOT_STARTED", "### Result\nCOMPLETE")
    text = text.replace("<None yet>", "Updated implementation")
    text = text.replace("<None>", "None")
    text = text.replace(
        "### Verification performed\nNone", "### Verification performed\nTargeted tests passed"
    )
    text = text.replace("Summary: <Concise summary>", "Summary: Added completed work")
    assert original in text
    item.write_text(text.replace(original, replacement, 1))
    assert run(root, "transition", "W001", "IN_PROGRESS").returncode == 0
    assert run(root, "transition", "W001", "DONE").returncode != 0
    assert "Status: IN_PROGRESS" in item.read_text()
