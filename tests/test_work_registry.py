from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from agentready.detach.service import detach_project
from agentready.doctor.inspector import FindingStatus, inspect
from agentready.render.generator import generate_project


def _project(tmp_path: Path) -> Path:
    root = tmp_path / "demo_agentready"
    generate_project(root)
    return root


def _run(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(root / "scripts/feature_registry.py"), *args],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )


def test_empty_registry_check_next_id_and_next_ready(tmp_path: Path) -> None:
    root = _project(tmp_path)

    assert _run(root, "check").returncode == 0
    index = root / "docs/features/index.md"
    before = index.read_bytes()
    assert _run(root, "sync").returncode == 0
    assert index.read_bytes() == before
    assert _run(root, "next-id").stdout.strip() == "F001"
    ready = _run(root, "next-ready")
    assert ready.returncode == 0 and ready.stdout.strip() == "NO_READY_FEATURE"
    assert (root / "docs/features/index.md").read_text() == (
        "# Feature Registry\n\n> Generated file. Do not edit manually.\n\nNo features registered.\n"
    )


def test_new_lifecycle_is_deterministic_and_one_feature_at_a_time(tmp_path: Path) -> None:
    root = _project(tmp_path)

    created = _run(root, "new", "Greeting history")
    assert created.returncode == 0 and created.stdout.strip() == "F001"
    spec = root / "docs/features/F001-greeting-history.md"
    scaffold = spec.read_text(encoding="utf-8")
    template = (root / "docs/features/template.md").read_text(encoding="utf-8")
    assert scaffold == template.replace("# FNNN — Feature title", "# F001 — Greeting history", 1)
    assert "Status: BACKLOG" in scaffold
    assert _run(root, "next-ready").stdout.strip() == "NO_READY_FEATURE"

    human_spec = (
        scaffold.replace("Status: BACKLOG", "Status: READY", 1)
        .replace("What outcome should this feature provide?", "Retain generated greetings.")
        .replace("- Describe the required behavior.", "- Record and list generated greetings.")
        .replace("- [ ] Define observable completion criteria.", "- [ ] History preserves order.")
    )
    spec.write_text(human_spec, encoding="utf-8")
    assert _run(root, "sync").returncode == 0
    assert _run(root, "next-ready").stdout.strip() == "F001"
    normative_before = human_spec.split("## Product specification", 1)[1].split(
        "## Implementation record", 1
    )[0]

    second = _run(root, "new", "Another feature")
    assert second.returncode == 0 and second.stdout.strip() == "F002"
    assert "Status: BACKLOG" in (root / "docs/features/F002-another-feature.md").read_text()
    assert _run(root, "next-id").stdout.strip() == "F003"
    assert _run(root, "next-ready").stdout.strip() == "F001"
    index = root / "docs/features/index.md"
    before_sync = index.read_bytes()
    assert _run(root, "sync").returncode == 0
    assert index.read_bytes() == before_sync

    spec.write_text(human_spec.replace("Status: READY", "Status: IN_PROGRESS", 1), encoding="utf-8")
    assert _run(root, "sync").returncode == 0
    spec.write_text(
        spec.read_text(encoding="utf-8")
        .replace("Status: IN_PROGRESS", "Status: DONE", 1)
        .replace("- Implementation result: NOT_STARTED", "- Implementation result: COMPLETED")
        .replace("- Verification performed: Not run", "- Verification performed: pytest passed"),
        encoding="utf-8",
    )
    assert _run(root, "sync").returncode == 0
    assert _run(root, "next-ready").stdout.strip() == "NO_READY_FEATURE"
    assert _run(root, "check").returncode == 0
    normative_after = (
        spec.read_text(encoding="utf-8")
        .split("## Product specification", 1)[1]
        .split("## Implementation record", 1)[0]
    )
    assert normative_after == normative_before


def test_new_cannot_automatically_mark_ready(tmp_path: Path) -> None:
    root = _project(tmp_path)
    result = _run(root, "new", "Unapproved feature", "--status", "READY")
    assert result.returncode != 0
    assert not tuple((root / "docs/features").glob("F*.md"))


def test_next_id_is_max_plus_one_and_does_not_fill_gaps(tmp_path: Path) -> None:
    root = _project(tmp_path)
    assert _run(root, "new", "First").returncode == 0
    (root / "docs/features/F003-third.md").write_text(
        "# F003 — Third\n\nStatus: BACKLOG\n", encoding="utf-8"
    )
    assert _run(root, "sync").returncode == 0
    assert _run(root, "next-id").stdout.strip() == "F004"


def test_next_ready_selects_first_ready_by_numeric_id(tmp_path: Path) -> None:
    root = _project(tmp_path)
    features = root / "docs/features"
    cases = (
        ("F001-done.md", "# F001 — Done\n\nStatus: DONE\n"),
        ("F002-backlog.md", "# F002 — Backlog\n\nStatus: BACKLOG\n"),
        ("F003-ready-three.md", "# F003 — Ready Three\n\nStatus: READY\n"),
        ("F004-ready-four.md", "# F004 — Ready Four\n\nStatus: READY\n"),
    )
    for filename, content in cases:
        (features / filename).write_text(content, encoding="utf-8")
    assert _run(root, "sync").returncode == 0
    assert _run(root, "next-ready").stdout.strip() == "F003"


def test_duplicate_ids_fail_check(tmp_path: Path) -> None:
    root = _project(tmp_path)
    features = root / "docs/features"
    (features / "F001-first.md").write_text("# F001 — First\n\nStatus: BACKLOG\n", encoding="utf-8")
    (features / "F001-second.md").write_text(
        "# F001 — Second\n\nStatus: BACKLOG\n", encoding="utf-8"
    )
    result = _run(root, "check")
    assert result.returncode != 0 and "duplicate feature ID" in result.stderr
    finding = next(item for item in inspect(root).findings if item.check_id == "features.registry")
    assert finding.status is FindingStatus.FAIL


@pytest.mark.parametrize(
    "filename,content",
    [
        ("F01-title.md", "# F01 — Title\n\nStatus: BACKLOG\n"),
        ("F001-title.md", "# F001 — Title\n"),
        ("F001-title.md", "# F001 — Title\n\nStatus: UNKNOWN\n"),
        ("F001-title.md", "# F002 — Title\n\nStatus: BACKLOG\n"),
        ("F001-wrong-slug.md", "# F001 — Title\n\nStatus: BACKLOG\n"),
        ("notes.md", "# Notes\n\nNot a feature\n"),
    ],
)
def test_invalid_specs_fail_check_and_doctor(tmp_path: Path, filename: str, content: str) -> None:
    root = _project(tmp_path)
    (root / "docs/features" / filename).write_text(content, encoding="utf-8")

    result = _run(root, "check")
    assert result.returncode != 0 and result.stderr.startswith("feature registry:")
    report = inspect(root)
    finding = next(item for item in report.findings if item.check_id == "features.registry")
    assert finding.status is FindingStatus.FAIL


def test_index_drift_fails_without_rewriting_and_doctor_reports_it(tmp_path: Path) -> None:
    root = _project(tmp_path)
    index = root / "docs/features/index.md"
    original = index.read_text()
    index.write_text(original + "\n", encoding="utf-8")

    result = _run(root, "check")
    assert result.returncode != 0 and index.read_text() == original + "\n"
    finding = next(item for item in inspect(root).findings if item.check_id == "features.registry")
    assert finding.status is FindingStatus.FAIL


def test_registry_survives_detach_and_does_not_require_git(tmp_path: Path) -> None:
    root = _project(tmp_path)
    assert not (root / ".git").exists()
    assert _run(root, "new", "Detached feature").returncode == 0
    detach_project(root)

    assert not (root / ".agentready").exists()
    assert _run(root, "check").returncode == 0
    assert _run(root, "sync").returncode == 0
    assert _run(root, "next-ready").stdout.strip() == "NO_READY_FEATURE"
    assert (root / "docs/features/F001-detached-feature.md").is_file()


def test_new_rejects_multiline_title(tmp_path: Path) -> None:
    root = _project(tmp_path)
    result = _run(root, "new", "Broken\ntitle")
    assert result.returncode != 0
    assert not tuple((root / "docs/features").glob("F*.md"))


@pytest.mark.parametrize("profile", ("minimal", "application", "service"))
def test_all_profiles_receive_human_owned_feature_governance(tmp_path: Path, profile: str) -> None:
    root = tmp_path / f"demo_{profile}"
    generate_project(root, profile=profile)

    template = (root / "docs/features/template.md").read_text(encoding="utf-8")
    workflow = (root / "docs/agent/workflows/feature.md").read_text(encoding="utf-8")
    agents = (root / "AGENTS.md").read_text(encoding="utf-8")
    required_specification_headings = (
        "## Product specification (human-owned, normative)",
        "### Objective",
        "### Context",
        "### Functional requirements",
        "### Inputs and outputs",
        "### Behavior",
        "### Constraints",
        "### Non-goals",
        "### Acceptance criteria",
        "### Manual validation (if relevant)",
        "## Implementation record (agent-maintained)",
    )
    assert all(heading in template for heading in required_specification_headings)
    assert "must not be modified by an implementing agent" in template
    assert "Never modify them solely" in workflow
    assert "Do not implement a `BACKLOG` item" in workflow
    assert "project-owned normative requirements" in agents
