import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from agentready.render.generator import generate_project


@pytest.fixture
def infrastructure(tmp_path: Path) -> Path:
    root = tmp_path / "infra-example"
    generate_project(root, family="cloudformation")
    return root


def command(
    root: Path, *arguments: str, missing_tools: bool = False
) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    if missing_tools:
        env["PATH"] = ""
    return subprocess.run(
        [sys.executable, "scripts/project.py", *arguments],
        cwd=root,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


def test_generated_family_is_independent_and_routes_exist(infrastructure: Path) -> None:
    root = infrastructure
    assert not (root / "pyproject.toml").exists()
    assert not (root / "src").exists()
    assert command(root, "sync").returncode == 0
    assert command(root, "skill", "check").returncode == 0
    for kind in ("FEATURE", "BUGFIX", "REFACTOR", "MAINTENANCE", "DOCS", "SECURITY"):
        result = command(root, "route", kind, "--format", "json")
        assert result.returncode == 0, result.stderr
        route = json.loads(result.stdout)
        for path in [route["workflow"], *route["standards"]]:
            assert (root / path).is_file()
    adapter = (root / ".claude/skills/cloudformation-change/SKILL.md").read_text()
    assert adapter.startswith("---\n")
    assert "../../../.agents/skills/cloudformation-change/SKILL.md" in adapter
    assert "## Procedure" not in adapter
    before = (root / "docs/generated/CODEBASE_MAP.md").read_bytes()
    assert command(root, "sync").returncode == 0
    assert (root / "docs/generated/CODEBASE_MAP.md").read_bytes() == before


def test_missing_tools_fail_actionably(infrastructure: Path) -> None:
    result = command(infrastructure, "check", missing_tools=True)
    assert result.returncode == 1
    assert "Missing required tools: cfn-lint, cfn-guard" in result.stderr
    assert ".venv" in result.stderr
    assert command(infrastructure, "verify", "--work", "W999").returncode == 1


def test_documentation_verification_does_not_require_infrastructure_tools(
    infrastructure: Path,
) -> None:
    root = infrastructure
    result = command(root, "work", "new", "--type", "DOCS", "Documentation")
    assert result.returncode == 0, result.stderr
    work = root / "docs/work/W001-documentation.md"
    work.write_text(work.read_text().replace("Status: BACKLOG", "Status: IN_PROGRESS"))
    assert command(root, "sync").returncode == 0
    result = command(root, "verify", "--work", "W001", missing_tools=True)
    assert result.returncode == 0, result.stdout + result.stderr
    receipt = json.loads((root / "docs/verification/W001.json").read_text())
    assert {entry["stage"] for entry in receipt["commands"]} == {
        "work registry",
        "skills",
        "codebase map",
    }


def test_map_rejects_unsafe_ancestors_and_destination(
    infrastructure: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import runpy

    root = infrastructure
    monkeypatch.syspath_prepend(str(root / "scripts"))
    namespace = runpy.run_path(str(root / "scripts/generate_codebase_map.py"))
    original = Path.is_junction
    unsafe = root / ".agents"
    monkeypatch.setattr(Path, "is_junction", lambda path: path == unsafe or original(path))
    with pytest.raises(ValueError, match="unsafe"):
        namespace["render"](root)
    unsafe = root / "docs/generated"
    before = (unsafe / "CODEBASE_MAP.md").read_bytes()
    monkeypatch.setattr(sys, "argv", ["generate_codebase_map.py"])
    with pytest.raises(ValueError, match="unsafe"):
        namespace["main"]()
    assert (unsafe / "CODEBASE_MAP.md").read_bytes() == before


def test_fixture_inventory_cannot_silently_lose_tls_regression(infrastructure: Path) -> None:
    (infrastructure / "tests/fixtures/missing-tls-policy.yaml").unlink()
    result = subprocess.run(
        [sys.executable, "scripts/fixture_check.py"],
        cwd=infrastructure,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 1
    assert "Missing required fixtures: missing-tls-policy" in result.stdout
