import json
import sys
from pathlib import Path

import pytest

from agentready.verification import VerificationError, record, validate


def test_optional_version_probe_timeout_does_not_invalidate_receipt(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import agentready.verification as verification

    root = repository(tmp_path)
    identity = {"python": "test", "cfn-lint": "stable-executable"}
    monkeypatch.setattr(verification, "tool_identity", lambda commands, root: identity.copy())
    assert record(root, "W001", "FEATURE", [("tests", [sys.executable, "-c", "pass"])]) == 0
    identity["version:cfn-lint"] = "cfn-lint 1.57.2"
    validate(root, "W001")
    assert record(root, "W001", "FEATURE", [("tests", [sys.executable, "-c", "pass"])]) == 0
    identity.pop("version:cfn-lint")
    validate(root, "W001")


def repository(tmp_path: Path) -> Path:
    (tmp_path / "docs/work").mkdir(parents=True)
    (tmp_path / "docs/verification.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "max_age_seconds": 86400,
                "required_stages": {"default": ["tests"], "DOCS": ["map"]},
            }
        )
    )
    (tmp_path / "docs/work/W001-example.md").write_text(
        "# W001 - Example\nType: FEATURE\nStatus: IN_PROGRESS\n## Acceptance\nWorks\n"
        "## Implementation record\nTODO\n"
    )
    (tmp_path / "source.py").write_text("x = 1\n")
    return tmp_path


def test_actual_success_and_completion_prose_compatibility(tmp_path: Path) -> None:
    root = repository(tmp_path)
    assert record(root, "W001", "FEATURE", [("tests", [sys.executable, "-c", "pass"])]) == 0
    work = root / "docs/work/W001-example.md"
    work.write_text(work.read_text().replace("IN_PROGRESS", "DONE").replace("TODO", "COMPLETE"))
    validate(root, "W001")
    (root / "source.py").write_text("x = 2\n")
    with pytest.raises(VerificationError, match="stale"):
        validate(root, "W001")
    validate(root, "W001", fresh=False)


def test_missing_failed_and_missing_stage_evidence(tmp_path: Path) -> None:
    root = repository(tmp_path)
    with pytest.raises(VerificationError):
        validate(root, "W001")
    assert (
        record(root, "W001", "FEATURE", [("tests", [sys.executable, "-c", "raise SystemExit(1)"])])
        == 1
    )
    with pytest.raises(VerificationError, match="failed"):
        validate(root, "W001")
    assert record(root, "W001", "FEATURE", [("unrelated", [sys.executable, "-c", "pass"])]) == 1


def test_expired_changed_contract_and_resumed_work(tmp_path: Path) -> None:
    root = repository(tmp_path)
    command = [("tests", [sys.executable, "-c", "pass"])]
    assert record(root, "W001", "FEATURE", command) == 0
    path = root / "docs/verification/W001.json"
    evidence = json.loads(path.read_text())
    evidence["created_at"] = 0
    path.write_text(json.dumps(evidence))
    with pytest.raises(VerificationError, match="expired"):
        validate(root, "W001")
    assert record(root, "W001", "FEATURE", command) == 0
    work = root / "docs/work/W001-example.md"
    work.write_text(work.read_text().replace("Works", "New criteria"))
    with pytest.raises(VerificationError, match="stale"):
        validate(root, "W001")
    assert record(root, "W001", "FEATURE", command) == 0
    validate(root, "W001")


def test_unsafe_path_and_incomplete_receipt(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = repository(tmp_path)
    with pytest.raises(VerificationError, match="ID"):
        record(root, "../../outside", "FEATURE", [])
    assert record(root, "W001", "FEATURE", [("tests", [sys.executable, "-c", "pass"])]) == 0
    path = root / "docs/verification/W001.json"
    path.write_text("{}")
    with pytest.raises(VerificationError):
        validate(root, "W001")
    monkeypatch.setattr(Path, "is_junction", lambda path: path == root / "docs/verification")
    with pytest.raises(VerificationError, match="unsafe"):
        validate(root, "W001")


def test_registry_opt_in_rejects_fabricated_prose_and_accepts_actual_receipt(
    tmp_path: Path,
) -> None:
    import subprocess

    from agentready.render.generator import generate_project

    root = tmp_path / "project"
    generate_project(root)
    (root / "docs/verification.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "max_age_seconds": 86400,
                "required_stages": {"default": ["tests"]},
            }
        ),
        encoding="utf-8",
    )

    def registry(*arguments: str) -> int:
        return subprocess.run(
            [sys.executable, "scripts/work_registry.py", *arguments],
            cwd=root,
            capture_output=True,
            check=False,
        ).returncode

    assert registry("new", "--type", "FEATURE", "Evidence") == 0
    work = root / "docs/work/W001-evidence.md"
    text = work.read_text(encoding="utf-8")
    assert "Verification evidence: REQUIRED" in text
    text = text.replace("Status: BACKLOG", "Status: IN_PROGRESS")
    text = text.replace("NOT_EVALUATED", "NOT_REQUIRED")
    text = text.replace("### Result\nNOT_STARTED", "### Result\nCOMPLETE")
    text = text.replace("<None yet>", "Implemented").replace("<None>", "None")
    text = text.replace("Summary: <Concise summary>", "Summary: Implemented")
    work.write_text(text, encoding="utf-8")
    assert registry("sync") == 0
    assert registry("transition", "W001", "DONE") == 1
    assert record(root, "W001", "FEATURE", [("tests", [sys.executable, "-c", "pass"])]) == 0
    assert registry("transition", "W001", "DONE") == 0
    (root / "README.md").write_text("Later unrelated development", encoding="utf-8")
    assert registry("check") == 0


def test_changed_inputs_work_type_and_competing_receipt_writer(tmp_path: Path) -> None:
    root = repository(tmp_path)
    command = [("tests", [sys.executable, "-c", "pass"])]
    assert record(root, "W001", "FEATURE", command) == 0
    with pytest.raises(VerificationError, match="type mismatch"):
        validate(root, "W001", kind="DOCS")
    with pytest.raises(VerificationError, match="matching type"):
        record(root, "W001", "DOCS", command)
    lock = root / "docs/verification/W001.json.lock"
    lock.write_text("other writer", encoding="utf-8")
    with pytest.raises(ValueError, match="update in progress"):
        record(root, "W001", "FEATURE", command)
    lock.unlink()
    changed = [("tests", [sys.executable, "-c", "open('source.py','w').write('changed')"])]
    assert record(root, "W001", "FEATURE", changed) == 1
    with pytest.raises(VerificationError, match="inputs changed"):
        validate(root, "W001")
    assert not list((root / "docs/verification").glob("*.lock"))


def test_explicit_sync_refreshes_thin_skill_views(tmp_path: Path) -> None:
    import subprocess

    from agentready.render.generator import generate_project
    from agentready.skill_qa import claude_view

    root = tmp_path / "project"
    generate_project(root)
    canonical = root / ".agents/skills/feature-builder/SKILL.md"
    text = canonical.read_text(encoding="utf-8").replace(
        "description: ", "description: Project-specific "
    )
    canonical.write_text(text, encoding="utf-8")
    result = subprocess.run(
        [sys.executable, "scripts/project.py", "sync"],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert (root / ".claude/skills/feature-builder/SKILL.md").read_text(
        encoding="utf-8"
    ) == claude_view(text, "feature-builder")
