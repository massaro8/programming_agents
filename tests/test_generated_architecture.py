from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from agentready.render.generator import generate_project


def run_script(project: Path, script: str, *arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, f"scripts/{script}.py", *arguments],
        cwd=project,
        capture_output=True,
        text=True,
        check=False,
    )


def test_architecture_check_accepts_capability_and_rejects_root_bucket(
    tmp_path: Path,
) -> None:
    project = tmp_path / "application"
    generate_project(project, profile="application")
    package = project / "src/application"
    nested_domain = package / "modules/model_catalog/domain/subpackage"
    nested_domain.mkdir(parents=True)
    (nested_domain / "catalog.py").write_text("from pathlib import Path\n\nVALUE = Path('.')\n")
    (nested_domain.parent / "models.py").write_text("VALUE = 1\n")
    result = run_script(project, "architecture_check")
    assert result.returncode == 0, result.stderr

    (package / "openrouter_client.py").write_text("VALUE = 1\n")
    (package / "services").mkdir()
    result = run_script(project, "architecture_check")
    assert result.returncode == 1
    assert "openrouter_client.py" in result.stderr
    assert "package-root implementation" in result.stderr
    assert "services/" in result.stderr


def test_architecture_check_rejects_inward_dependency_inversion(tmp_path: Path) -> None:
    project = tmp_path / "application"
    generate_project(project, profile="application")
    nested_domain = project / "src/application/modules/greeting/domain/nested"
    nested_domain.mkdir()
    domain = nested_domain / "errors.py"
    domain.write_text(
        "from application.modules.greeting.application.service import GreetingService\n"
    )
    result = run_script(project, "architecture_check")
    assert result.returncode == 1
    assert "domain must not depend on" in result.stderr


def test_architecture_check_does_not_confuse_capability_name_with_outer_layer(
    tmp_path: Path,
) -> None:
    project = tmp_path / "application"
    generate_project(project, profile="application")
    domain = project / "src/application/modules/platform/domain"
    domain.mkdir(parents=True)
    (domain / "policy.py").write_text("from application.modules.platform.domain import rules\n")

    result = run_script(project, "architecture_check")

    assert result.returncode == 0, result.stderr


def test_generated_codebase_map_is_consistent_and_detects_drift(tmp_path: Path) -> None:
    project = tmp_path / "service"
    generate_project(project, profile="service")
    checked = run_script(project, "generate_codebase_map", "--check")
    assert checked.returncode == 0, checked.stdout + checked.stderr

    (project / "src/service/modules/__pycache__").mkdir()
    cached = run_script(project, "generate_codebase_map", "--check")
    assert cached.returncode == 0, cached.stdout + cached.stderr

    (project / "src/service/modules/greeting/adapters/http.py").write_text("VALUE = 1\n")
    stale = run_script(project, "generate_codebase_map", "--check")
    assert stale.returncode == 1
    assert "CODEBASE_MAP.md is stale" in stale.stdout
