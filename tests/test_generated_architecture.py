from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from agentready.render.generator import generate_project


def run_script(project: Path, script: str, *arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, f"scripts/{script}.py", *arguments],
        cwd=project,
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.mark.parametrize("profile", ("minimal", "application", "service"))
def test_generated_guidance_profile_parity(tmp_path: Path, profile: str) -> None:
    project = tmp_path / profile
    generate_project(project, profile=profile)

    architecture = (project / "docs/agent/standards/architecture.md").read_text()
    assert "finite timeout" in architecture
    assert "idempotent or explicitly made safe" in architecture
    assert "deterministic cleanup" in architecture
    assert "from exc" in architecture
    assert "one clear retry owner" in architecture
    if profile == "minimal":
        assert "Configuration belongs to `config.py`" not in architecture
        assert "application/__init__.py" not in architecture
    else:
        assert "validate required settings" in architecture
        assert "application/__init__.py" in architecture
        assert "other modules must not import its adapters" in architecture

    security_workflow = (project / "docs/agent/workflows/security.md").read_text()
    assert "review-only" in security_workflow and "no READY item" in security_workflow
    assert "independent final review" in security_workflow
    security_skill = (project / ".agents/skills/security-review/SKILL.md").read_text()
    assert "Review-only returns evidence without edits" in security_skill
    assert security_skill == (project / ".claude/skills/security-review/SKILL.md").read_text()
    testing_standard = (project / "docs/agent/standards/testing.md").read_text()
    assert "live network access" in testing_standard
    assert "temporary directories and files" in testing_standard
    context_standard = (project / "docs/agent/standards/context-efficiency.md").read_text()
    assert "crosses an isolated agent or context boundary" in context_standard
    generated_architecture = (project / "docs/ARCHITECTURE.md").read_text()
    if profile == "application":
        assert "service profile additionally" not in generated_architecture
        assert "console adapter" not in generated_architecture
    if profile == "service":
        assert "console adapter" in generated_architecture


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


def test_architecture_check_accepts_public_cross_module_application_import(
    tmp_path: Path,
) -> None:
    project = tmp_path / "application"
    generate_project(project, profile="application")
    package = project / "src/application/modules/catalog/application"
    package.mkdir(parents=True)
    (package / "__init__.py").write_text('__all__ = ["CatalogService"]\n')
    consumer = project / "src/application/modules/greeting/application/consumer.py"
    consumer.write_text("from application.modules.catalog.application import CatalogService\n")

    result = run_script(project, "architecture_check")

    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize(
    ("relative_path", "contents", "message"),
    (
        ("modules/greeting/domain/bad.py", "import requests\n", "domain must not depend"),
        (
            "modules/greeting/application/bad.py",
            "from application.modules.greeting.adapters.console import ConsoleAdapter\n",
            "application must not depend",
        ),
        (
            "modules/greeting/adapters/bad.py",
            "from application.modules.catalog.domain.model import Catalog\n",
            "adapters must not depend on another module's internals",
        ),
        (
            "entrypoints/bad.py",
            "from application.modules.greeting.domain.errors import InvalidGreetingName\n",
            "entrypoints must depend",
        ),
        (
            "platform/bad.py",
            "from application.modules.greeting.application import GreetingService\n",
            "platform must not depend",
        ),
        ("shared/bad.py", "import requests\n", "shared must depend only"),
        (
            "modules/greeting/application/bad.py",
            "from application.modules.catalog.application.service import CatalogService\n",
            "cross module application imports must use an exported",
        ),
        (
            "modules/greeting/application/bad.py",
            "from application.modules.catalog.application.internal import CatalogService\n",
            "cross module application imports must use an exported",
        ),
        (
            "modules/greeting/adapters/bad.py",
            "from application.modules.catalog import domain\n",
            "imports must name a layer directly",
        ),
        (
            "platform/bad.py",
            "from application import bootstrap\n",
            "platform must not depend on entrypoints or composition files",
        ),
        ("modules/greeting/domain/bad.py", "def broken(:\n", "cannot parse imports"),
    ),
)
def test_architecture_check_rejects_invalid_imports(
    tmp_path: Path, relative_path: str, contents: str, message: str
) -> None:
    project = tmp_path / "application"
    generate_project(project, profile="application")
    target = project / "src/application" / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(contents)

    result = run_script(project, "architecture_check")

    assert result.returncode == 1
    assert message in result.stderr


def test_architecture_check_rejects_unknown_package_root_directory(tmp_path: Path) -> None:
    project = tmp_path / "application"
    generate_project(project, profile="application")
    (project / "src/application/data").mkdir()

    result = run_script(project, "architecture_check")

    assert result.returncode == 1
    assert "unexpected package-root directory" in result.stderr


@pytest.mark.parametrize(
    "contents",
    (
        "import os\nVALUE = os.environ.get('MODE')\n",
        "import os as operating_system\nVALUE = operating_system.getenv('MODE')\n",
        "from os import environ as env\nVALUE = env.get('MODE')\n",
        "from os import getenv as read_env\nVALUE = read_env('MODE')\n",
    ),
)
def test_architecture_check_rejects_application_environment_reads(
    tmp_path: Path, contents: str
) -> None:
    project = tmp_path / "application"
    generate_project(project, profile="application")
    target = project / "src/application/modules/greeting/application/environment.py"
    target.write_text(contents)

    result = run_script(project, "architecture_check")

    assert result.returncode == 1
    assert "application must not read process environment directly" in result.stderr


def test_generated_codebase_map_is_consistent_and_detects_drift(tmp_path: Path) -> None:
    project = tmp_path / "service"
    generate_project(project, profile="service")
    checked = run_script(project, "generate_codebase_map", "--check")
    assert checked.returncode == 0, checked.stdout + checked.stderr
    map_text = (project / "docs/generated/CODEBASE_MAP.md").read_text()
    assert "Public application contract: `GreetingService`" in map_text
    assert "Provide the greeting use case to project entrypoints." in map_text
    assert "[knowledge](../modules/greeting.md)" in map_text
    assert "Public facade:" not in map_text
    assert "CLI:" not in map_text
    generated = run_script(project, "generate_codebase_map")
    assert generated.returncode == 0, generated.stdout + generated.stderr
    first_bytes = (project / "docs/generated/CODEBASE_MAP.md").read_bytes()
    generated = run_script(project, "generate_codebase_map")
    assert generated.returncode == 0, generated.stdout + generated.stderr
    assert (project / "docs/generated/CODEBASE_MAP.md").read_bytes() == first_bytes

    (project / "src/service/modules/__pycache__").mkdir()
    cached = run_script(project, "generate_codebase_map", "--check")
    assert cached.returncode == 0, cached.stdout + cached.stderr

    (project / "src/service/modules/greeting/adapters/http.py").write_text("VALUE = 1\n")
    stale = run_script(project, "generate_codebase_map", "--check")
    assert stale.returncode == 1
    assert "CODEBASE_MAP.md is stale" in stale.stdout


@pytest.mark.parametrize("profile", ("minimal", "application", "service"))
def test_generated_codebase_map_matches_profile_and_project_shape(
    tmp_path: Path, profile: str
) -> None:
    project = tmp_path / profile
    generate_project(project, profile=profile)
    map_text = (project / "docs/generated/CODEBASE_MAP.md").read_text()
    assert f"Profile: `{profile}`" in map_text
    if profile == "minimal":
        assert "No declared command entrypoints" in map_text
    else:
        assert "Module runner: `python -m " + profile + "`" in map_text
    assert "Test: `tests/test_main.py`" in map_text
    if profile == "minimal":
        assert "No capability modules found" in map_text
        assert "Public application contract" not in map_text
        assert "Adapter:" not in map_text
    else:
        layers = (
            "`domain`, `application`, `adapters`"
            if profile == "service"
            else "`domain`, `application`"
        )
        assert f"`greeting`: {layers}" in map_text
        assert "Provide the greeting use case to project entrypoints." in map_text
        assert "Public application contract: `GreetingService`" in map_text
        if profile == "application":
            assert "Adapter:" not in map_text
    if profile == "service":
        assert "Adapter: `modules.greeting.adapters.console`" in map_text


def test_generated_codebase_map_tracks_modules_entrypoints_and_test_root(tmp_path: Path) -> None:
    project = tmp_path / "service"
    generate_project(project, profile="service")
    package = project / "src/service"
    extra = package / "modules/catalog"
    (extra / "application").mkdir(parents=True)
    (extra / "adapters/mail").mkdir(parents=True)
    (extra / "application/__init__.py").write_text(
        '"""Catalog operations."""\n\n__all__ = ["CatalogService"]\n'
    )
    (extra / "adapters/mail/smtp.py").write_text('"""SMTP adapter."""\n')
    (extra / "__init__.py").write_text('"""Catalog capability."""\n')
    card_dir = project / "docs/modules"
    card_dir.mkdir(parents=True, exist_ok=True)
    (card_dir / "catalog.md").write_text(
        "# catalog\n"
        "Responsibility: Manage catalog items for customer orders.\n"
        "Public application surface: CatalogService.\n"
        "External boundaries: SMTP delivery through mail adapter.\n"
        "Tests: tests/test_catalog.py.\n"
    )
    (project / "tests/test_catalog.py").write_text("def test_catalog() -> None:\n    assert True\n")
    nested_test = project / "tests/modules/catalog/test_service.py"
    nested_test.parent.mkdir(parents=True)
    nested_test.write_text("def test_catalog_service() -> None:\n    assert True\n")
    pyproject = project / "pyproject.toml"
    pyproject.write_text(
        pyproject.read_text()
        + '\n[project.scripts]\ndemo-catalog = "service.entrypoints.cli:main"\n'
    )

    regenerated = run_script(project, "generate_codebase_map")
    assert regenerated.returncode == 0, regenerated.stdout + regenerated.stderr
    map_path = project / "docs/generated/CODEBASE_MAP.md"
    first = map_path.read_bytes()
    checked = run_script(project, "generate_codebase_map", "--check")
    assert checked.returncode == 0, checked.stdout + checked.stderr
    regenerated = run_script(project, "generate_codebase_map")
    assert regenerated.returncode == 0, regenerated.stdout + regenerated.stderr
    assert map_path.read_bytes() == first
    map_text = first.decode()
    assert "Console script `demo-catalog`: `service.entrypoints.cli:main`" in map_text
    assert (
        "`catalog`: `application`, `adapters` — Manage catalog items for customer orders."
        in map_text
    )
    assert "Adapter: `modules.catalog.adapters.mail.smtp`" in map_text
    assert "Test: `tests/test_catalog.py`" in map_text
    assert "Test: `tests/modules/catalog/test_service.py`" in map_text
    assert "Test: `tests/test_main.py`" in map_text
    assert "Test root: `tests/`" in map_text
    assert "python scripts/project.py verify" in map_text


def test_module_knowledge_inventory_and_new_module(tmp_path: Path) -> None:
    project = tmp_path / "service"
    generate_project(project, profile="service")
    created = subprocess.run(
        [
            sys.executable,
            "scripts/module_knowledge.py",
            "new",
            "catalog",
            "--responsibility",
            "Manage catalog items for customer orders.",
        ],
        cwd=project,
        capture_output=True,
        text=True,
        check=False,
    )
    assert created.returncode == 0, created.stdout + created.stderr
    assert (project / "src/service/modules/catalog/__init__.py").is_file()
    assert not (project / "src/service/modules/catalog/domain").exists()
    card = project / "docs/modules/catalog.md"
    original = card.read_text()
    assert "Responsibility: Manage catalog items for customer orders." in original
    assert (
        "[knowledge](../modules/catalog.md)"
        in (project / "docs/generated/CODEBASE_MAP.md").read_text()
    )
    assert run_script(project, "module_knowledge", "check").returncode == 0

    card.write_text(original.replace("Manage catalog items", "Organize catalog items"))
    stale = run_script(project, "generate_codebase_map", "--check")
    assert stale.returncode == 1
    assert run_script(project, "generate_codebase_map").returncode == 0
    assert "Organize catalog items" in (project / "docs/generated/CODEBASE_MAP.md").read_text()
    assert run_script(project, "generate_codebase_map", "--check").returncode == 0
    duplicate = subprocess.run(
        [
            sys.executable,
            "scripts/module_knowledge.py",
            "new",
            "catalog",
            "--responsibility",
            "Replace the existing catalog responsibility.",
        ],
        cwd=project,
        capture_output=True,
        text=True,
        check=False,
    )
    assert duplicate.returncode == 1
    assert card.read_text().startswith("# catalog\nResponsibility: Organize catalog items")


@pytest.mark.parametrize("name", ("BadName", "class", "has-dash", "_internal"))
def test_module_knowledge_rejects_unsafe_names(tmp_path: Path, name: str) -> None:
    project = tmp_path / "service"
    generate_project(project, profile="service")
    result = subprocess.run(
        [
            sys.executable,
            "scripts/module_knowledge.py",
            "new",
            name,
            "--responsibility",
            "Manage catalog items for customer orders.",
        ],
        cwd=project,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 1
    assert "safe snake_case" in result.stderr


@pytest.mark.parametrize("card_name", (None, "orphan"))
def test_generated_map_rejects_missing_or_orphan_module_cards(
    tmp_path: Path, card_name: str | None
) -> None:
    project = tmp_path / "service"
    generate_project(project, profile="service")
    if card_name is None:
        (project / "docs/modules/greeting.md").unlink()
    else:
        (project / "docs/modules/orphan.md").write_text(
            "# orphan\nResponsibility: Manage orphan records for customer orders.\n"
            "Public application surface: Not documented.\n"
            "External boundaries: Not documented.\nTests: Not documented.\n"
        )
    result = run_script(project, "generate_codebase_map", "--check")
    assert result.returncode == 1


def test_generated_map_is_deterministic_with_many_module_cards(tmp_path: Path) -> None:
    project = tmp_path / "service"
    generate_project(project, profile="service")
    modules = project / "src/service/modules"
    cards = project / "docs/modules"
    for index in range(32):
        name = f"capability_{index:02d}"
        module = modules / name
        module.mkdir()
        (module / "__init__.py").write_text("")
        (cards / f"{name}.md").write_text(
            f"# {name}\n"
            f"Responsibility: Process capability records in group {index}.\n"
            "Public application surface: Not documented.\n"
            "External boundaries: Not documented.\n"
            "Tests: Not documented.\n"
        )

    first = run_script(project, "generate_codebase_map")
    assert first.returncode == 0, first.stdout + first.stderr
    map_path = project / "docs/generated/CODEBASE_MAP.md"
    first_bytes = map_path.read_bytes()
    second = run_script(project, "generate_codebase_map")
    assert second.returncode == 0, second.stdout + second.stderr
    assert map_path.read_bytes() == first_bytes
    checked = run_script(project, "generate_codebase_map", "--check")
    assert checked.returncode == 0, checked.stdout + checked.stderr
