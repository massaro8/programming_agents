"""Fail-closed removal of the fixed ``.agentready`` boundary."""

from __future__ import annotations

import os
import tomllib
from pathlib import Path

from agentready.core.project import Project, ProjectPath


class DetachError(ValueError):
    """A safe detachment refusal."""


def _inventory(root: Path) -> list[tuple[Path, bool]]:
    entries: list[tuple[Path, bool]] = []

    def visit(directory: Path) -> None:
        try:
            scanned = sorted(os.scandir(directory), key=lambda entry: entry.name)
            for entry in scanned:
                path = Path(entry.path)
                if entry.is_symlink():
                    raise DetachError("maintenance metadata contains a symlink")
                if entry.is_dir(follow_symlinks=False):
                    visit(path)
                    entries.append((path, True))
                elif entry.is_file(follow_symlinks=False):
                    entries.append((path, False))
                else:
                    raise DetachError("maintenance metadata contains an unsafe entry")
        except OSError as exc:
            raise DetachError(f"cannot inspect maintenance metadata: {exc}") from exc

    visit(root)
    entries.append((root, True))
    return entries


def _assert_safe_target(boundary: Path, path: Path, is_directory: bool) -> None:
    try:
        relative = path.relative_to(boundary)
    except ValueError as exc:
        raise DetachError("maintenance metadata target escaped its boundary") from exc
    current = boundary
    if current.is_symlink():
        raise DetachError("maintenance metadata changed or is unsafe")
    for part in relative.parts:
        current /= part
        if current.is_symlink():
            raise DetachError("maintenance metadata changed or is unsafe")
    if (is_directory and not path.is_dir()) or (not is_directory and not path.is_file()):
        raise DetachError("maintenance metadata changed or is unsafe")


def detach_project(target: Path | str = ".") -> None:
    """Remove only validated AgentReady maintenance metadata from ``target``."""

    if not isinstance(target, (Path, str)):
        raise TypeError("target must be a pathlib.Path or string")
    raw = Path(target)
    project = Project(raw if raw.is_absolute() else Path.cwd() / raw)
    if not project.path.is_dir() or project.path.is_symlink():
        raise DetachError("project is not AgentReady-managed or is already detached")
    boundary = project.path_for(ProjectPath(Path(".agentready")))
    if boundary.is_symlink() or not boundary.is_dir():
        raise DetachError("project is not AgentReady-managed or is already detached")
    manifest = boundary / "manifest.toml"
    if manifest.is_symlink() or not manifest.is_file():
        raise DetachError("AgentReady manifest is missing or unsafe")
    try:
        data = tomllib.loads(manifest.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, tomllib.TOMLDecodeError) as exc:
        raise DetachError("AgentReady manifest is malformed") from exc
    if (
        data.get("schema") != 1
        or data.get("generator") != "agentready"
        or data.get("profile") != "python"
        or not isinstance(data.get("generator_version"), str)
        or not data["generator_version"]
    ):
        raise DetachError("AgentReady manifest is unsupported")
    entries = _inventory(boundary)
    for path, is_directory in entries:
        _assert_safe_target(boundary, path, is_directory)
    for path, is_directory in entries:
        _assert_safe_target(boundary, path, is_directory)
        try:
            if is_directory:
                path.rmdir()
            else:
                path.unlink()
        except OSError as exc:
            raise DetachError(f"cannot remove maintenance metadata: {exc}") from exc
