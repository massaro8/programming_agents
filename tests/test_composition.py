"""Composition preserves one detachable engineering layer."""

import json
import subprocess
import sys
import tomllib

from agentready.render.generator import generate_project


def test_composed_project(tmp_path):
    root = tmp_path / "hybrid"
    generate_project(root, components=["cloudformation"])
    manifest = tomllib.loads((root / ".agentready/manifest.toml").read_text())
    assert manifest["family"] == "python"
    assert manifest["components"] == ["cloudformation"]
    assert (root / "infrastructure/stacks/storage/artifacts.yaml").exists()
    for script in ("skill_check.py", "environment_contracts.py", "generate_codebase_map.py"):
        arguments = ["--check"] if script == "generate_codebase_map.py" else []
        result = subprocess.run(
            [sys.executable, str(root / "scripts" / script), *arguments],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        assert result.returncode == 0, result.stdout + result.stderr
    assert "infrastructure/stacks/" in (root / "docs/generated/CODEBASE_MAP.md").read_text()
    assert (
        "infrastructure/infrastructure"
        not in (root / "scripts/infrastructure_checks.py").read_text()
    )

    for command in (("format", "--check", "."), ("check", ".")):
        result = subprocess.run(
            [sys.executable, "-m", "ruff", *command],
            cwd=root,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        assert result.returncode == 0, result.stdout + result.stderr

    result = subprocess.run(
        [
            sys.executable,
            str(root / "scripts/project.py"),
            "route",
            "BUGFIX",
            "--domain",
            "infrastructure",
            "--format",
            "json",
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["skill"] == "bug-investigation"
