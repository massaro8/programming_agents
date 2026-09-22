import json
import os
import shutil
import subprocess
import tomllib
from pathlib import Path

import pytest

from agentready import __version__
from agentready.render.generator import GeneratorError, generate_project

PROJECT_OWNED = [
    ".github/workflows/ci.yml",
    ".gitignore",
    ".python-version",
    "README.md",
    "docs/ARCHITECTURE.md",
    "pyproject.toml",
    "src/demo_agentready/__init__.py",
    "src/demo_agentready/main.py",
    "tests/test_main.py",
]
SHARED = [
    "AGENTS.md",
    "docs/features/template.md",
    "scripts/feature_registry.py",
    "docs/agent/index.md",
    "docs/agent/standards/python.md",
    "docs/agent/standards/architecture.md",
    "docs/agent/standards/testing.md",
    "docs/agent/standards/dependencies.md",
    "docs/agent/workflows/feature.md",
    "docs/agent/workflows/bugfix.md",
    "docs/agent/workflows/refactor.md",
]
GENERATED = ["CLAUDE.md", ".agentready/manifest.toml", "docs/features/index.md"]
EXPECTED_FILES = set(PROJECT_OWNED + SHARED + GENERATED)


def test_generate_canonical_tree_and_manifest(tmp_path: Path) -> None:
    target = tmp_path / "demo_agentready"
    generate_project(target)
    assert (target / "src/demo_agentready/main.py").read_text().strip() == (
        'def greet(name: str) -> str:\n    return f"Hello, {name}!"'
    )
    manifest = (target / ".agentready/manifest.toml").read_text()
    assert 'generator = "agentready"' in manifest
    assert '"src/demo_agentready/main.py"' in manifest
    parsed = tomllib.loads(manifest)
    assert parsed == {
        "schema": 1,
        "profile": "minimal",
        "generator": "agentready",
        "generator_version": __version__,
        "ownership": {
            "project_owned": PROJECT_OWNED,
            "shared": SHARED,
            "generated": GENERATED,
        },
    }
    assert not (target / ".copier-answers.yml").exists()
    actual = {p.relative_to(target).as_posix() for p in target.rglob("*") if p.is_file()}
    assert actual == EXPECTED_FILES
    for path in actual:
        content = (target / path).read_text()
        assert "{{" not in content
        assert "{%" not in content
    rendered_test = (target / "tests/test_main.py").read_text()
    assert "from demo_agentready.main import greet" in rendered_test
    assert 'greet("AgentReady") == "Hello, AgentReady!"' in rendered_test
    assert "AGENTS.md" in (target / "CLAUDE.md").read_text()
    assert len((target / "CLAUDE.md").read_text().splitlines()) == 1

    generated_pyproject = tomllib.loads((target / "pyproject.toml").read_text())
    assert generated_pyproject["project"]["dependencies"] == []
    runtime_files = [
        target / "src/demo_agentready/__init__.py",
        target / "src/demo_agentready/main.py",
        target / "tests/test_main.py",
    ]
    for path in runtime_files:
        content = path.read_text().lower()
        assert "import agentready" not in content
        assert "from agentready" not in content


def test_manifest_schema_matches_generated_contract() -> None:
    schema = json.loads(Path("schemas/manifest.schema.json").read_text())
    assert schema["required"] == [
        "schema",
        "profile",
        "generator",
        "generator_version",
        "ownership",
    ]
    ownership = schema["properties"]["ownership"]
    assert ownership["required"] == ["project_owned", "shared", "generated"]
    assert set(ownership["properties"]) == {"project_owned", "shared", "generated"}
    assert schema["properties"]["profile"]["enum"] == ["minimal", "application", "service"]


def test_hyphen_name_maps_package(tmp_path: Path) -> None:
    target = tmp_path / "demo-agentready"
    generate_project(target)
    assert (target / "src/demo_agentready/__init__.py").exists()


def test_invalid_profile_refuses_without_creating_target(tmp_path: Path) -> None:
    target = tmp_path / "demo_agentready"
    with pytest.raises(GeneratorError, match="unsupported profile"):
        generate_project(target, profile="unknown")
    assert not target.exists()


@pytest.mark.parametrize("profile", ("minimal", "application", "service"))
def test_profiles_have_exact_profile_shape(tmp_path: Path, profile: str) -> None:
    target = tmp_path / f"demo-{profile}"
    generate_project(target, profile=profile)
    package = f"demo_{profile}"
    files = {path.relative_to(target).as_posix() for path in target.rglob("*") if path.is_file()}
    common = set(
        [
            *SHARED,
            *GENERATED,
            ".github/workflows/ci.yml",
            ".gitignore",
            ".python-version",
            "README.md",
            "docs/ARCHITECTURE.md",
            "pyproject.toml",
            f"src/{package}/__init__.py",
            f"src/{package}/main.py",
            "tests/test_main.py",
        ]
    )
    expected = common
    if profile != "minimal":
        expected |= {
            f"src/{package}/bootstrap.py",
            f"src/{package}/config.py",
            f"src/{package}/domain/__init__.py",
            f"src/{package}/domain/errors.py",
            f"src/{package}/application/__init__.py",
            f"src/{package}/application/service.py",
        }
    if profile == "service":
        expected |= {f"src/{package}/adapters/__init__.py", f"src/{package}/adapters/console.py"}
    assert files == expected
    assert tomllib.loads((target / ".agentready/manifest.toml").read_text())["profile"] == profile
    forbidden = (
        {"application", "domain", "adapters"}
        if profile == "minimal"
        else {"adapters"}
        if profile == "application"
        else set()
    )
    assert not any(path.is_dir() and path.name in forbidden for path in target.rglob("*"))


@pytest.mark.parametrize(
    "name",
    ["Bad", "1bad", ".bad", "-bad", "bad--name", "bad.", "class", "con", "nul"],
)
def test_invalid_names_refuse(tmp_path: Path, name: str) -> None:
    with pytest.raises(GeneratorError):
        generate_project(tmp_path / name)


def test_nonempty_target_refuses_and_empty_target_is_allowed(tmp_path: Path) -> None:
    empty = tmp_path / "empty"
    empty.mkdir()
    generate_project(empty)
    blocked = tmp_path / "blocked"
    blocked.mkdir()
    sentinel = blocked / "sentinel.txt"
    sentinel.write_text("keep")
    with pytest.raises(GeneratorError):
        generate_project(blocked)
    assert sentinel.read_text() == "keep"


def test_file_target_refuses_without_modifying_content(tmp_path: Path) -> None:
    file_target = tmp_path / "file_target"
    file_target.write_text("keep")
    with pytest.raises(GeneratorError):
        generate_project(file_target)
    assert file_target.read_text() == "keep"


def test_symlink_target_refuses_without_modifying_content(tmp_path: Path) -> None:
    real_target = tmp_path / "real_target"
    real_target.mkdir()
    symlink_target = tmp_path / "symlink_target"
    try:
        symlink_target.symlink_to(real_target, target_is_directory=True)
    except OSError as exc:
        pytest.skip(f"directory symlink unavailable: {exc}")
    with pytest.raises(GeneratorError):
        generate_project(symlink_target)
    assert list(real_target.iterdir()) == []


def test_absolute_target_is_independent_from_caller_cwd(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    target = tmp_path / "demo_agentready"
    caller = tmp_path / "caller"
    caller.mkdir()
    monkeypatch.chdir(caller)
    generate_project(target)
    assert (target / "src/demo_agentready/main.py").exists()
    assert not (caller / "demo_agentready").exists()


def test_installed_console_init_and_nonempty_refusal(tmp_path: Path) -> None:
    executable = shutil.which("agentready")
    if executable is None:
        pytest.fail("installed agentready executable not found on PATH")
    target = tmp_path / "demo_agentready"
    created = subprocess.run(
        [executable, "init", os.fspath(target)], capture_output=True, text=True, check=False
    )
    assert created.returncode == 0
    assert (target / "src/demo_agentready/main.py").exists()

    invalid_target = tmp_path / "invalid_profile"
    invalid = subprocess.run(
        [executable, "init", os.fspath(invalid_target), "--profile", "unknown"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert invalid.returncode == 2
    assert "invalid choice" in invalid.stderr
    assert not invalid_target.exists()

    sentinel = target / "sentinel.txt"
    sentinel.write_text("keep")
    refused = subprocess.run(
        [executable, "init", os.fspath(target)], capture_output=True, text=True, check=False
    )
    assert refused.returncode == 1
    assert "target directory must be empty" in refused.stderr
    assert sentinel.read_text() == "keep"
