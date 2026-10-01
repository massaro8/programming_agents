from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
from pathlib import Path

import pytest

from agentready.render.generator import generate_project


@pytest.mark.parametrize("profile", ("minimal", "application", "service"))
def test_package_check_uses_temporary_isolated_wheel(tmp_path: Path, profile: str) -> None:
    uv = shutil.which("uv")
    if uv is None:
        pytest.fail("uv is required for package-check qualification")
    project = tmp_path / "demo_package_check"
    generate_project(project, profile=profile)

    environment = os.environ.copy()
    environment.pop("PYTHONPATH", None)
    environment.pop("VIRTUAL_ENV", None)
    temporary = tmp_path / "package-check-temporary"
    temporary.mkdir()
    environment.update({key: os.fspath(temporary) for key in ("TMP", "TEMP", "TMPDIR")})
    prepared = subprocess.run(
        [uv, "sync", "--all-groups", "--offline"],
        cwd=project,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
        timeout=180,
    )
    assert prepared.returncode == 0, prepared.stdout + prepared.stderr
    shutil.rmtree(project / ".agentready")
    for leftover in temporary.iterdir():
        if leftover.is_file():
            leftover.unlink()

    pyproject = project / "pyproject.toml"
    lock = project / "uv.lock"
    before = (
        hashlib.sha256(pyproject.read_bytes()).digest(),
        hashlib.sha256(lock.read_bytes()).digest() if lock.exists() else None,
    )
    if profile == "minimal":
        failed = subprocess.run(
            [
                os.fspath(project / ".venv/Scripts/python.exe"),
                "scripts/package_check.py",
                "--uv",
                "package-check-missing-uv",
            ],
            cwd=project,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
            timeout=30,
        )
        assert failed.returncode == 1
        assert "failed during wheel build" in failed.stderr
    result = subprocess.run(
        [
            os.fspath(project / ".venv/Scripts/python.exe"),
            "scripts/package_check.py",
        ],
        cwd=project,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
        timeout=180,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "Package check passed." in result.stdout
    assert not (project / "dist").exists()
    assert list(temporary.iterdir()) == []
    after = (
        hashlib.sha256(pyproject.read_bytes()).digest(),
        hashlib.sha256(lock.read_bytes()).digest() if lock.exists() else None,
    )
    assert after == before
