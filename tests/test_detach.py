from __future__ import annotations

import ast
import os
import tomllib
from pathlib import Path

import pytest

from agentready.cli import main
from agentready.detach.service import DetachError, detach_project
from agentready.render.generator import generate_project


def _project(tmp_path: Path, name: str = "demo_agentready") -> Path:
    root = tmp_path / name
    generate_project(root)
    return root


def _snapshot(root: Path) -> tuple[tuple[str, str, bytes | str | None], ...]:
    entries: list[tuple[str, str, bytes | str | None]] = []

    def visit(directory: Path) -> None:
        with os.scandir(directory) as scanned:
            for entry in sorted(scanned, key=lambda item: item.name):
                path = Path(entry.path)
                relative = path.relative_to(root).as_posix()
                if entry.is_symlink():
                    entries.append((relative, "symlink", os.readlink(path)))
                elif entry.is_dir(follow_symlinks=False):
                    entries.append((relative, "directory", None))
                    visit(path)
                elif entry.is_file(follow_symlinks=False):
                    entries.append((relative, "file", path.read_bytes()))
                else:
                    entries.append((relative, "other", None))

    visit(root)
    return tuple(entries)


def _outside_metadata(
    snapshot: tuple[tuple[str, str, bytes | str | None], ...],
) -> tuple[tuple[str, str, bytes | str | None], ...]:
    return tuple(
        entry
        for entry in snapshot
        if entry[0] != ".agentready" and not entry[0].startswith(".agentready/")
    )


def test_detach_removes_only_metadata_and_preserves_ordinary_files(tmp_path: Path) -> None:
    root = _project(tmp_path)
    nested = root / ".agentready/cache/state.txt"
    nested.parent.mkdir()
    nested.write_text("maintenance-only", encoding="utf-8")
    before = _outside_metadata(_snapshot(root))

    detach_project(root)

    assert not (root / ".agentready").exists()
    assert _snapshot(root) == before
    for relative in (
        "AGENTS.md",
        "CLAUDE.md",
        "docs/agent/standards/testing.md",
        "docs/agent/workflows/feature.md",
        "docs/work/index.md",
        "docs/work/templates/feature.md",
        "scripts/work_registry.py",
        "docs/changelog/index.md",
        "docs/ARCHITECTURE.md",
        ".github/workflows/ci.yml",
        "pyproject.toml",
        "src/demo_agentready/main.py",
        "tests/test_main.py",
    ):
        assert (root / relative).is_file()


@pytest.mark.parametrize("corruption", ("malformed", "unsupported", "missing"))
def test_invalid_manifest_refuses_without_mutation(tmp_path: Path, corruption: str) -> None:
    root = _project(tmp_path)
    manifest = root / ".agentready/manifest.toml"
    if corruption == "malformed":
        manifest.write_text("not = [valid", encoding="utf-8")
    elif corruption == "unsupported":
        manifest.write_text(
            manifest.read_text(encoding="utf-8").replace("schema = 1", "schema = 999"),
            encoding="utf-8",
        )
    else:
        manifest.unlink()
    before = _snapshot(root)

    with pytest.raises(DetachError):
        detach_project(root)

    assert _snapshot(root) == before


def test_unrecognized_project_refuses_without_mutation(tmp_path: Path) -> None:
    root = tmp_path / "ordinary_project"
    root.mkdir()
    (root / "README.md").write_text("ordinary", encoding="utf-8")
    before = _snapshot(root)

    with pytest.raises(DetachError, match="not AgentReady-managed or is already detached"):
        detach_project(root)

    assert _snapshot(root) == before


def test_second_detach_is_deterministic_and_does_not_recreate_metadata(tmp_path: Path) -> None:
    root = _project(tmp_path)
    detach_project(root)
    detached = _snapshot(root)

    with pytest.raises(DetachError, match="not AgentReady-managed or is already detached"):
        detach_project(root)

    assert _snapshot(root) == detached
    assert not (root / ".agentready").exists()


def test_missing_unrelated_artifact_still_detaches(tmp_path: Path) -> None:
    root = _project(tmp_path)
    (root / "README.md").unlink()

    detach_project(root)

    assert not (root / ".agentready").exists()


def test_absolute_and_relative_targets_work_from_unrelated_cwd(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    absolute_project = _project(tmp_path, "absolute_project")
    relative_project = _project(tmp_path, "relative_project")
    caller = tmp_path / "unrelated/caller"
    caller.mkdir(parents=True)
    relative = Path(os.path.relpath(relative_project, caller))
    monkeypatch.chdir(caller)

    detach_project(absolute_project)
    detach_project(relative)

    assert not (absolute_project / ".agentready").exists()
    assert not (relative_project / ".agentready").exists()


def test_cli_success_then_deterministic_refusal(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = _project(tmp_path)

    assert main(["detach", str(root)]) == 0
    assert "Detached AgentReady metadata" in capsys.readouterr().out
    assert main(["detach", str(root)]) == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "not AgentReady-managed or is already detached" in captured.err


def test_detached_project_has_no_agentready_runtime_or_development_dependency(
    tmp_path: Path,
) -> None:
    root = _project(tmp_path)
    detach_project(root)
    pyproject = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))

    assert all("agentready" not in item.lower() for item in pyproject["project"]["dependencies"])
    for source in (root / "src").rglob("*.py"):
        tree = ast.parse(source.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                assert all(
                    alias.name != "agentready" and not alias.name.startswith("agentready.")
                    for alias in node.names
                )
            elif isinstance(node, ast.ImportFrom) and node.module is not None:
                assert node.module != "agentready" and not node.module.startswith("agentready.")


def test_symlinked_maintenance_boundary_fails_closed(tmp_path: Path) -> None:
    root = _project(tmp_path)
    boundary = root / ".agentready"
    original = root / ".agentready-original"
    outside = tmp_path / "outside-boundary"
    outside.mkdir()
    (outside / "sentinel.txt").write_text("outside", encoding="utf-8")
    boundary.rename(original)
    try:
        boundary.symlink_to(outside, target_is_directory=True)
    except OSError as exc:
        pytest.skip(f"symlink creation is unavailable: {exc}")
    before_root = _snapshot(root)
    before_outside = _snapshot(outside)

    with pytest.raises(DetachError):
        detach_project(root)

    assert _snapshot(root) == before_root
    assert _snapshot(outside) == before_outside


def test_nested_metadata_symlink_fails_closed(tmp_path: Path) -> None:
    root = _project(tmp_path)
    outside = tmp_path / "outside-file.txt"
    outside.write_text("outside", encoding="utf-8")
    link = root / ".agentready/outside-link"
    try:
        link.symlink_to(outside)
    except OSError as exc:
        pytest.skip(f"symlink creation is unavailable: {exc}")
    before_root = _snapshot(root)
    outside_bytes = outside.read_bytes()

    with pytest.raises(DetachError):
        detach_project(root)

    assert _snapshot(root) == before_root
    assert outside.read_bytes() == outside_bytes
