"""Bundled family contracts, independent of CLI orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from agentready.core.ownership import OwnershipClass
from agentready.core.profiles import ProfileContract, get_profile

DEFAULT_FAMILY = "python"
SUPPORTED_FAMILIES = ("python", "cloudformation")


def component_path(path: str) -> str | None:
    """Map the additive infrastructure artifacts into a Python repository."""
    if path.startswith(("templates/", "parameters/", "policies/")) or (
        path.startswith("tests/fixtures/") and path.endswith(".yaml")
    ):
        return "infrastructure/" + path
    if path.startswith("docs/agent/"):
        return path.replace("docs/agent/", "docs/infrastructure/", 1)
    if path in ("README.md", "docs/ARCHITECTURE.md", ".cfnlintrc"):
        return {
            "README.md": "docs/infrastructure/README.md",
            "docs/ARCHITECTURE.md": "docs/infrastructure/ARCHITECTURE.md",
            ".cfnlintrc": ".cfnlintrc",
        }[path]
    if path.startswith(
        (
            ".agents/skills/cloudformation-change/",
            ".agents/skills/aws-infrastructure-inspection/",
            ".claude/skills/cloudformation-change/",
            ".claude/skills/aws-infrastructure-inspection/",
        )
    ) or path in (
        "scripts/fixture_check.py",
        "scripts/infrastructure_checks.py",
        "scripts/infrastructure_tools.py",
        "scripts/environment_contracts.py",
        "scripts/aws_inspection.py",
        "docs/infrastructure/environments.json",
        "docs/infrastructure/parameters.json",
        "docs/infrastructure/ENGINEERING.md",
        "bitbucket-pipelines.yml",
    ):
        return path
    return None


@dataclass(frozen=True, slots=True)
class ComposedContract:
    """Python ownership plus the explicit bundled infrastructure component."""

    base: ProfileContract

    @property
    def name(self) -> str:
        return self.base.name

    def ownership_paths(self, package: str) -> dict[OwnershipClass, tuple[str, ...]]:
        ownership = self.base.ownership_paths(package)
        for cls, paths in InfrastructureContract().ownership_paths().items():
            ownership[cls] += tuple(mapped for path in paths if (mapped := component_path(path)))
        return ownership

    def required_paths(self, package: str) -> tuple[Path, ...]:
        return tuple(
            Path(path) for paths in self.ownership_paths(package).values() for path in paths
        )


@dataclass(frozen=True, slots=True)
class InfrastructureContract:
    """Artifact ownership for the infrastructure template family."""

    name: str = "infrastructure"

    def ownership_paths(self, package: str = "") -> dict[OwnershipClass, tuple[str, ...]]:
        root = Path(__file__).parents[1] / "templates/cloudformation/template"
        paths = sorted(
            path.relative_to(root).as_posix().removesuffix(".jinja")
            for path in root.rglob("*")
            if path.is_file() and "__pycache__" not in path.parts
        )
        if len(paths) != len(set(paths)):
            raise ValueError("duplicate rendered CloudFormation artifact paths")
        generated = tuple(
            path
            for path in paths
            if path.startswith((".agentready/", ".claude/", "docs/generated/"))
            or path in ("CLAUDE.md", "docs/work/index.md", "docs/changelog/index.md")
        )
        project = tuple(
            path
            for path in paths
            if path.startswith(("templates/", "parameters/", "policies/", ".github/"))
            or path in ("README.md", ".gitignore", ".cfnlintrc", "docs/ARCHITECTURE.md")
        )
        shared = tuple(path for path in paths if path not in (*generated, *project))
        return {
            OwnershipClass.PROJECT_OWNED: project,
            OwnershipClass.SHARED: shared,
            OwnershipClass.GENERATED: generated,
        }

    def required_paths(self, package: str = "") -> tuple[Path, ...]:
        return tuple(
            Path(path) for paths in self.ownership_paths(package).values() for path in paths
        )


def get_contract(
    family: str = DEFAULT_FAMILY,
    profile: str | None = None,
    *,
    components: tuple[str, ...] | list[str] = (),
) -> ProfileContract | InfrastructureContract | ComposedContract:
    """Resolve a supported family/profile pair; never silently fall back."""

    if (
        not isinstance(components, (tuple, list))
        or any(component != "cloudformation" for component in components)
        or len(components) > 1
        or (components and family != "python")
    ):
        raise ValueError("only Python supports the single cloudformation component")
    if family == "python" and components:
        return ComposedContract(get_profile(profile or "minimal"))
    if family == "python":
        return get_profile(profile or "minimal")
    if family == "cloudformation":
        if profile not in (None, "infrastructure"):
            raise ValueError("cloudformation supports only profile 'infrastructure'")
        return InfrastructureContract()
    raise ValueError(
        f"unsupported family {family!r}; choose one of: {', '.join(SUPPORTED_FAMILIES)}"
    )
