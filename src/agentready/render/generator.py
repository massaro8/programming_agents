"""Generate independent projects from the trusted bundled Copier template."""

from __future__ import annotations

import json
import keyword
import re
import tempfile
from contextlib import ExitStack
from importlib import resources
from pathlib import Path, PureWindowsPath

import copier

from agentready import __version__
from agentready.core.families import component_path, get_contract
from agentready.core.ownership import ArtifactOwnership, OwnershipClass
from agentready.core.project import Project, ProjectPath

_NAME_RE = re.compile(r"[a-z][a-z0-9]*(?:[-_][a-z0-9]+)*\Z")


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


def generate_project(
    target: Path,
    profile: str | None = None,
    *,
    family: str = "python",
    components: tuple[str, ...] | list[str] = (),
    into_existing: bool = False,
) -> Project:
    """Generate an independent project from an explicit trusted bundled family."""

    if not isinstance(target, Path):
        raise TypeError("target must be a pathlib.Path")
    absolute = target if target.is_absolute() else Path.cwd() / target
    project = Project(absolute)
    name = project.path.name
    package = _validate_name(name)
    if any(
        path.is_symlink() or path.is_junction() for path in (project.path, *project.path.parents)
    ):
        raise GeneratorError("target and its ancestors must not be symlinks or junctions")
    if project.path.exists() and (project.path.is_file() or not project.path.is_dir()):
        raise GeneratorError("target must be a directory")
    if into_existing:
        from agentready.render.existing import ExistingInitError, initialize_existing

        if ".." in absolute.parts:
            raise GeneratorError("--into-existing requires a path without '..'; resolve it first")
        try:
            initialize_existing(
                project.path,
                lambda staged: generate_project(
                    staged, profile, family=family, components=components
                ),
            )
        except ExistingInitError as exc:
            raise GeneratorError(str(exc)) from exc
        return project
    if project.path.is_dir() and any(project.path.iterdir()):
        raise GeneratorError("target directory must be empty")
    try:
        selected_profile = get_contract(family, profile, components=components)
    except ValueError as exc:
        raise GeneratorError(str(exc)) from exc
    plan = tuple(
        ArtifactOwnership(ProjectPath(Path(path)), cls)
        for cls, paths in selected_profile.ownership_paths(package).items()
        for path in paths
    )
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
    data: dict[str, object] = {
        "project_name": name,
        "distribution_name": name,
        "package_name": package,
        "profile": selected_profile.name,
        "family": family,
        "components": list(components),
        "generator_version": __version__,
        "ownership": ownership,
        "inventory_source": resources.files("agentready.core")
        .joinpath("inventory.py")
        .read_text(encoding="utf-8"),
    }
    for module in (
        "local_paths",
        "skill_qa",
        "hooks",
        "continuity",
        "verification",
        "environment_contracts",
        "aws_inspection",
    ):
        data[f"{module}_source"] = (
            resources.files("agentready")
            .joinpath(f"{module}.py")
            .read_text(encoding="utf-8")
            .replace("from agentready.local_paths import", "from local_paths import")
        )
    for module in ("work_registry", "skill_check", "skill_routes", "context", "status"):
        source = (
            resources.files("agentready.templates.python")
            .joinpath(f"template/scripts/{module}.py")
            .read_text(encoding="utf-8")
        )
        if (family == "cloudformation" or components) and module == "skill_routes":
            source = source.replace(
                'FAMILY = "python"', f'FAMILY = "{"hybrid" if components else "cloudformation"}"'
            )
        data[f"{module}_source"] = source
    with ExitStack() as stack:
        template = stack.enter_context(
            resources.as_file(resources.files(f"agentready.templates.{family}"))
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
    if components:
        (project.path / "scripts/skill_routes.py").write_text(
            str(data["skill_routes_source"]), encoding="utf-8"
        )
        _render_component(project.path, data)
    if family == "cloudformation":
        from agentready.doctor.infrastructure import render_map

        (project.path / "docs/generated/CODEBASE_MAP.md").write_text(
            render_map(project.path), encoding="utf-8", newline="\n"
        )
    return project


def _render_component(root: Path, data: dict[str, object]) -> None:
    """Render trusted component assets separately without overwriting base artifacts."""
    with (
        tempfile.TemporaryDirectory() as temporary,
        resources.as_file(resources.files("agentready.templates.cloudformation")) as template,
    ):
        component = Path(temporary) / "component"
        copier.run_copy(
            str(template),
            component,
            data=data,
            defaults=True,
            overwrite=False,
            unsafe=False,
            skip_tasks=True,
            quiet=True,
        )
        for source in component.rglob("*"):
            if not source.is_file():
                continue
            relative = source.relative_to(component).as_posix()
            destination = component_path(relative)
            if destination is None:
                continue
            path = root / destination
            if path.exists():
                raise GeneratorError(
                    f"component artifact conflicts with Python artifact: {destination}"
                )
            path.parent.mkdir(parents=True, exist_ok=True)
            text = source.read_text(encoding="utf-8")
            for old, new in (
                ("docs/agent/", "docs/infrastructure/"),
                ("tests/fixtures/", "infrastructure/tests/fixtures/"),
                ("templates/", "infrastructure/templates/"),
                ("parameters/", "infrastructure/parameters/"),
                ("policies/", "infrastructure/policies/"),
            ):
                if relative not in (
                    "scripts/infrastructure_checks.py",
                    "scripts/fixture_check.py",
                    "scripts/environment_contracts.py",
                    "scripts/aws_inspection.py",
                ):
                    text = text.replace(old, new)
            path.write_text(text, encoding="utf-8", newline="\n")
    workflow = root / ".github/workflows/ci.yml"
    infrastructure_ci = (
        resources.files("agentready.templates.cloudformation")
        .joinpath("template/.github/workflows/ci.yml")
        .read_text(encoding="utf-8")
    )
    install = infrastructure_ci.split("      - run: python -m pip install", 1)[1].split(
        "      - run: python scripts/project.py verify", 1
    )[0]
    workflow.write_text(
        workflow.read_text(encoding="utf-8").replace(
            "      - run: uv sync",
            "      - uses: actions/setup-python@v5\n"
            "        with:\n"
            "          python-version: '3.12'\n"
            "      - run: python -m pip install" + install + "      - run: uv sync",
        ),
        encoding="utf-8",
    )
    bitbucket = root / "bitbucket-pipelines.yml"
    bitbucket.write_text(
        bitbucket.read_text(encoding="utf-8").replace(
            "          - python scripts/project.py verify",
            "          - curl -LsSf https://astral.sh/uv/install.sh | sh\n"
            '          - export PATH="$HOME/.local/bin:$PATH"\n'
            "          - uv sync --all-groups\n"
            "          - uv run python scripts/project.py verify",
        ),
        encoding="utf-8",
    )
    manifest = root / ".agentready/manifest.toml"
    manifest.write_text(
        'family = "python"\ncomponents = ["cloudformation"]\n'
        + manifest.read_text(encoding="utf-8"),
        encoding="utf-8",
        newline="\n",
    )
    config = root / "docs/verification.json"
    settings = json.loads(config.read_text(encoding="utf-8"))
    settings["components"] = ["cloudformation"]
    settings["required_stages"]["default"] += [
        "environment contracts",
        "cfn-lint",
        "Guard",
        "negative fixtures",
    ]
    settings["required_stages"]["DOCS"] = settings["required_stages"]["default"]
    config.write_text(json.dumps(settings, indent=2) + "\n", encoding="utf-8")
    from agentready.skill_qa import claude_view

    for canonical in (root / ".agents/skills").glob("*/SKILL.md"):
        (root / f".claude/skills/{canonical.parent.name}/SKILL.md").write_text(
            claude_view(canonical.read_text(encoding="utf-8"), canonical.parent.name),
            encoding="utf-8",
        )
    from agentready.doctor.infrastructure import inventory

    map_path = root / "docs/generated/CODEBASE_MAP.md"
    map_path.write_text(
        map_path.read_text(encoding="utf-8")
        + "\n## Infrastructure files\n\n"
        + "".join(
            f"- `{path}`\n"
            for area in ("infrastructure/", "docs/infrastructure/")
            for path in sorted(inventory(root, composed=True))
            if path.startswith(area)
        ),
        encoding="utf-8",
    )
    agents = root / "AGENTS.md"
    agents.write_text(
        agents.read_text(encoding="utf-8") + "\n## Infrastructure component\n\n"
        "Read [infrastructure guidance](docs/infrastructure/index.md) for CloudFormation changes.\n"
        "Infrastructure assets live under `infrastructure/`; use the shared repository tools.\n",
        encoding="utf-8",
    )
