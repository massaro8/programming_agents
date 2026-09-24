from __future__ import annotations

import importlib.util
import shutil
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from agentready.bootstrap import BootstrapError, bootstrap_project
from agentready.cli import main
from agentready.doctor.inspector import inspect
from agentready.render.generator import generate_project


def test_bootstrap_runs_local_stages_in_order(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    project = tmp_path / "demo-app"
    generate_project(project, profile="application")
    commands: list[list[str]] = []

    def run(command: list[str], **kwargs: object) -> SimpleNamespace:
        commands.append(command)
        if command[1:3] == ["sync", "--all-groups"]:
            (project / "uv.lock").write_text("version = 1\n", encoding="utf-8")
        return SimpleNamespace(returncode=0, stdout="", stderr="")

    monkeypatch.setattr("agentready.bootstrap.shutil.which", lambda name: "/bin/uv")
    monkeypatch.setattr("agentready.bootstrap.subprocess.run", run)
    bootstrap_project(project)

    assert [command[1:] for command in commands] == [
        ["sync", "--all-groups"],
        ["run", "python", "scripts/work_registry.py", "check"],
        ["run", "python", "scripts/architecture_check.py"],
    ]


def test_bootstrap_missing_uv_preserves_generated_project(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    project = tmp_path / "demo-app"
    monkeypatch.setattr("agentready.bootstrap.shutil.which", lambda name: None)

    assert main(["init", str(project), "--profile", "application", "--bootstrap"]) == 1
    assert (project / "pyproject.toml").is_file()
    assert "uv availability" in capsys.readouterr().err


def test_bootstrap_reports_failed_stage_and_preserves_project(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    project = tmp_path / "demo-app"
    generate_project(project)
    monkeypatch.setattr("agentready.bootstrap.shutil.which", lambda name: "/bin/uv")

    def fail(command: list[str], **kwargs: object) -> SimpleNamespace:
        return SimpleNamespace(returncode=9, stdout="", stderr="sync failed")

    monkeypatch.setattr("agentready.bootstrap.subprocess.run", fail)
    with pytest.raises(BootstrapError, match=r"uv sync.*sync failed"):
        bootstrap_project(project)
    assert (project / "README.md").is_file()


def test_bootstrap_lockfile_stage_is_explicit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    project = tmp_path / "demo-app"
    generate_project(project)
    monkeypatch.setattr("agentready.bootstrap.shutil.which", lambda name: "/bin/uv")
    monkeypatch.setattr(
        "agentready.bootstrap.subprocess.run",
        lambda *args, **kwargs: SimpleNamespace(returncode=0, stdout="", stderr=""),
    )
    with pytest.raises(BootstrapError, match="lockfile"):
        bootstrap_project(project)


def test_project_local_runner_commands_are_detach_capable(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    project = tmp_path / "demo-app"
    generate_project(project)
    runner_path = project / "scripts/project.py"
    spec = importlib.util.spec_from_file_location("project_runner", runner_path)
    assert spec is not None and spec.loader is not None
    runner = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = runner
    spec.loader.exec_module(runner)
    runner.ROOT = project
    commands: list[list[str]] = []

    def run(command: list[str], **kwargs: object) -> SimpleNamespace:
        commands.append(command)
        if command[1:3] == ["sync", "--all-groups"]:
            (project / "uv.lock").write_text("version = 1\n", encoding="utf-8")
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(runner.shutil, "which", lambda name: "/bin/uv")
    monkeypatch.setattr(runner.subprocess, "run", run)
    assert runner.execute("bootstrap") == 0
    assert runner.execute("check") == 0
    assert runner.execute("verify") == 0
    assert commands[0][1:3] == ["sync", "--all-groups"]
    assert commands[-2][1:] == ["build"]
    assert commands[-1][1:] == ["run", "python", "scripts/generate_codebase_map.py", "--check"]
    assert "agentready" not in runner_path.read_text(encoding="utf-8").lower()


@pytest.mark.parametrize("profile", ("minimal", "application", "service"))
def test_opt_in_bootstrap_prepares_each_profile(tmp_path: Path, profile: str) -> None:
    uv = shutil.which("uv")
    if uv is None:
        pytest.skip("uv is not installed")
    project = tmp_path / "demo_app"

    assert main(["init", str(project), "--profile", profile, "--bootstrap"]) == 0

    assert (project / "uv.lock").is_file()
    assert inspect(project).healthy
    command = [sys.executable, "scripts/project.py", "verify"]
    result = subprocess.run(command, cwd=project, capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stdout + result.stderr
