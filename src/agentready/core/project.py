"""Project roots and safe repository-relative paths."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _lexically_normalize(path: Path) -> Path:
    """Normalize a path without filesystem access or symlink resolution."""

    return Path(os.path.normpath(str(path)))


@dataclass(frozen=True, slots=True)
class ProjectPath:
    """A non-empty, repository-relative path with no parent traversal."""

    path: Path

    def __post_init__(self) -> None:
        if not isinstance(self.path, Path):
            raise TypeError("ProjectPath.path must be a pathlib.Path")
        if not str(self.path) or self.path == Path("."):
            raise ValueError("project path must be non-empty")
        if self.path.anchor:
            raise ValueError("project path must be unanchored and relative")
        if ".." in self.path.parts:
            raise ValueError("project path must not contain parent traversal")
        normalized = _lexically_normalize(self.path)
        if normalized == Path("."):
            raise ValueError("project path must be non-empty")
        object.__setattr__(self, "path", normalized)


@dataclass(frozen=True, slots=True)
class Project:
    """An absolute project root, normalized lexically without filesystem access."""

    path: Path

    def __post_init__(self) -> None:
        if not isinstance(self.path, Path):
            raise TypeError("Project.path must be a pathlib.Path")
        if not self.path.is_absolute():
            raise ValueError("project root must be absolute")
        object.__setattr__(self, "path", _lexically_normalize(self.path))

    def path_for(self, project_path: ProjectPath) -> Path:
        """Return the deterministic absolute path for a repository-relative path."""

        if not isinstance(project_path, ProjectPath):
            raise TypeError("path_for() requires a ProjectPath")
        return self.path / project_path.path

    def relative_path(self, absolute_path: Path) -> ProjectPath:
        """Convert an absolute in-project path to a repository-relative value."""

        if not isinstance(absolute_path, Path):
            raise TypeError("absolute_path must be a pathlib.Path")
        if not absolute_path.is_absolute():
            raise ValueError("absolute_path must be absolute")
        candidate = _lexically_normalize(absolute_path)
        if candidate == self.path:
            raise ValueError("project root is not an artifact path")
        try:
            relative = candidate.relative_to(self.path)
        except ValueError as exc:
            raise ValueError("path is outside the project root") from exc
        return ProjectPath(relative)
