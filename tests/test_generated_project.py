from __future__ import annotations

import os
import re
import shutil
import subprocess
import tomllib
import zipfile
from pathlib import Path

import pytest

from agentready.core import ArtifactOwnership, OwnershipClass, ProjectPath

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_COMMANDS = [
    "uv sync --all-groups",
    "uv run python scripts/project.py verify",
]


def run(command: list[str], cwd: Path, env: dict[str, str], timeout: int = 180) -> str:
    result = subprocess.run(
        command, cwd=cwd, env=env, capture_output=True, text=True, timeout=timeout, check=False
    )
    if result.returncode:
        output = (result.stdout + "\n" + result.stderr).strip()[-2000:]
        pytest.fail(f"command failed ({result.returncode}): {' '.join(command)}\n{output}")
    output = result.stdout + result.stderr
    assert "No Python files found" not in output
    return output


def files(root: Path) -> dict[str, bytes]:
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob("*") if p.is_file()}


@pytest.mark.parametrize("profile", ("minimal", "application", "service"))
def test_qualify_independent_generated_project(tmp_path: Path, profile: str) -> None:
    uv = shutil.which("uv")
    if uv is None:
        pytest.fail("uv is required for generated-project qualification")
    env = os.environ.copy()
    env.pop("PYTHONPATH", None)
    env.pop("VIRTUAL_ENV", None)
    wheel_dir = tmp_path / "wheel"
    wheel_dir.mkdir()
    run([uv, "build", "--wheel", "--out-dir", str(wheel_dir)], ROOT, env)
    wheel = next(wheel_dir.glob("*.whl"))
    first, second = tmp_path / "first", tmp_path / "second"
    first.mkdir()
    second.mkdir()
    for parent in (first, second):
        run(
            [
                uv,
                "run",
                "--isolated",
                "--no-project",
                "--with",
                str(wheel),
                "agentready",
                "init",
                str(parent / "demo_agentready"),
                "--profile",
                profile,
            ],
            tmp_path,
            env,
        )
    first_project, second_project = first / "demo_agentready", second / "demo_agentready"
    first_files = files(first_project)
    assert first_files == files(second_project)
    manifest = tomllib.loads((first_project / ".agentready/manifest.toml").read_text())
    assert manifest["schema"] == 1 and manifest["profile"] == profile
    assert manifest["generator"] == "agentready" and manifest["generator_version"]
    ownership = {key: set(value) for key, value in manifest["ownership"].items()}
    assert ownership["shared"] == {
        "AGENTS.md",
        "docs/work/templates/feature.md",
        "docs/work/templates/bugfix.md",
        "docs/work/templates/refactor.md",
        "docs/work/templates/maintenance.md",
        "docs/work/templates/documentation.md",
        "docs/work/templates/security.md",
        "scripts/work_registry.py",
        "scripts/project.py",
        "docs/adr/0000-template.md",
        "docs/agent/index.md",
        "docs/agent/standards/python.md",
        "docs/agent/standards/architecture.md",
        "docs/agent/standards/module-placement.md",
        "docs/agent/standards/testing.md",
        "docs/agent/standards/dependencies.md",
        "docs/agent/standards/documentation.md",
        "docs/agent/standards/security.md",
        "docs/agent/standards/context-efficiency.md",
        "scripts/architecture_check.py",
        "scripts/generate_codebase_map.py",
        "docs/agent/workflows/feature.md",
        "docs/agent/workflows/bugfix.md",
        "docs/agent/workflows/refactor.md",
        "docs/agent/workflows/maintenance.md",
        "docs/agent/workflows/documentation.md",
        "docs/agent/workflows/security.md",
        "docs/agent/workflows/repo-explore.md",
        "docs/agent/workflows/module-placement.md",
        ".agents/skills/repo-explore/SKILL.md",
        ".agents/skills/module-placement/SKILL.md",
        ".agents/skills/feature-builder/SKILL.md",
        ".agents/skills/bug-investigation/SKILL.md",
        ".agents/skills/refactoring/SKILL.md",
        ".agents/skills/maintenance/SKILL.md",
        ".agents/skills/documentation/SKILL.md",
        ".agents/skills/security-review/SKILL.md",
        ".claude/skills/repo-explore/SKILL.md",
        ".claude/skills/module-placement/SKILL.md",
        ".claude/skills/feature-builder/SKILL.md",
        ".claude/skills/bug-investigation/SKILL.md",
        ".claude/skills/refactoring/SKILL.md",
        ".claude/skills/maintenance/SKILL.md",
        ".claude/skills/documentation/SKILL.md",
        ".claude/skills/security-review/SKILL.md",
    }
    assert ownership["generated"] == {
        "CLAUDE.md",
        ".agentready/manifest.toml",
        "docs/work/index.md",
        "docs/changelog/index.md",
        "docs/generated/CODEBASE_MAP.md",
    }
    assert profile == "service" or not any("adapters/" in path for path in first_files)
    if profile == "minimal":
        assert not any(
            "/application/" in path or "/domain/" in path or "/adapters/" in path
            for path in first_files
        )
    else:
        assert any("/modules/greeting/application/service.py" in path for path in first_files)
        assert any("/modules/greeting/domain/errors.py" in path for path in first_files)
        assert (first_project / "src/demo_agentready/__main__.py").exists()
        assert not any(
            f"src/demo_agentready/{name}/" in path
            for name in ("application", "domain", "adapters")
            for path in first_files
        )
    if profile == "service":
        assert any("/modules/greeting/adapters/console.py" in path for path in first_files)
    assert set().union(*ownership.values()) == set(first_files)
    assert sum(map(len, ownership.values())) == len(set().union(*ownership.values()))
    ownership_classes = {
        "project_owned": OwnershipClass.PROJECT_OWNED,
        "shared": OwnershipClass.SHARED,
        "generated": OwnershipClass.GENERATED,
    }
    associations = {
        ArtifactOwnership(ProjectPath(Path(path)), ownership_classes[group])
        for group, paths in ownership.items()
        for path in paths
    }
    assert len(associations) == len(first_files)
    assert not (first_project / ".copier-answers.yml").exists()
    config = tomllib.loads((first_project / "pyproject.toml").read_text())
    assert not any(
        "agentready" in str(value).lower()
        for value in config.get("project", {}).get("dependencies", [])
    )
    assert "{{" not in (first_project / "tests/test_main.py").read_text()
    assert (
        "from demo_agentready.main import greet"
        in (first_project / "tests/test_main.py").read_text()
    )
    for name in ("pyproject.toml", "src/demo_agentready/main.py", "tests/test_main.py"):
        content = (first_project / name).read_text().lower()
        assert "import agentready" not in content and "from agentready" not in content
    agents = (first_project / "AGENTS.md").read_text()
    assert len(agents) < 2_000
    assert "docs/agent/index.md" in agents and "docs/work/" in agents
    assert "context-efficiency.md" in agents
    assert (
        "task/work item -> AGENTS.md"
        in (first_project / "docs/agent/standards/context-efficiency.md").read_text()
    )
    assert "search" in (first_project / "docs/agent/standards/context-efficiency.md").read_text()
    assert (
        "whole repository"
        in (first_project / "docs/agent/standards/context-efficiency.md").read_text()
    )
    skill_names = {
        "repo-explore",
        "module-placement",
        "feature-builder",
        "bug-investigation",
        "refactoring",
        "maintenance",
        "documentation",
        "security-review",
    }
    for skill_name in skill_names:
        codex_path = Path(".agents/skills") / skill_name / "SKILL.md"
        claude_path = Path(".claude/skills") / skill_name / "SKILL.md"
        codex_skill = (first_project / codex_path).read_text()
        claude_skill = (first_project / claude_path).read_text()
        assert codex_skill == claude_skill
        assert len(codex_skill.splitlines()) < 15
        assert codex_skill.startswith("---\nname: ")
        frontmatter, body = codex_skill.split("---\n", 2)[1:]
        assert f"name: {skill_name}" in frontmatter
        assert "description:" in frontmatter
        assert "Input:" in body and "Done when" in body
        assert "docs/agent/workflows/" in body
        for target in re.findall(r"\]\(([^)]+)\)", body):
            assert (first_project / codex_path).parent.joinpath(target).resolve().is_file()
    index = (first_project / "docs/agent/index.md").read_text()
    for skill_name in skill_names:
        assert f"`{skill_name}`" in index
    for fallback in (
        "repo-explore",
        "module-placement",
        "feature",
        "bugfix",
        "refactor",
        "maintenance",
        "documentation",
        "security",
    ):
        assert f"workflows/{fallback}.md" in index
    assert (
        first_project / "CLAUDE.md"
    ).read_text().strip() == "See [AGENTS.md](AGENTS.md) for the canonical project guidance."
    ci = (first_project / ".github/workflows/ci.yml").read_text()
    assert [
        line.split("- run: ", 1)[1] for line in ci.splitlines() if "- run: " in line
    ] == EXPECTED_COMMANDS
    project_env = env.copy()
    for command in EXPECTED_COMMANDS:
        run([uv, *command.split()[1:]], first_project, project_env)
    probe = (
        "import importlib.util; "
        "assert importlib.util.find_spec('agentready') is None; "
        "assert importlib.util.find_spec('copier') is None; "
        "assert importlib.util.find_spec('jinja2') is None; "
        "from demo_agentready.main import greet; "
        "assert greet('AgentReady') == 'Hello, AgentReady!'"
    )
    run([uv, "run", "python", "-c", probe], first_project, project_env)
    run([uv, "build"], first_project, project_env)
    run(
        [uv, "run", "python", "scripts/work_registry.py", "check"],
        first_project,
        project_env,
    )
    run([uv, "run", "python", "scripts/architecture_check.py"], first_project, project_env)
    run(
        [uv, "run", "python", "scripts/generate_codebase_map.py", "--check"],
        first_project,
        project_env,
    )
    built = next((first_project / "dist").glob("*.whl"))
    with zipfile.ZipFile(built) as archive:
        names = set(archive.namelist())
    assert "demo_agentready/__init__.py" in names and "demo_agentready/main.py" in names
    assert not any(name.startswith("agentready/") for name in names)
