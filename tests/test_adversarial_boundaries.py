from __future__ import annotations

import os
import subprocess
import sys
import threading
from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

from agentready import continuity, hooks
from agentready.cli import main
from agentready.detach.service import DetachError, detach_project
from agentready.doctor.inspector import inspect
from agentready.local_paths import repository_write
from agentready.render.generator import GeneratorError, generate_project


def junction(link: Path, target: Path) -> None:
    if os.name != "nt":
        pytest.skip("Windows junction integration test")
    escaped_link = str(link).replace("'", "''")
    escaped_target = str(target).replace("'", "''")
    result = subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-Command",
            f"New-Item -ItemType Junction -Path '{escaped_link}' -Target '{escaped_target}'",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode or not link.is_junction():
        pytest.skip(f"junction creation unavailable: {result.stderr}")


@pytest.mark.parametrize("location", ["boundary", "nested", "root", "ancestor"])
def test_detach_rejects_real_junction_without_external_deletion(
    tmp_path: Path,
    location: str,
) -> None:
    root = tmp_path / "project"
    generate_project(root)
    sentinel_root = tmp_path / "outside"
    sentinel_root.mkdir()
    sentinel = sentinel_root / "sentinel.txt"
    sentinel.write_text("preserve", encoding="utf-8")
    original_manifest = (root / ".agentready/manifest.toml").read_bytes()
    if location == "nested":
        junction(root / ".agentready/external", sentinel_root)
    elif location == "boundary":
        (root / ".agentready").rename(sentinel_root / "metadata")
        junction(root / ".agentready", sentinel_root / "metadata")
        sentinel = sentinel_root / "metadata/sentinel.txt"
        sentinel.write_text("preserve", encoding="utf-8")
    elif location == "root":
        junction(tmp_path / "alias", root)
        root = tmp_path / "alias"
    else:
        junction(tmp_path / "alias", tmp_path / "project")
        root = tmp_path / "alias/child"
        generate_project(tmp_path / "project/child")
        original_manifest = (root / ".agentready/manifest.toml").read_bytes()
    with pytest.raises(DetachError):
        detach_project(root)
    assert sentinel.read_text(encoding="utf-8") == "preserve"
    assert (root / ".agentready/manifest.toml").read_bytes() == original_manifest


@pytest.mark.parametrize("ancestor", [False, True])
def test_init_rejects_real_junction_target_or_ancestor(tmp_path: Path, ancestor: bool) -> None:
    outside = tmp_path / "outside"
    outside.mkdir()
    link = tmp_path / "project"
    junction(link, outside)
    with pytest.raises(GeneratorError):
        generate_project(link / "child" if ancestor else link)
    assert list(outside.iterdir()) == []


@pytest.mark.parametrize("location", ["root", "ancestor", "metadata", "work"])
def test_doctor_rejects_junction_boundaries(tmp_path: Path, location: str) -> None:
    root = tmp_path / "project"
    generate_project(root)
    if location in ("root", "ancestor"):
        junction(tmp_path / "alias", root)
        if location == "ancestor":
            generate_project(root / "child")
            root = tmp_path / "alias/child"
        else:
            root = tmp_path / "alias"
    else:
        relative = ".agentready" if location == "metadata" else "docs/work"
        original = root / relative
        outside = tmp_path / "outside"
        original.rename(outside)
        junction(original, outside)
    report = inspect(root)
    expected_check = {
        "root": "project.root",
        "ancestor": "project.root",
        "metadata": "manifest.present",
        "work": "work.registry",
    }[location]
    assert any(
        finding.check_id == expected_check and finding.status.value == "FAIL"
        for finding in report.findings
    )


def test_init_cli_reports_unreadable_target_without_traceback(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    target = tmp_path / "project"
    target.mkdir()
    original = Path.iterdir

    def unreadable(path: Path) -> Iterator[Path]:
        if path == target:
            raise PermissionError("target directory is unreadable")
        return original(path)

    monkeypatch.setattr(Path, "iterdir", unreadable)
    assert main(["init", str(target)]) == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "unreadable" in captured.err
    assert list(original(target)) == []


@pytest.mark.parametrize("capability", ["checkpoint", "evidence"])
def test_concurrent_writes_preserve_every_success(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capability: str
) -> None:
    root = tmp_path / "project"
    (root / "docs/work").mkdir(parents=True)
    (root / "docs/agent").mkdir()
    (root / "docs/work/W001-test.md").write_text(
        "# W001 — Test\n\nType: FEATURE\nStatus: READY\n", encoding="utf-8"
    )
    hooks.configure(root, "evidence-recorder", enabled=True)
    module = continuity if capability == "checkpoint" else hooks
    first_writing = threading.Event()
    release_first = threading.Event()
    original = module.write_json

    def controlled_write(root: Path, relative: str, data: dict) -> None:
        first = (
            data.get("state", {}).get("objective") == "first"
            if capability == "checkpoint"
            else data["entries"][-1]["command"] == "first"
        )
        if first:
            first_writing.set()
            assert release_first.wait(10)
        original(root, relative, data)

    monkeypatch.setattr(module, "write_json", controlled_write)

    def write(identity: str) -> bool:
        try:
            if capability == "checkpoint":
                continuity.checkpoint(
                    root,
                    "W001",
                    {
                        "objective": identity,
                        "next_step": "Verify",
                        "files": [],
                        "decisions": [],
                        "validation": [],
                        "risks": [],
                        "questions": [],
                    },
                )
            else:
                hooks.record(root, identity, 0, "W001")
            return True
        except ValueError:
            return False

    with ThreadPoolExecutor(2) as pool:
        first = pool.submit(write, "first")
        assert first_writing.wait(10)
        second = pool.submit(write, "second")
        try:
            second_success = second.result(timeout=10)
        finally:
            release_first.set()
        first_success = first.result(timeout=10)
    assert first_success
    if capability == "checkpoint":
        assert not second_success, "two successful creations replaced an existing checkpoint"
    else:
        from agentready.local_paths import read_json

        entries = read_json(root, hooks.EVIDENCE)["entries"]
        assert len(entries) == int(first_success) + int(second_success)


def test_repository_write_rejects_other_process_and_recovers(tmp_path: Path) -> None:
    code = (
        "from pathlib import Path; from agentready.local_paths import repository_write; "
        f"root=Path({str(tmp_path)!r}); "
        "\ntry:\n with repository_write(root, 'state.json'): pass\n"
        "except ValueError as exc:\n print(exc); raise SystemExit(1)\n"
    )
    with repository_write(tmp_path, "state.json"):
        result = subprocess.run(
            [sys.executable, "-c", code], capture_output=True, text=True, check=False, timeout=10
        )
        assert result.returncode == 1
        assert "update in progress" in result.stdout
    assert not (tmp_path / "state.json.lock").exists()
    with pytest.raises(OSError, match="injected"), repository_write(tmp_path, "state.json"):
        raise OSError("injected")
    assert not (tmp_path / "state.json.lock").exists()
    with repository_write(tmp_path, "state.json"):
        pass


def test_stale_lock_is_preserved_with_actionable_error(tmp_path: Path) -> None:
    lock = tmp_path / "state.json.lock"
    lock.write_text("interrupted writer", encoding="utf-8")
    with (
        pytest.raises(ValueError, match="confirming no writer is running"),
        repository_write(tmp_path, "state.json"),
    ):
        pytest.fail("stale lock must not be stolen")
    assert lock.read_text(encoding="utf-8") == "interrupted writer"


def test_cli_unicode_target_succeeds_with_redirected_legacy_encoding(tmp_path: Path) -> None:
    target = tmp_path / "日本" / "project"
    environment = os.environ.copy()
    environment["PYTHONIOENCODING"] = "cp1252"
    for command in (["init", str(target)], ["detach", str(target)]):
        result = subprocess.run(
            [sys.executable, "-m", "agentready.cli", *command],
            env=environment,
            capture_output=True,
            check=False,
            timeout=60,
        )
        assert result.returncode == 0, result.stderr.decode("cp1252", errors="replace")
        assert "project" in result.stdout.decode("cp1252")
    assert (target / "src/project/main.py").is_file()
    assert not (target / ".agentready").exists()
