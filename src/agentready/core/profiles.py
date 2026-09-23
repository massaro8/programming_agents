"""Canonical contracts for the bundled Python project profiles.

The profile contract is deliberately data-only.  Rendering, doctor, and the
manifest all consume the same artifact lists so a profile cannot silently
start requiring files that the renderer does not produce.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from agentready.core.ownership import OwnershipClass

DEFAULT_PROFILE = "minimal"
SUPPORTED_PROFILES = ("minimal", "application", "service")

_COMMON_PROJECT_OWNED = (
    ".github/workflows/ci.yml",
    ".gitignore",
    ".python-version",
    "README.md",
    "docs/ARCHITECTURE.md",
    "pyproject.toml",
)
_COMMON_SHARED = (
    "AGENTS.md",
    "docs/work/templates/feature.md",
    "docs/work/templates/bugfix.md",
    "docs/work/templates/refactor.md",
    "docs/work/templates/maintenance.md",
    "docs/work/templates/documentation.md",
    "docs/work/templates/security.md",
    "scripts/work_registry.py",
    "docs/adr/0000-template.md",
    "docs/agent/index.md",
    "docs/agent/standards/python.md",
    "docs/agent/standards/architecture.md",
    "docs/agent/standards/testing.md",
    "docs/agent/standards/dependencies.md",
    "docs/agent/standards/documentation.md",
    "docs/agent/standards/security.md",
    "docs/agent/workflows/feature.md",
    "docs/agent/workflows/bugfix.md",
    "docs/agent/workflows/refactor.md",
    "docs/agent/workflows/maintenance.md",
    "docs/agent/workflows/documentation.md",
    "docs/agent/workflows/security.md",
)
_COMMON_GENERATED = (
    "CLAUDE.md",
    ".agentready/manifest.toml",
    "docs/work/index.md",
    "docs/changelog/index.md",
)
_PROFILE_FILES: dict[str, tuple[str, ...]] = {
    "minimal": (
        "src/{package}/__init__.py",
        "src/{package}/main.py",
        "tests/test_main.py",
    ),
    "application": (
        "src/{package}/__init__.py",
        "src/{package}/bootstrap.py",
        "src/{package}/config.py",
        "src/{package}/main.py",
        "src/{package}/domain/__init__.py",
        "src/{package}/domain/errors.py",
        "src/{package}/application/__init__.py",
        "src/{package}/application/service.py",
        "tests/test_main.py",
    ),
    "service": (
        "src/{package}/__init__.py",
        "src/{package}/bootstrap.py",
        "src/{package}/config.py",
        "src/{package}/main.py",
        "src/{package}/domain/__init__.py",
        "src/{package}/domain/errors.py",
        "src/{package}/application/__init__.py",
        "src/{package}/application/service.py",
        "src/{package}/adapters/__init__.py",
        "src/{package}/adapters/console.py",
        "tests/test_main.py",
    ),
}


@dataclass(frozen=True, slots=True)
class ProfileContract:
    """Required artifact structure for one supported profile."""

    name: str
    profile_files: tuple[str, ...]

    def ownership_paths(self, package: str) -> dict[OwnershipClass, tuple[str, ...]]:
        """Return all owned repository-relative files for ``package``."""

        source = tuple(path.format(package=package) for path in self.profile_files)
        return {
            OwnershipClass.PROJECT_OWNED: (*_COMMON_PROJECT_OWNED, *source),
            OwnershipClass.SHARED: _COMMON_SHARED,
            OwnershipClass.GENERATED: _COMMON_GENERATED,
        }

    def required_paths(self, package: str) -> tuple[Path, ...]:
        """Return files that must exist for a healthy generated repository."""

        ownership = self.ownership_paths(package)
        return tuple(Path(path) for paths in ownership.values() for path in paths)


def get_profile(name: str = DEFAULT_PROFILE) -> ProfileContract:
    """Resolve a supported profile or raise ``ValueError``."""

    if not isinstance(name, str) or name not in _PROFILE_FILES:
        supported = ", ".join(SUPPORTED_PROFILES)
        raise ValueError(f"unsupported profile {name!r}; choose one of: {supported}")
    return ProfileContract(name, _PROFILE_FILES[name])


def ownership_paths(
    profile: str = DEFAULT_PROFILE, package: str = "{package}"
) -> dict[OwnershipClass, tuple[str, ...]]:
    """Return canonical ownership paths for a profile and package."""

    return get_profile(profile).ownership_paths(package)
