from __future__ import annotations

import ast
import json
import os
import shutil
import subprocess
import tomllib
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
EXCLUDE = {".venv", ".pytest_cache", ".ruff_cache", ".mypy_cache", "dist", "build", "__pycache__"}
BASELINE = [
    ["uv", "sync", "--all-groups"],
    ["uv", "run", "ruff", "format", "--check", "."],
    ["uv", "run", "ruff", "check", "."],
    ["uv", "run", "mypy", "src"],
    ["uv", "run", "pytest"],
]


def run(command: list[str], cwd: Path, env: dict[str, str], timeout: int = 180) -> str:
    result = subprocess.run(
        command, cwd=cwd, env=env, capture_output=True, text=True, timeout=timeout, check=False
    )
    if result.returncode:
        pytest.fail(
            f"failed ({result.returncode}): {' '.join(command)}\n"
            f"{(result.stdout + result.stderr)[-2000:]}"
        )
    return result.stdout + result.stderr


def snapshot(root: Path) -> dict[str, tuple[str, bytes | None]]:
    result: dict[str, tuple[str, bytes | None]] = {}
    for path in root.rglob("*"):
        rel = path.relative_to(root)
        if any(part in EXCLUDE for part in rel.parts):
            continue
        kind = "dir" if path.is_dir() else "link" if path.is_symlink() else "file"
        result[rel.as_posix()] = (kind, None if kind != "file" else path.read_bytes())
    return result


def assert_frameworks_absent(uv: str, project: Path, env: dict[str, str]) -> None:
    probe = (
        "import importlib.util; "
        "assert importlib.util.find_spec('agentready') is None; "
        "assert importlib.util.find_spec('copier') is None; "
        "assert importlib.util.find_spec('jinja2') is None; "
        "from demo_agentready.main import greet; "
        "assert greet('AgentReady') == 'Hello, AgentReady!'"
    )
    run([uv, "run", "python", "-c", probe], project, env)


def declared_dependencies(config: dict[str, object]) -> list[str]:
    project = config.get("project", {})
    groups = config.get("dependency-groups", {})
    assert isinstance(project, dict) and isinstance(groups, dict)
    values = list(project.get("dependencies", []))
    optional = project.get("optional-dependencies", {})
    assert isinstance(optional, dict)
    values.extend(item for group in optional.values() for item in group)
    values.extend(item for group in groups.values() for item in group)
    assert all(isinstance(item, str) for item in values)
    return values


def test_formal_detach_no_lock_in_qualification(tmp_path: Path) -> None:
    uv = shutil.which("uv")
    if uv is None:
        pytest.fail("uv is required for formal detachment qualification")
    env = os.environ.copy()
    env.pop("PYTHONPATH", None)
    env.pop("VIRTUAL_ENV", None)
    wheel_dir = tmp_path / "wheel"
    run([uv, "build", "--wheel", "--out-dir", str(wheel_dir)], ROOT, env)
    wheel = next(wheel_dir.glob("*.whl"))
    tool_env = tmp_path / "tool-venv"
    run([uv, "venv", str(tool_env)], tmp_path, env)
    tool_python = tool_env / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    run([uv, "pip", "install", "--python", str(tool_python), str(wheel)], tmp_path, env)
    tool = tool_env / ("Scripts/agentready.exe" if os.name == "nt" else "bin/agentready")
    help_output = run([str(tool), "--help"], tmp_path, env)
    assert all(command in help_output for command in ("init", "doctor", "detach"))
    assert run([str(tool), "--version"], tmp_path, env).strip() == "agentready 0.1.0"
    project = tmp_path / "project" / "demo_agentready"
    project.parent.mkdir()
    run([str(tool), "init", str(project)], tmp_path, env)
    doctor = subprocess.run(
        [str(tool), "doctor", str(project), "--format", "json"],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert doctor.returncode == 0
    doctor_report = json.loads(doctor.stdout)
    assert doctor_report["schema"] == 1 and doctor_report["status"] == "healthy"
    assert doctor_report["project"] == "demo_agentready"
    assert doctor_report["checks"] and all(
        check["status"] == "pass" for check in doctor_report["checks"]
    )
    for command in BASELINE:
        run([uv, *command[1:]], project, env)
    run([uv, "build"], project, env)
    assert_frameworks_absent(uv, project, env)
    before = snapshot(project)
    guidance = {
        relative: (project / relative).read_bytes()
        for relative in (
            "AGENTS.md",
            "CLAUDE.md",
            "docs/agent/standards/testing.md",
            "docs/agent/workflows/feature.md",
            "docs/ARCHITECTURE.md",
        )
    }
    run([str(tool), "detach", str(project)], tmp_path, env)
    after = snapshot(project)
    removed = {name for name in before if name == ".agentready" or name.startswith(".agentready/")}
    assert set(after) == set(before) - removed
    assert all(after[name] == before[name] for name in after)
    assert not (project / ".agentready").exists()
    shutil.rmtree(tool_env)
    assert not tool_env.exists()
    for transient in (".venv", ".pytest_cache", ".ruff_cache", ".mypy_cache", "dist", "build"):
        candidate = project / transient
        if candidate.exists():
            shutil.rmtree(candidate)
    for command in BASELINE:
        run([uv, *command[1:]], project, env)
    run([uv, "build"], project, env)
    assert_frameworks_absent(uv, project, env)
    config = tomllib.loads((project / "pyproject.toml").read_text(encoding="utf-8"))
    assert not any("agentready" in value.lower() for value in declared_dependencies(config))
    for source in (project / "src").rglob("*.py"):
        for node in ast.walk(ast.parse(source.read_text(encoding="utf-8"))):
            if isinstance(node, ast.Import):
                assert all(
                    alias.name != "agentready" and not alias.name.startswith("agentready.")
                    for alias in node.names
                )
            elif isinstance(node, ast.ImportFrom) and node.module is not None:
                assert node.module != "agentready" and not node.module.startswith("agentready.")
    assert all(
        (project / relative).read_bytes() == content for relative, content in guidance.items()
    )
    agents = (project / "AGENTS.md").read_text(encoding="utf-8")
    assert all(
        reference in agents and (project / reference).is_file()
        for reference in (
            "docs/agent/standards/testing.md",
            "docs/agent/workflows/feature.md",
        )
    )
    assert "[AGENTS.md](AGENTS.md)" in (project / "CLAUDE.md").read_text(encoding="utf-8")
    app_wheel = next((project / "dist").glob("*.whl"))
    with zipfile.ZipFile(app_wheel) as archive:
        names = set(archive.namelist())
    assert "demo_agentready/main.py" in names
    assert not any(name.startswith(("agentready/", "copier/", "jinja2/")) for name in names)
