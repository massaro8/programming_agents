"""Catalog and optional deployment are shipped, independent, and safe by default."""

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from agentready.doctor.inspector import inspect
from agentready.render.generator import generate_project


def bash_path() -> str:
    git_bash = Path(os.environ.get("PROGRAMFILES", "C:/Program Files")) / "Git/bin/bash.exe"
    found = (
        str(git_bash) if sys.platform == "win32" and git_bash.is_file() else shutil.which("bash")
    )
    if found is None:
        pytest.fail("Bash 4+ required for offline engine qualification")
    return found


@pytest.mark.parametrize("components", [(), ("cloudformation",)])
def test_generated_catalog_engine_and_defaults(tmp_path: Path, components: tuple[str, ...]) -> None:
    root = tmp_path / "catalog-example"
    generate_project(
        root, family="python" if components else "cloudformation", components=components
    )
    base = root / "infrastructure" if components else root
    assert (base / "stacks/storage/artifacts.yaml").is_file()
    assert inspect(root).healthy
    assert "stacks/storage/artifacts.yaml -" in (base / "stacks/catalog.conf").read_text()
    assert (
        "infrastructure/stacks/storage/artifacts.yaml"
        not in (base / "stacks/catalog.conf").read_text()
    )
    assert not (base / "templates/storage.yaml").exists()
    assert (base / "deployment/environments.conf").read_text().splitlines()[-1].startswith("#")
    pipeline = (root / "bitbucket-pipelines.yml").read_text()
    assert "deploy.sh" not in pipeline
    assert "execute-change-set" not in pipeline
    for path in (root / "scripts").glob("*.sh"):
        assert b"\r" not in path.read_bytes()
    assert "eol=lf" in (root / ".gitattributes").read_text()
    for script in ("cfn_lib.sh", "deploy.sh", "validate.sh", "bootstrap.sh"):
        result = subprocess.run(
            [bash_path(), "-n", str(root / "scripts" / script)], capture_output=True, text=True
        )
        assert result.returncode == 0, result.stderr
    for arguments, expected in [(("catalog",), 0), ((), 1), (("inspect", "sandbox"), 1)]:
        result = subprocess.run(
            [bash_path(), "scripts/deploy.sh", *arguments],
            cwd=root,
            capture_output=True,
            text=True,
        )
        assert result.returncode == expected, result.stderr
    result = subprocess.run(
        [bash_path(), str(base / "tests/engine/run.sh")],
        cwd=root,
        capture_output=True,
        text=True,
        timeout=240,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "Engine offline regression tests passed" in result.stdout
