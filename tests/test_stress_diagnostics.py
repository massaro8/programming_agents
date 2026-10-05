from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from agentready.render.generator import generate_project


def project(tmp_path: Path) -> Path:
    root = tmp_path / "service"
    generate_project(root, profile="service")
    return root


def run(root: Path, script: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(root / f"scripts/{script}.py"), *args],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )


def test_module_card_structure_diagnostics(tmp_path: Path) -> None:
    root = project(tmp_path)
    card = root / "docs/modules/greeting.md"
    original = card.read_text(encoding="utf-8")
    lines = original.splitlines()
    surface = next(
        index for index, line in enumerate(lines) if line.startswith("Public application surface:")
    )
    boundary = next(
        index for index, line in enumerate(lines) if line.startswith("External boundaries:")
    )
    lines[surface], lines[boundary] = lines[boundary], lines[surface]
    card.write_text("\n".join(lines) + "\n", encoding="utf-8")
    result = run(root, "module_knowledge", "check")
    assert result.returncode == 1
    assert "field order" in result.stderr

    card.write_text(original.replace("Tests: tests/test_main.py.\n", ""), encoding="utf-8")
    result = run(root, "module_knowledge", "check")
    assert result.returncode == 1 and "missing fields: Tests" in result.stderr

    card.write_text(
        original.replace(
            "Public application surface: GreetingService.\n",
            "Public application surface: GreetingService.\nPublic application surface: Extra.\n",
        ),
        encoding="utf-8",
    )
    result = run(root, "module_knowledge", "check")
    assert result.returncode == 1 and "duplicate fields" in result.stderr

    card.write_text(
        original.replace("Tests: ", "Team: Engineering.\nTests: ", 1),
        encoding="utf-8",
    )
    result = run(root, "module_knowledge", "check")
    assert result.returncode == 1 and "unexpected fields: Team" in result.stderr


def test_module_card_tests_grammar_and_accepted_forms(tmp_path: Path) -> None:
    root = project(tmp_path)
    card = root / "docs/modules/greeting.md"
    original = card.read_text(encoding="utf-8")
    for value in ("/tmp/test.py", "../tests/test.py", "src/app/test.py", "tests\\test.py"):
        card.write_text(original.replace("tests/test_main.py.", value), encoding="utf-8")
        result = run(root, "module_knowledge", "check")
        assert result.returncode == 1
        assert "repository-relative paths rooted under tests/" in result.stderr
    for value in (
        "Not documented.",
        "`tests/test_main.py`.",
        "tests/test_a.py, tests/unit/test_b.py.",
        "tests/",
        "`tests/unit/`.",
    ):
        card.write_text(original.replace("tests/test_main.py.", value), encoding="utf-8")
        assert run(root, "module_knowledge", "check").returncode == 0


def test_registry_enum_and_missing_completion_diagnostics(tmp_path: Path) -> None:
    root = project(tmp_path)
    created = run(root, "work_registry", "new", "--type", "FEATURE", "Invalid metadata")
    assert created.returncode == 0
    item = root / "docs/work/W001-invalid-metadata.md"
    original = item.read_text(encoding="utf-8")
    item.write_text(original.replace("Type: FEATURE", "Type: FEATURE -- because"), encoding="utf-8")
    result = run(root, "work_registry", "check")
    assert result.returncode == 1
    assert "FEATURE, BUGFIX, REFACTOR" in result.stderr
    assert "Type is on metadata line 3" in result.stderr

    item.write_text(
        original.replace("Status: BACKLOG", "Status: BACKLOG -- waiting"), encoding="utf-8"
    )
    result = run(root, "work_registry", "check")
    assert result.returncode == 1
    assert "BACKLOG, READY, IN_PROGRESS" in result.stderr
    assert "Status is on metadata line 4" in result.stderr

    item.write_text(original.replace("Status: BACKLOG", "Status: DONE"), encoding="utf-8")
    result = run(root, "work_registry", "check")
    assert result.returncode == 1
    assert "Result: COMPLETE" in result.stderr
    assert "## Implementation record" in result.stderr

    completed = original.replace("Status: BACKLOG", "Status: DONE")
    for before, after in (
        ("README: NOT_EVALUATED", "README: NOT_REQUIRED"),
        ("ARCHITECTURE: NOT_EVALUATED", "ARCHITECTURE: NOT_REQUIRED"),
        ("ADR: NOT_EVALUATED", "ADR: NOT_REQUIRED"),
        ("### Result\nNOT_STARTED", "### Result\nCOMPLETE"),
        ("Summary: <Concise summary>", "Summary: Completed internal maintenance"),
        ("<None yet>", "Updated internal maintenance"),
        ("<None>", "None"),
        ("### Verification performed\nNone", "### Verification performed\nChecks passed"),
    ):
        completed = completed.replace(before, after)
    item.write_text(completed, encoding="utf-8")
    result = run(root, "work_registry", "list")
    assert result.returncode == 0, result.stderr

    item.write_text(
        completed.replace("README: NOT_REQUIRED", "README: NOT_REQUIRED because this is internal"),
        encoding="utf-8",
    )
    result = run(root, "work_registry", "list")
    assert result.returncode == 1
    assert "README" in result.stderr
    assert "NOT_REQUIRED or UPDATED" in result.stderr
    assert "Documentation impact" in result.stderr
    assert "NOT_REQUIRED because this is internal" in result.stderr
    assert "Keep the enum value alone" in result.stderr
    assert "Implementation record" in result.stderr and "Design decisions" in result.stderr

    item.write_text(
        completed.replace("### Design decisions\nNone", "### Design decisions\nTODO"),
        encoding="utf-8",
    )
    result = run(root, "work_registry", "list")
    assert result.returncode == 1
    assert "Design decisions" in result.stderr
    assert "Implementation record" in result.stderr
