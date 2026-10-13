"""Continuity includes non-ignored new files before the first Git commit."""

import subprocess
from pathlib import Path

import pytest

from agentready.continuity import tracked_digest


@pytest.mark.parametrize("relative", ["src/example/new.py", "templates/new.yaml"])
def test_untracked_content_changes_digest(tmp_path: Path, relative: str) -> None:
    subprocess.run(["git", "init", str(tmp_path)], check=True, capture_output=True)
    initial = tracked_digest(tmp_path)
    file = tmp_path / relative
    file.parent.mkdir(parents=True)
    file.write_text("first", encoding="utf-8")
    created = tracked_digest(tmp_path)
    assert created is not None and created != initial
    file.write_text("second", encoding="utf-8")
    assert tracked_digest(tmp_path) != created


def test_checkpoint_metadata_does_not_stale_itself(tmp_path: Path) -> None:
    subprocess.run(["git", "init", str(tmp_path)], check=True, capture_output=True)
    initial = tracked_digest(tmp_path)
    checkpoint = tmp_path / "docs/work/checkpoints/W001.json"
    checkpoint.parent.mkdir(parents=True)
    checkpoint.write_text("{}", encoding="utf-8")
    assert tracked_digest(tmp_path) == initial


def test_uninitialized_project_tracks_new_templates(tmp_path: Path) -> None:
    first = tracked_digest(tmp_path)
    template = tmp_path / "templates/new.yaml"
    template.parent.mkdir()
    template.write_text("Resources: {}", encoding="utf-8")
    assert tracked_digest(tmp_path) != first
