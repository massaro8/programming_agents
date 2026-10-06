from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

from agentready import continuity, hooks, skill_qa
from agentready.cli import main
from agentready.core.profiles import EVOLUTION_SHARED
from agentready.detach.service import detach_project
from agentready.doctor.inspector import inspect
from agentready.local_paths import local_path
from agentready.render.generator import generate_project


@pytest.fixture(scope="module")
def seed(tmp_path_factory: pytest.TempPathFactory) -> Path:
    root = tmp_path_factory.mktemp("evolution") / "sample"
    generate_project(root)
    return root


@pytest.fixture
def repository(tmp_path: Path, seed: Path) -> Path:
    root = tmp_path / "sample"
    shutil.copytree(seed, root)
    return root


def snapshot(root: Path) -> dict[str, bytes]:
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob("*") if p.is_file()}


def item(root: Path, status: str = "IN_PROGRESS") -> Path:
    path = root / "docs/work/W001-test-work.md"
    path.write_text(f"# W001 — Test work\n\nType: FEATURE\nStatus: {status}\n", encoding="utf-8")
    return path


def state() -> dict[str, Any]:
    return {
        "objective": "Complete the scoped change",
        "files": ["src/sample/main.py"],
        "decisions": ["Keep the public API"],
        "validation": ["Focused tests passed"],
        "risks": [],
        "questions": [],
        "next_step": "Run the final checks",
    }


def test_contract_accepts_seed_and_validates_all_evals(repository: Path) -> None:
    assert skill_qa.check(repository) == []
    for path in (repository / ".agents/skills").iterdir():
        report = skill_qa.evaluate(repository, path.name)
        assert report["passed"]
        assert [case["trigger_passed"] for case in report["cases"]] == [True, True]
    before = snapshot(repository)
    assert main(["skill", "--path", str(repository), "check", "--format", "json"]) == 0
    assert snapshot(repository) == before


@pytest.mark.parametrize(
    "heading",
    ["Purpose", "Positive triggers", "Evidence of completion", "Output contract", "Exclusions"],
)
def test_missing_contract_sections_have_severity(repository: Path, heading: str) -> None:
    path = repository / ".agents/skills/feature-builder/SKILL.md"
    path.write_text(path.read_text().replace(f"## {heading}", "## Removed"))
    issue = next(v for v in skill_qa.check(repository) if "missing or empty" in v["message"])
    assert issue["severity"] == ("WARNING" if heading == "Exclusions" else "ERROR")


def test_contract_broken_reference_duplicate_and_empty_sections(repository: Path) -> None:
    path = repository / ".agents/skills/feature-builder/SKILL.md"
    path.write_text(path.read_text() + "\n[broken](missing.md)\n## Purpose\n\n")
    messages = [v["message"] for v in skill_qa.check(repository)]
    assert "broken skill reference" in messages
    assert "duplicate skill section" in messages
    path.write_text("unstructured skill")
    assert skill_qa.check(repository, "feature-builder")[0]["severity"] == "ERROR"


def test_empty_verification_and_advisory_severities(repository: Path) -> None:
    path = repository / ".agents/skills/feature-builder/SKILL.md"
    original = path.read_text()
    path.write_text(
        re.sub(r"(## Evidence of completion\n).*?(?=\n## |\Z)", r"\1\n", original, flags=re.S)
    )
    assert any(
        v["severity"] == "ERROR" and "verification" in v["message"]
        for v in skill_qa.check(repository)
    )
    path.write_text(
        original.replace("## Exclusions", "## Legacy exclusions").replace(
            "description: ", "description: " + "x" * 1025
        )
    )
    issues = skill_qa.check(repository)
    assert {v["severity"] for v in issues} == {"WARNING", "INFO"}
    report = inspect(repository)
    assert report.healthy
    message = next(v.message for v in report.findings if v.check_id == "skills.contract")
    assert "WARNING" in message and "INFO" in message


def test_legacy_manifest_and_skills_remain_accepted(repository: Path) -> None:
    manifest = repository / ".agentready/manifest.toml"
    text = manifest.read_text()
    for relative in EVOLUTION_SHARED:
        (repository / relative).unlink()
        text = text.replace(f'  "{relative}",\n', "")
    manifest.write_text(text)
    for path in (repository / ".agents/skills").glob("*/SKILL.md"):
        path.write_text(path.read_text().split("\n## Purpose", 1)[0])
    before = snapshot(repository)
    report = inspect(repository)
    assert report.healthy
    assert snapshot(repository) == before


def test_malformed_eval_criteria_fail_clearly(repository: Path) -> None:
    path = repository / ".agents/skills/feature-builder/evals/cases.json"
    data = json.loads(path.read_text())
    data["cases"][0]["criteria"] = [{}]
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError, match="criteria"):
        skill_qa.definition(repository, "feature-builder")


def test_local_file_boundary_rejects_junctions(
    repository: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    boundary = repository / "docs"
    monkeypatch.setattr(Path, "is_junction", lambda path: path == boundary)
    with pytest.raises(ValueError, match="unsafe"):
        hooks.configure(repository, "safe-shell", enabled=True)


def test_external_results_score_missing_false_and_evidenced_criteria(repository: Path) -> None:
    definition = skill_qa.definition(repository, "feature-builder")
    observations = {
        key: {"passed": True, "evidence": "tests/test_main.py: passing check"}
        for key in definition["cases"][0]["criteria"]
    }
    results = {
        "schema": 1,
        "skill": "feature-builder",
        "variant": "with-skill",
        "cases": {"positive": observations},
    }
    path = repository / "results.json"
    path.write_text(json.dumps(results))
    assert skill_qa.evaluate(repository, "feature-builder", results="results.json")["passed"]
    del observations["validation_executed"]
    path.write_text(json.dumps(results))
    assert not skill_qa.evaluate(repository, "feature-builder", results="results.json")["passed"]
    observations["validation_executed"] = {"passed": True, "evidence": ""}
    path.write_text(json.dumps(results))
    with pytest.raises(ValueError, match="evidence"):
        skill_qa.evaluate(repository, "feature-builder", results="results.json")
    with pytest.raises(ValueError, match="unknown eval case"):
        skill_qa.evaluate(repository, "feature-builder", "nonexistent")


def test_invalid_eval_is_reported_by_doctor(repository: Path) -> None:
    path = repository / ".agents/skills/feature-builder/evals/cases.json"
    path.write_text('{"schema": 99}')
    report = inspect(repository)
    assert next(v for v in report.findings if v.check_id == "skills.evals").status.value != "PASS"


def test_hooks_default_preview_roundtrip_disable_and_no_global_writes(
    repository: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fake_home = tmp_path / "home"
    fake_home.mkdir()
    sentinel = fake_home / "settings.json"
    sentinel.write_text("user settings")
    monkeypatch.setenv("HOME", str(fake_home))
    monkeypatch.setenv("USERPROFILE", str(fake_home))
    assert not (repository / hooks.CONFIG).exists()
    assert sum(v["enabled"] for v in hooks.configuration(repository)["hooks"].values()) == 0
    before = snapshot(repository)
    preview = hooks.configure(repository, "safe-shell", enabled=True, mode="block", dry_run=True)
    assert preview["hooks"]["safe-shell"]["enabled"]
    assert snapshot(repository) == before
    enabled = hooks.configure(repository, "safe-shell", enabled=True, mode="block")
    assert enabled == hooks.configuration(repository)
    assert not hooks.check_command(repository, "git reset --hard")["allowed"]
    assert not hooks.check_command(repository, "git push origin main", "feature")["allowed"]
    assert hooks.check_command(repository, "git push origin feature", "feature")["allowed"]
    hooks.configure(repository, "safe-shell", enabled=False)
    assert hooks.check_command(repository, "git reset --hard")["allowed"]
    assert sentinel.read_text() == "user settings"
    assert list(fake_home.iterdir()) == [sentinel]


@pytest.mark.parametrize(
    "command",
    [
        "rm -rf directory",
        "Remove-Item path -Recurse",
        "rd /s path",
        "git push --force",
        "git reset --hard",
    ],
)
def test_safety_modes_and_exclusions(repository: Path, command: str) -> None:
    hooks.configure(repository, "safe-shell", enabled=True, mode="warn")
    result = hooks.check_command(repository, command)
    assert result["rules"] and result["allowed"]
    hooks.configure(repository, "safe-shell", mode="block")
    assert not hooks.check_command(repository, command)["allowed"]
    hooks.configure(repository, "safe-shell", exclusions=list(hooks.RULES))
    assert hooks.check_command(repository, command)["allowed"]


def test_hooks_fail_closed_and_record_no_arguments(repository: Path) -> None:
    item(repository)
    with pytest.raises(ValueError, match="disabled"):
        hooks.record(repository, "pytest", 0, "W001")
    hooks.configure(repository, "evidence-recorder", enabled=True)
    entry = hooks.record(repository, "pytest --token=known-secret-fixture", 0, "W001")
    assert entry["command"] == "pytest"
    assert "known-secret-fixture" not in (repository / hooks.EVIDENCE).read_text()
    assert hooks.record(repository, "cmd /c missing-command", 9009, "W001")["exit_status"] == 9009
    with pytest.raises(ValueError, match="exit status"):
        hooks.record(repository, "cmd", 2**64, "W001")
    with pytest.raises(ValueError):
        hooks.configure(repository, "safe-shell", mode="unsupported")
    data = hooks.configuration(repository)
    data["hooks"]["safe-shell"]["mode"] = "unsupported"
    (repository / hooks.CONFIG).write_text(json.dumps(data))
    with pytest.raises(ValueError):
        hooks.check_command(repository, "echo hello")


def test_protected_push_recognizes_full_refs_without_matching_branch_suffixes(
    repository: Path,
) -> None:
    hooks.configure(
        repository, "safe-shell", enabled=True, mode="block", branches=["main", "release/stable"]
    )
    for target in ("refs/heads/main", "refs/heads/release/stable"):
        assert not hooks.check_command(repository, f"git push origin HEAD:{target}", "feature")[
            "allowed"
        ]
    assert hooks.check_command(
        repository, "git push origin HEAD:refs/heads/feature/main", "feature"
    )["allowed"]


def test_checkpoint_roundtrip_preview_missing_done_and_secret(repository: Path) -> None:
    with pytest.raises(ValueError, match="missing"):
        continuity.checkpoint(repository, "W001")
    path = item(repository)
    before = snapshot(repository)
    continuity.checkpoint(repository, "W001", state(), dry_run=True)
    assert snapshot(repository) == before
    continuity.checkpoint(repository, "W001", state())
    resumed = continuity.resume(repository, "W001")
    assert not resumed["stale"] and resumed["state"]["next_step"] == "Run the final checks"
    with pytest.raises(ValueError, match="already exists"):
        continuity.checkpoint(repository, "W001")
    bad = state()
    bad["decisions"] = ["token=known-secret-fixture"]
    with pytest.raises(ValueError, match="secret-like"):
        continuity.checkpoint(repository, "W001", bad, replace=True)
    assert (
        "known-secret-fixture" not in (repository / "docs/work/checkpoints/W001.json").read_text()
    )
    path.write_text(path.read_text().replace("IN_PROGRESS", "DONE"))
    assert not continuity.resume(repository, "W001")["actionable"]
    with pytest.raises(ValueError, match="DONE"):
        continuity.checkpoint(repository, "W001", replace=True)


def test_checkpoint_stale_files_and_orphans(repository: Path) -> None:
    path = item(repository)
    continuity.checkpoint(repository, "W001", state())
    source = repository / "src/sample/main.py"
    source.write_text(source.read_text() + "\n# modified\n")
    assert continuity.resume(repository, "W001")["stale"]
    source.unlink()
    assert "missing" in " ".join(continuity.resume(repository, "W001")["warnings"])
    path.unlink()
    assert continuity.inspect_checkpoints(repository)[0]["severity"] == "ERROR"


def test_checkpoint_detects_dirty_tracked_file_and_revision(repository: Path) -> None:
    item(repository)
    for command in (
        ["git", "init"],
        ["git", "add", "."],
        [
            "git",
            "-c",
            "user.name=Test",
            "-c",
            "user.email=test@example.com",
            "commit",
            "-m",
            "baseline",
        ],
    ):
        subprocess.run(command, cwd=repository, capture_output=True, check=True)
    continuity.checkpoint(repository, "W001")
    path = repository / "src/sample/main.py"
    path.write_text(path.read_text() + "\n# changed\n")
    assert "tracked files changed" in " ".join(continuity.resume(repository, "W001")["warnings"])
    subprocess.run(["git", "add", str(path)], cwd=repository, capture_output=True, check=True)
    subprocess.run(
        [
            "git",
            "-c",
            "user.name=Test",
            "-c",
            "user.email=test@example.com",
            "commit",
            "-m",
            "change",
        ],
        cwd=repository,
        capture_output=True,
        check=True,
    )
    assert "repository revision changed" in continuity.resume(repository, "W001")["warnings"]


def test_new_tools_remain_usable_after_detach(repository: Path) -> None:
    item(repository)
    hooks.configure(repository, "safe-shell", enabled=True, mode="block")
    continuity.checkpoint(repository, "W001", state())
    before = snapshot(repository)
    detach_project(repository)
    assert snapshot(repository) == {
        p: data for p, data in before.items() if not p.startswith(".agentready/")
    }
    for args in (
        ["skill", "check"],
        ["skill", "eval", "feature-builder"],
        ["hooks", "status"],
        ["resume", "W001", "--format", "json"],
    ):
        result = subprocess.run(
            [sys.executable, "scripts/project.py", *args],
            cwd=repository,
            text=True,
            capture_output=True,
            check=False,
        )
        assert result.returncode == 0, result.stdout + result.stderr


def test_duplicate_hook_configuration_fields_are_rejected(repository: Path) -> None:
    path = repository / hooks.CONFIG
    path.write_text('{"schema": 1, "schema": 1, "hooks": {}}')
    with pytest.raises(ValueError, match="duplicate"):
        hooks.configuration(repository)


def test_checkpoint_does_not_invoke_repository_local_git(
    repository: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    item(repository)
    monkeypatch.setattr(shutil, "which", lambda name: str(repository / "git.exe"))
    result = continuity.checkpoint(repository, "W001")
    assert result["revision"] is None and result["tracked_digest"] is None


@pytest.mark.parametrize(
    "relative", ["../outside", "C:/outside", "/outside", "docs/../outside", "docs\\x"]
)
def test_repository_paths_reject_escape(repository: Path, relative: str) -> None:
    with pytest.raises(ValueError):
        local_path(repository, relative)
