from __future__ import annotations

import json
import runpy
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from agentready.render.generator import generate_project

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def project_template(tmp_path_factory: pytest.TempPathFactory) -> Path:
    target = tmp_path_factory.mktemp("skill-template") / "generated"
    generate_project(target)
    return target


def generated_project(tmp_path: Path, project_template: Path) -> Path:
    target = tmp_path / "generated"
    shutil.copytree(project_template, target)
    return target


def load_checker(project: Path) -> dict[str, object]:
    scripts = str(project / "scripts")
    sys.path.insert(0, scripts)
    try:
        return runpy.run_path(str(project / "scripts/skill_check.py"))
    finally:
        sys.path.remove(scripts)


def test_static_routing_fixtures_match_routes_and_modes(
    tmp_path: Path, project_template: Path
) -> None:
    project = generated_project(tmp_path, project_template)
    routes = runpy.run_path(str(project / "scripts/skill_routes.py"))
    fixture = json.loads((project / "tests/fixtures/skill_routing.json").read_text())
    assert "not model-routing evaluation" in fixture["scope"]
    assert {case["work_type"] for case in fixture["scenarios"]} == set(routes["ROUTES"])
    for case in fixture["scenarios"]:
        route = routes["ROUTES"][case["work_type"]]
        assert case["expected_skill"] == route["skill"]
        assert route["workflow"] in case["required_context"]
        assert set(route["standards"]).issubset(case["required_context"])
        assert all((project / path).is_file() for path in case["required_context"])
        if case["work_type"] == "SECURITY":
            assert case["mode"] in routes["SECURITY_MODES"]
            mode = routes["SECURITY_MODES"][case["mode"]]
            assert mode["ready_item_required"] is (case["mode"] == "implementation")
            assert mode["production_edits_allowed"] is (case["mode"] == "implementation")


def test_skill_check_accepts_generated_skills(tmp_path: Path, project_template: Path) -> None:
    project = generated_project(tmp_path, project_template)
    checker = load_checker(project)
    checker["check"](project)
    result = subprocess.run(
        [sys.executable, str(project / "scripts/skill_check.py")],
        cwd=project,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "skill contracts and routes are valid" in result.stdout


@pytest.mark.parametrize(
    ("relative", "replacement", "message"),
    [
        (".agents/skills/feature-builder/SKILL.md", None, "skills differ from expected set"),
        (
            ".claude/skills/feature-builder/SKILL.md",
            (
                "---\nname: feature-builder\ndescription: Use for a different and sufficiently "
                "long purpose.\n---\n\nChanged."
            ),
            "provider skill drift",
        ),
        (
            ".agents/skills/feature-builder/SKILL.md",
            (
                "---\nname: feature-builder\ndescription: Use for implementing many scoped "
                "features.\n---\n\n"
                "Broken [link](../../../missing.md)"
            ),
            "broken skill link",
        ),
    ],
)
def test_skill_check_reports_missing_drift_and_bad_metadata(
    tmp_path: Path,
    project_template: Path,
    relative: str,
    replacement: str | None,
    message: str,
) -> None:
    project = generated_project(tmp_path, project_template)
    target = project / relative
    if replacement is None:
        target.unlink()
    else:
        target.write_text(replacement)
    checker = load_checker(project)
    with pytest.raises(checker["SkillCheckError"], match=message):
        checker["check"](project)
