import shutil
import subprocess

import pytest

from agentready import __version__


@pytest.fixture
def executable() -> str:
    path = shutil.which("agentready")
    if path is None:
        pytest.fail("installed agentready executable not found on PATH")
    return path


def test_console_help(executable: str) -> None:
    result = subprocess.run([executable, "--help"], capture_output=True, text=True, check=False)

    assert result.returncode == 0
    assert "usage: agentready" in result.stdout
    assert "--version" in result.stdout


def test_console_version(executable: str) -> None:
    result = subprocess.run([executable, "--version"], capture_output=True, text=True, check=False)

    assert result.returncode == 0
    assert result.stdout.strip() == f"agentready {__version__}"
    assert result.stderr == ""


def test_console_invalid_option(executable: str) -> None:
    result = subprocess.run(
        [executable, "--definitely-invalid"], capture_output=True, text=True, check=False
    )

    assert result.returncode == 2
    assert "unrecognized arguments" in result.stderr
