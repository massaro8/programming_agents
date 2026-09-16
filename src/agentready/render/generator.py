"""Generate independent projects from the trusted bundled Copier template."""

from __future__ import annotations

import keyword
import re
from contextlib import ExitStack
from importlib import resources
from pathlib import Path, PureWindowsPath

import copier

from agentready import __version__
from agentready.core.ownership import ArtifactOwnership, OwnershipClass
from agentready.core.project import Project, ProjectPath

_NAME_RE = re.compile(r"[a-z][a-z0-9]*(?:[-_][a-z0-9]+)*\Z")
_OWNERSHIP: dict[OwnershipClass, tuple[str, ...]] = {
    OwnershipClass.PROJECT_OWNED: (
        ".github/workflows/ci.yml",
        ".gitignore",
        ".python-version",
        "README.md",
        "docs/ARCHITECTURE.md",
        "pyproject.toml",
        "src/{package}/__init__.py",
        "src/{package}/main.py",
        "tests/test_main.py",
    ),
    OwnershipClass.SHARED: (
        "AGENTS.md",
        "docs/agent/standards/testing.md",
        "docs/agent/workflows/feature.md",
    ),
    OwnershipClass.GENERATED: ("CLAUDE.md", ".agentready/manifest.toml"),
}


class GeneratorError(ValueError):
    """A user-correctable project generation error."""


def _validate_name(name: str) -> str:
    if not isinstance(name, str) or not _NAME_RE.fullmatch(name):
        raise GeneratorError("target name must be lowercase ASCII with safe separators")
    if PureWindowsPath(name).is_reserved():
        raise GeneratorError("target name is reserved on Windows")
    package = name.replace("-", "_")
    if keyword.iskeyword(package) or not package.isidentifier():
        raise GeneratorError("target name does not produce a valid Python package")
    return package


def _ownership_plan(package: str) -> tuple[ArtifactOwnership, ...]:
    return tuple(
        ArtifactOwnership(ProjectPath(Path(path.format(package=package))), ownership)
        for ownership, paths in _OWNERSHIP.items()
        for path in paths
    )


def generate_project(target: Path) -> Project:
    """Generate a named independent Python project at ``target``."""

    if not isinstance(target, Path):
        raise TypeError("target must be a pathlib.Path")
    absolute = target if target.is_absolute() else Path.cwd() / target
    project = Project(absolute)
    name = project.path.name
    package = _validate_name(name)
    if project.path.is_symlink():
        raise GeneratorError("target must not be a symlink")
    if project.path.exists() and (project.path.is_file() or not project.path.is_dir()):
        raise GeneratorError("target must be a directory")
    if project.path.is_dir() and any(project.path.iterdir()):
        raise GeneratorError("target directory must be empty")
    plan = _ownership_plan(package)
    ownership = {
        "project_owned": [
            str(item.path.path).replace("\\", "/")
            for item in plan
            if item.ownership is OwnershipClass.PROJECT_OWNED
        ],
        "shared": [
            str(item.path.path).replace("\\", "/")
            for item in plan
            if item.ownership is OwnershipClass.SHARED
        ],
        "generated": [
            str(item.path.path).replace("\\", "/")
            for item in plan
            if item.ownership is OwnershipClass.GENERATED
        ],
    }
    data = {
        "distribution_name": name,
        "package_name": package,
        "generator_version": __version__,
        "ownership": ownership,
    }
    with ExitStack() as stack:
        template = stack.enter_context(
            resources.as_file(resources.files("agentready.templates.python"))
        )
        try:
            copier.run_copy(
                str(template),
                project.path,
                data=data,
                defaults=True,
                overwrite=False,
                unsafe=False,
                skip_tasks=True,
                cleanup_on_error=True,
                quiet=True,
            )
        except Exception as exc:
            raise GeneratorError(f"project generation failed: {exc}") from exc
    return project
