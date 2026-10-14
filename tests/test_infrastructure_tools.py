"""Local bootstrap installs only missing tools; checks do not download."""

from __future__ import annotations

import hashlib
import io
import os
import subprocess
import sys
import tarfile
from pathlib import Path
from types import SimpleNamespace

import pytest

from agentready import infrastructure_tools as tools
from agentready.cli import main
from agentready.doctor.inspector import inspect
from agentready.render.generator import generate_project


def test_existing_tools_do_not_install(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(tools, "find_tool", lambda root, name: f"/owner/{name}")
    monkeypatch.setattr(tools.subprocess, "run", lambda *a, **k: pytest.fail("installation"))
    monkeypatch.setattr(tools.urllib.request, "urlopen", lambda *a, **k: pytest.fail("network"))
    tools.prepare_tools(tmp_path)


def test_missing_lint_installs_in_isolated_environment(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(tools, "find_tool", lambda root, name: None if name == "cfn-lint" else name)
    monkeypatch.setattr(tools.shutil, "which", lambda name: "/bin/uv")
    commands = []

    def run(command, **kwargs):
        commands.append(command)
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(tools.subprocess, "run", run)
    tools.prepare_tools(tmp_path)
    assert commands[0] == ["/bin/uv", "venv", str(tmp_path / ".tools/.venv")]
    assert commands[1][-1] == "cfn-lint==1.57.2"
    assert "--python" in commands[1]
    assert str(tmp_path / ".tools/.venv") in commands[1][4]


@pytest.mark.parametrize("invalid", [False, True])
def test_guard_checksum_and_safe_binary_install(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, invalid: bool
) -> None:
    binary = "cfn-guard.exe" if os.name == "nt" else "cfn-guard"
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w:gz") as archive:
        member = tarfile.TarInfo(f"../../escape/{binary}")
        member.size = 5
        archive.addfile(member, io.BytesIO(b"guard"))
        other = tarfile.TarInfo("../../unrelated")
        other.size = 3
        archive.addfile(other, io.BytesIO(b"bad"))
    data = buffer.getvalue()
    monkeypatch.setattr(tools.platform, "system", lambda: "Windows")
    monkeypatch.setattr(tools.platform, "machine", lambda: "AMD64")
    monkeypatch.setattr(
        tools,
        "ASSETS",
        {("Windows", "x86_64"): ("test", "bad" if invalid else hashlib.sha256(data).hexdigest())},
    )
    monkeypatch.setattr(tools.urllib.request, "urlopen", lambda *a, **k: io.BytesIO(data))
    if invalid:
        with pytest.raises(ValueError, match="SHA-256"):
            tools._install_guard(tmp_path)
        assert not (tmp_path / ".tools").exists()
    else:
        tools._install_guard(tmp_path)
        assert (tmp_path / ".tools/bin" / binary).read_bytes() == b"guard"
        assert not (tmp_path / "unrelated").exists()
        with pytest.raises(FileExistsError):
            tools._install_guard(tmp_path)
        assert (tmp_path / ".tools/bin" / binary).read_bytes() == b"guard"


def test_local_tool_discovery_needs_no_shell_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    directory = tmp_path / ".tools/bin"
    directory.mkdir(parents=True)
    binary = directory / ("cfn-guard.exe" if os.name == "nt" else "cfn-guard")
    binary.write_bytes(b"guard")
    binary.chmod(0o755)
    monkeypatch.setenv("PATH", "")
    found = tools.find_tool(tmp_path, "cfn-guard")
    assert found is not None and Path(found).samefile(binary)


def test_unsafe_tool_directory_rejected_before_install(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    original = Path.is_junction
    monkeypatch.setattr(Path, "is_junction", lambda p: p.name == ".tools" or original(p))
    with pytest.raises(ValueError, match="unsafe"):
        tools.prepare_tools(tmp_path)


def test_retry_old_infrastructure_project_receives_local_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    (scripts / "project.py").write_text("# owner runner\n")
    (scripts / "infrastructure_checks.py").write_text("# old generated runner\n")
    prepared = []
    monkeypatch.setattr(tools, "prepare_tools", lambda root: prepared.append(root))
    monkeypatch.setattr("agentready.bootstrap.shutil.which", lambda name: "/bin/uv")
    monkeypatch.setattr("agentready.bootstrap.inspect", lambda root: SimpleNamespace(healthy=True))
    calls = []

    def run(command, **kwargs):
        calls.append(kwargs)
        return SimpleNamespace(returncode=0, stdout="", stderr="")

    monkeypatch.setattr("agentready.bootstrap.subprocess.run", run)
    assert main(["bootstrap", str(tmp_path)]) == 0
    assert prepared == [tmp_path]
    assert str(tmp_path / ".tools/bin") in calls[0]["env"]["PATH"]
    assert (scripts / "project.py").read_text() == "# owner runner\n"


def test_installation_failure_is_actionable(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(tools, "find_tool", lambda root, name: None)
    monkeypatch.setattr(tools.shutil, "which", lambda name: "/bin/uv")
    monkeypatch.setattr(tools.subprocess, "run", lambda *a, **k: SimpleNamespace(returncode=1))
    with pytest.raises(ValueError, match="retry bootstrap"):
        tools.prepare_tools(tmp_path)


def test_doctor_accepts_preexisting_infrastructure_without_new_helper(tmp_path: Path) -> None:
    root = tmp_path / "old-infra"
    generate_project(root, family="cloudformation")
    (root / "scripts/infrastructure_tools.py").unlink()
    manifest = root / ".agentready/manifest.toml"
    manifest.write_text(
        manifest.read_text().replace('  "scripts/infrastructure_tools.py",\n', ""),
        encoding="utf-8",
    )
    result = subprocess.run(
        [sys.executable, "scripts/project.py", "sync"], cwd=root, check=False, capture_output=True
    )
    assert result.returncode == 0, result.stderr
    assert inspect(root).healthy
