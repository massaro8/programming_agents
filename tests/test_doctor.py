from __future__ import annotations

import os
from pathlib import Path

import pytest

from agentready.cli import main
from agentready.doctor.inspector import (
    CHECKS,
    DoctorFinding,
    DoctorReport,
    FindingStatus,
    format_report,
    inspect,
)
from agentready.render.generator import generate_project


def _project(tmp_path: Path) -> Path:
    root = tmp_path / "demo_agentready"
    generate_project(root)
    return root


def _finding(report: DoctorReport, check_id: str) -> DoctorFinding:
    assert tuple(item.check_id for item in report.findings) == CHECKS
    return next(item for item in report.findings if item.check_id == check_id)


def _assert_fails(root: Path, check_id: str) -> DoctorReport:
    report = inspect(root)
    assert not report.healthy
    assert _finding(report, check_id).status is FindingStatus.FAIL
    assert _finding(report, "detach.ready").status is FindingStatus.FAIL
    return report


def _replace(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    assert old in text
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def _snapshot(root: Path) -> tuple[tuple[str, str, bytes | str | None], ...]:
    entries: list[tuple[str, str, bytes | str | None]] = []
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            entries.append((relative, "symlink", str(path.readlink())))
        elif path.is_dir():
            entries.append((relative, "directory", None))
        else:
            entries.append((relative, "file", path.read_bytes()))
    return tuple(entries)


def test_generated_project_is_healthy_ordered_and_deterministic(tmp_path: Path) -> None:
    root = _project(tmp_path)

    first = inspect(root)
    second = inspect(root)

    assert first == second
    assert first.healthy
    assert tuple(item.check_id for item in first.findings) == CHECKS
    assert all(item.status is FindingStatus.PASS for item in first.findings)


def test_human_output_is_grouped_and_terminal(tmp_path: Path) -> None:
    output = format_report(inspect(_project(tmp_path)))

    assert output.startswith("AgentReady Doctor\n\nProject")
    assert "\nManifest\n" in output
    assert "\nAgent guidance\n" in output
    assert output.endswith("RESULT\n  HEALTHY")


def test_missing_manifest_is_unhealthy(tmp_path: Path) -> None:
    root = _project(tmp_path)
    (root / ".agentready/manifest.toml").unlink()

    report = _assert_fails(root, "manifest.present")

    assert _finding(report, "manifest.valid").status is FindingStatus.FAIL
    assert _finding(report, "ownership.unique").status is FindingStatus.FAIL


@pytest.mark.parametrize(
    "manifest_text",
    ("schema = [", None),
    ids=("malformed", "unsupported-schema"),
)
def test_invalid_or_unsupported_manifest_fails(tmp_path: Path, manifest_text: str | None) -> None:
    root = _project(tmp_path)
    manifest = root / ".agentready/manifest.toml"
    if manifest_text is None:
        _replace(manifest, "schema = 1", "schema = 999")
    else:
        manifest.write_text(manifest_text, encoding="utf-8")

    report = _assert_fails(root, "manifest.valid")

    assert "malformed or unsupported" in _finding(report, "manifest.valid").message


def test_missing_agents_fails_guidance_and_declared_artifact(tmp_path: Path) -> None:
    root = _project(tmp_path)
    (root / "AGENTS.md").unlink()

    report = _assert_fails(root, "guidance.agents")

    assert _finding(report, "ownership.artifacts").status is FindingStatus.FAIL


@pytest.mark.parametrize(
    "relative",
    ("docs/agent/workflows/feature.md", "docs/agent/standards/testing.md"),
)
def test_missing_referenced_guidance_fails_with_path(tmp_path: Path, relative: str) -> None:
    root = _project(tmp_path)
    (root / relative).unlink()

    report = _assert_fails(root, "guidance.references")

    finding = _finding(report, "guidance.references")
    assert finding.path is not None
    assert finding.path.path.as_posix() == relative
    assert _finding(report, "ownership.artifacts").status is FindingStatus.FAIL


def test_broken_claude_local_link_fails(tmp_path: Path) -> None:
    root = _project(tmp_path)
    claude = root / "CLAUDE.md"
    claude.write_text("[AGENTS](AGENTS.md)\n[missing](docs/missing.md)\n", encoding="utf-8")

    report = _assert_fails(root, "guidance.references")

    finding = _finding(report, "guidance.references")
    assert finding.path is not None
    assert finding.path.path == Path("docs/missing.md")


def test_invalid_ownership_path_fails(tmp_path: Path) -> None:
    root = _project(tmp_path)
    manifest = root / ".agentready/manifest.toml"
    _replace(manifest, "generated = [", 'generated = [\n  "../escape",')

    report = _assert_fails(root, "ownership.paths")

    assert _finding(report, "ownership.unique").status is FindingStatus.FAIL


@pytest.mark.parametrize("section", ("shared", "generated"))
def test_duplicate_or_overlapping_ownership_fails(tmp_path: Path, section: str) -> None:
    root = _project(tmp_path)
    manifest = root / ".agentready/manifest.toml"
    _replace(manifest, f"{section} = [", f'{section} = [\n  "AGENTS.md",')

    _assert_fails(root, "ownership.unique")


def test_missing_declared_artifact_reports_path(tmp_path: Path) -> None:
    root = _project(tmp_path)
    (root / "README.md").unlink()

    report = _assert_fails(root, "ownership.artifacts")

    finding = _finding(report, "ownership.artifacts")
    assert finding.path is not None
    assert finding.path.path == Path("README.md")


@pytest.mark.parametrize(
    "dependencies",
    ('["AgentReady[extra]>=1"]', '"not-a-list"', '[""]'),
    ids=("agentready-extra", "malformed-container", "malformed-requirement"),
)
def test_dependency_invariant_fails(tmp_path: Path, dependencies: str) -> None:
    root = _project(tmp_path)
    pyproject = root / "pyproject.toml"
    _replace(pyproject, "dependencies = []", f"dependencies = {dependencies}")

    _assert_fails(root, "repository.independence")


def test_doctor_does_not_mutate_tree_or_content(tmp_path: Path) -> None:
    root = _project(tmp_path)
    before = _snapshot(root)

    inspect(root)

    assert _snapshot(root) == before


def test_absolute_and_relative_targets_work_from_unrelated_cwd(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = _project(tmp_path)
    caller = tmp_path / "unrelated" / "caller"
    caller.mkdir(parents=True)
    relative = Path(os.path.relpath(root, caller))
    monkeypatch.chdir(caller)

    assert inspect(root).healthy
    assert inspect(relative).healthy


def test_cli_exit_codes_and_output(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    root = _project(tmp_path)

    assert main(["doctor", str(root)]) == 0
    assert capsys.readouterr().out.endswith("RESULT\n  HEALTHY\n")
    (root / ".agentready/manifest.toml").unlink()
    assert main(["doctor", str(root)]) == 1
    assert capsys.readouterr().out.endswith("RESULT\n  UNHEALTHY\n")


def test_symlinked_path_component_is_rejected(tmp_path: Path) -> None:
    root = _project(tmp_path)
    agent_docs = root / "docs/agent"
    original = root / "docs/agent-original"
    outside = tmp_path / "outside"
    outside.mkdir()
    agent_docs.rename(original)
    try:
        agent_docs.symlink_to(outside, target_is_directory=True)
    except OSError as exc:
        pytest.skip(f"symlink creation is unavailable: {exc}")

    report = _assert_fails(root, "ownership.artifacts")

    assert _finding(report, "guidance.references").status is FindingStatus.FAIL
