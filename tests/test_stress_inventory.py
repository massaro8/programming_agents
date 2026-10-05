"""Architectural knowledge coverage regressions from STRESS-FIX-001."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from agentready.core.inventory import discover
from agentready.doctor.codebase_map import validate
from agentready.doctor.inspector import FindingStatus, inspect
from agentready.render.generator import generate_project


def run_map(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "scripts/generate_codebase_map.py", *args],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )


@pytest.mark.parametrize("profile", ("minimal", "application", "service"))
def test_inventory_file_package_matrix_and_independent_coverage(
    tmp_path: Path, profile: str
) -> None:
    root = tmp_path / "example"
    generate_project(root, profile=profile)
    package = root / "src/example"
    files = (
        "platform/sqlite.py",
        "platform/storage/__init__.py",
        "platform/http/client.py",
        "shared/result.py",
        "shared/types/__init__.py",
    )
    for relative in files:
        path = package / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("VALUE = 1\n", encoding="utf-8")
    inventory = discover(root, "example")
    assert {path.name for path in inventory.platform} == {"sqlite.py", "storage", "http"}
    assert {path.name for path in inventory.shared} == {"result.py", "types"}
    assert {path.name for path in inventory.entrypoints} == (
        set() if profile == "minimal" else {"cli.py"}
    )
    assert run_map(root, "--check").returncode == 1
    assert run_map(root).returncode == 0
    assert run_map(root, "--check").returncode == 0
    destination = root / "docs/generated/CODEBASE_MAP.md"
    text = destination.read_text(encoding="utf-8")
    assert validate(root, "example", profile, text)
    assert not validate(root, "example", profile, text.replace("- Test root: `tests/`", ""))
    if profile != "minimal":
        assert not validate(
            root,
            "example",
            profile,
            text.replace("Public application contract: `GreetingService`", ""),
        )
    assert "src/example/platform/sqlite.py" in text
    assert "src/example/platform/http/client.py" not in text  # compact responsibility root
    assert "src/example/platform/http`" in text
    for path in (*inventory.platform, *inventory.shared, *inventory.entrypoints):
        omitted = text.replace(f"`{path.relative_to(root).as_posix()}`", "`omitted`")
        assert not validate(root, "example", profile, omitted)
    # Simulate a defective renderer whose incomplete output passes freshness.
    generator = root / "scripts/generate_codebase_map.py"
    source = generator.read_text(encoding="utf-8")
    source = source.replace(
        'return "\\n".join(lines)',
        "return \"\\n\".join(lines).replace('`src/example/platform/sqlite.py`', '`omitted`')",
    )
    generator.write_text(source, encoding="utf-8")
    assert run_map(root).returncode == 0
    assert run_map(root, "--check").returncode == 0
    finding = next(
        item for item in inspect(root).findings if item.check_id == "repository.codebase_map"
    )
    assert finding.status is FindingStatus.FAIL


def test_flat_and_package_sqlite_have_equivalent_responsibility(tmp_path: Path) -> None:
    for package_form in (False, True):
        root = tmp_path / ("packaged" if package_form else "flat") / "example"
        generate_project(root, profile="application")
        path = root / "src/example/platform/sqlite"
        path = path / "__init__.py" if package_form else path.with_suffix(".py")
        path.parent.mkdir(parents=True)
        path.write_text("", encoding="utf-8")
        assert [item.stem for item in discover(root, "example").platform] == ["sqlite"]
        assert run_map(root).returncode == 0
        assert run_map(root, "--check").returncode == 0
        text = (root / "docs/generated/CODEBASE_MAP.md").read_text(encoding="utf-8")
        assert validate(root, "example", "application", text)
        represented = "src/example/platform/sqlite" + ("" if package_form else ".py")
        assert represented in text
        assert not validate(root, "example", "application", text.replace(represented, "omitted"))


def test_inventory_ignores_private_helpers_and_caches(tmp_path: Path) -> None:
    for relative in ("_helper.py", "__pycache__/cached.py", ".cache/ignored.py", "http/client.py"):
        path = tmp_path / "src/example/platform" / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("", encoding="utf-8")
    assert [path.name for path in discover(tmp_path, "example").platform] == ["http"]


def test_inventory_capability_application_layer(tmp_path: Path) -> None:
    module = tmp_path / "src/example/modules/catalog"
    (module / "application").mkdir(parents=True)
    (module / "application/__init__.py").write_text("", encoding="utf-8")
    inventory = discover(tmp_path, "example")
    assert inventory.modules == (module,)
    assert inventory.module_layers == (("catalog", ("application",)),)


def test_inventory_rejects_junction_layer(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    module = tmp_path / "src/example/modules/catalog"
    module.mkdir(parents=True)
    junction = module / "application"
    monkeypatch.setattr(Path, "is_junction", lambda path: path == junction)
    with pytest.raises(ValueError, match="unsafe capability layer"):
        discover(tmp_path, "example")
