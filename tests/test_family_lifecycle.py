"""Family selection compatibility and read-only infrastructure lifecycle."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from agentready.cli import main
from agentready.detach.service import detach_project
from agentready.doctor.inspector import inspect
from agentready.render.generator import GeneratorError, generate_project


@pytest.mark.parametrize(
    ("family", "profile"),
    [("python", "infrastructure"), ("cloudformation", "minimal"), ("cloudformation", "service")],
)
def test_incompatible_selection_writes_nothing(tmp_path: Path, family: str, profile: str) -> None:
    target = tmp_path / "example"
    with pytest.raises(GeneratorError):
        generate_project(target, profile=profile, family=family)
    assert not target.exists()
    assert main(["init", str(target), "--family", family, "--profile", profile]) == 1
    assert not target.exists()


def hashes(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in root.rglob("*")
        if path.is_file() and ".agentready" not in path.parts
    }


def test_cloudformation_doctor_readonly_and_detach(tmp_path: Path) -> None:
    root = tmp_path / "infrastructure"
    assert main(["init", str(root), "--family", "cloudformation"]) == 0
    before = hashes(root)
    report = inspect(root)
    assert report.healthy, [(item.check_id, item.message) for item in report.findings]
    assert hashes(root) == before
    detach_project(root)
    assert not (root / ".agentready").exists()
    assert hashes(root) == before


def test_cloudformation_navigation_and_adapter_drift(tmp_path: Path) -> None:
    root = tmp_path / "infrastructure"
    generate_project(root, family="cloudformation")
    (root / "templates/new.yaml").write_text("Resources: {}\n", encoding="utf-8")
    report = inspect(root)
    assert (
        next(f for f in report.findings if f.check_id == "repository.codebase_map").status.value
        != "PASS"
    )
    (root / "templates/new.yaml").unlink()
    (root / "CLAUDE.md").write_text("Read AGENTS.md\n", encoding="utf-8")
    assert not inspect(root).healthy
