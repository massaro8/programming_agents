"""Deterministic, local, read-only checks for generated repositories."""

from __future__ import annotations

import re
import tomllib
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from agentready.core.ownership import ArtifactOwnership, OwnershipClass
from agentready.core.profiles import get_profile
from agentready.core.project import Project, ProjectPath
from agentready.doctor.codebase_map import validate as validate_codebase_map
from agentready.doctor.work import validate as validate_work

CHECKS = (
    "project.root",
    "manifest.present",
    "manifest.valid",
    "ownership.paths",
    "ownership.unique",
    "ownership.artifacts",
    "guidance.agents",
    "guidance.references",
    "repository.structure",
    "repository.codebase_map",
    "repository.independence",
    "work.registry",
    "detach.ready",
)


class FindingStatus(Enum):
    PASS = "PASS"
    FAIL = "FAIL"


@dataclass(frozen=True, slots=True)
class DoctorFinding:
    check_id: str
    status: FindingStatus
    message: str
    path: ProjectPath | None = None


@dataclass(frozen=True, slots=True)
class DoctorReport:
    findings: tuple[DoctorFinding, ...]

    @property
    def healthy(self) -> bool:
        return all(f.status is FindingStatus.PASS for f in self.findings)


def _finding(check: str, ok: bool, message: str, path: ProjectPath | None = None) -> DoctorFinding:
    return DoctorFinding(check, FindingStatus.PASS if ok else FindingStatus.FAIL, message, path)


def _safe(project: Project, rel: str) -> tuple[ProjectPath | None, Path | None]:
    try:
        pp = ProjectPath(Path(rel))
    except (TypeError, ValueError):
        return None, None
    current = project.path
    for part in pp.path.parts:
        current /= part
        if current.is_symlink():
            return pp, None
    return pp, project.path_for(pp)


def _safe_file(project: Project, rel: str) -> bool:
    _, path = _safe(project, rel)
    return path is not None and path.is_file()


def _read_safe_text(project: Project, rel: str) -> tuple[ProjectPath | None, str | None]:
    project_path, path = _safe(project, rel)
    if path is None or not path.is_file():
        return project_path, None
    try:
        return project_path, path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return project_path, None


def _guidance_references(text: str) -> set[str]:
    references = set(re.findall(r"`(docs/agent/[^`]+)`", text))
    for target in re.findall(r"\]\(([^)]+)\)", text):
        target = target.strip()
        if target.startswith("<") and target.endswith(">"):
            target = target[1:-1]
        target = target.split("#", 1)[0]
        if (
            target
            and not re.match(r"^[A-Za-z][A-Za-z0-9+.-]*://", target)
            and not target.lower().startswith("mailto:")
        ):
            references.add(target)
    return references


def _dependency_values(data: object) -> list[str] | None:
    if not isinstance(data, dict):
        return None
    project_data = data.get("project", {})
    groups = data.get("dependency-groups", {})
    if not isinstance(project_data, dict) or not isinstance(groups, dict):
        return None
    dependencies = project_data.get("dependencies", [])
    optional = project_data.get("optional-dependencies", {})
    if not isinstance(dependencies, list) or not all(isinstance(v, str) for v in dependencies):
        return None
    if not isinstance(optional, dict) or not all(
        isinstance(v, list) and all(isinstance(item, str) for item in v) for v in optional.values()
    ):
        return None
    if not all(
        isinstance(v, list) and all(isinstance(item, str) for item in v) for v in groups.values()
    ):
        return None
    return [
        *dependencies,
        *(item for values in optional.values() for item in values),
        *(item for values in groups.values() for item in values),
    ]


def _requirement_name(requirement: str) -> str | None:
    match = re.match(r"^\s*([A-Za-z0-9][A-Za-z0-9_.-]*)", requirement)
    if match is None:
        return None
    return re.sub(r"[-_.]+", "-", match.group(1).lower())


def inspect(root: Path | str = ".") -> DoctorReport:
    """Inspect a repository without changing it or invoking project tools."""

    findings: list[DoctorFinding] = []
    try:
        raw = Path(root)
        absolute = raw if raw.is_absolute() else Path.cwd() / raw
        project = Project(absolute)
        root_ok = project.path.is_dir() and not project.path.is_symlink()
    except (TypeError, ValueError, OSError) as exc:
        findings.append(_finding("project.root", False, f"invalid project root: {exc}"))
        findings.extend(
            _finding(c, False, "not inspected because project root is invalid") for c in CHECKS[1:]
        )
        return DoctorReport(tuple(findings))
    findings.append(
        _finding(
            "project.root",
            root_ok,
            "project root is safe" if root_ok else "project root is missing or unsafe",
        )
    )
    if not root_ok:
        findings.extend(
            _finding(c, False, "not inspected because project root is unavailable")
            for c in CHECKS[1:]
        )
        return DoctorReport(tuple(findings))

    manifest_pp, manifest_path = _safe(project, ".agentready/manifest.toml")
    manifest_ok = manifest_path is not None and manifest_path.is_file()
    findings.append(
        _finding(
            "manifest.present",
            manifest_ok,
            "manifest is present" if manifest_ok else "manifest is missing or unsafe",
            manifest_pp,
        )
    )
    manifest: dict[str, object] = {}
    valid = False
    profile_contract = None
    if manifest_ok and manifest_path is not None:
        try:
            parsed = tomllib.loads(manifest_path.read_text(encoding="utf-8"))
            ownership = parsed.get("ownership")
            profile_name = parsed.get("profile")
            try:
                profile_contract = get_profile(profile_name)  # type: ignore[arg-type]
            except ValueError:
                profile_contract = None
            valid = (
                parsed.get("schema") == 1
                and profile_contract is not None
                and parsed.get("generator") == "agentready"
                and isinstance(parsed.get("generator_version"), str)
                and bool(parsed["generator_version"])
                and isinstance(ownership, dict)
                and set(ownership) == {"project_owned", "shared", "generated"}
                and all(
                    isinstance(v, list) and all(isinstance(x, str) for x in v)
                    for v in ownership.values()
                )
            )
            manifest = parsed
        except (OSError, UnicodeError, tomllib.TOMLDecodeError):
            valid = False
    findings.append(
        _finding(
            "manifest.valid",
            valid,
            "manifest is valid" if valid else "manifest is malformed or unsupported",
            manifest_pp,
        )
    )
    ownership_entries: list[ArtifactOwnership] = []
    paths_ok = valid
    if valid:
        expected = {
            cls: set(paths)
            for cls, paths in profile_contract.ownership_paths(  # type: ignore[union-attr]
                project.path.name.replace("-", "_")
            ).items()
        }
        for cls in OwnershipClass:
            for value in manifest["ownership"][cls.value]:  # type: ignore[index]
                try:
                    ownership_entries.append(ArtifactOwnership(ProjectPath(Path(value)), cls))
                except (TypeError, ValueError):
                    paths_ok = False
        if paths_ok:
            actual = {
                cls: {
                    str(item.path.path).replace("\\", "/")
                    for item in ownership_entries
                    if item.ownership is cls
                }
                for cls in OwnershipClass
            }
            paths_ok = all(actual[cls] == expected[cls] for cls in OwnershipClass)
    findings.append(
        _finding(
            "ownership.paths",
            paths_ok,
            "ownership paths are safe" if paths_ok else "ownership contains invalid paths",
        )
    )
    unique = paths_ok and len({a.path for a in ownership_entries}) == len(ownership_entries)
    findings.append(
        _finding(
            "ownership.unique",
            unique,
            (
                "ownership paths are unique"
                if unique
                else "ownership paths overlap or duplicate"
                if paths_ok
                else "ownership uniqueness is unavailable because paths are invalid"
            ),
        )
    )
    artifacts_ok = paths_ok
    missing_artifact: ProjectPath | None = None
    for artifact in ownership_entries:
        _, artifact_path = _safe(project, str(artifact.path.path))
        artifact_ok = artifact_path is not None and artifact_path.is_file()
        if not artifact_ok and missing_artifact is None:
            missing_artifact = artifact.path
        artifacts_ok &= artifact_ok
    findings.append(
        _finding(
            "ownership.artifacts",
            artifacts_ok,
            (
                "declared artifacts exist"
                if artifacts_ok
                else "declared artifact is missing or unsafe"
                if paths_ok
                else "artifact checks are unavailable because ownership paths are invalid"
            ),
            missing_artifact,
        )
    )
    agents_pp, agents_path = _safe(project, "AGENTS.md")
    agents_ok = (
        agents_path is not None
        and agents_path.is_file()
        and any(a.path.path == Path("AGENTS.md") for a in ownership_entries)
    )
    findings.append(
        _finding(
            "guidance.agents",
            agents_ok,
            "AGENTS.md is declared and present"
            if agents_ok
            else "AGENTS.md is missing, unsafe, or undeclared",
            agents_pp,
        )
    )
    refs_ok = agents_ok
    refs: set[str] = set()
    if agents_ok:
        _, agents_text = _read_safe_text(project, "AGENTS.md")
        refs_ok = agents_text is not None
        if agents_text is not None:
            refs.update(_guidance_references(agents_text))
    claude_declared = any(a.path.path == Path("CLAUDE.md") for a in ownership_entries)
    if claude_declared:
        _, claude_text = _read_safe_text(project, "CLAUDE.md")
        if claude_text is None:
            refs_ok = False
        else:
            refs.update(_guidance_references(claude_text))
    broken_reference: ProjectPath | None = None
    for ref in sorted(refs):
        ref_pp, path = _safe(project, ref)
        ref_ok = path is not None and path.is_file()
        if not ref_ok and broken_reference is None:
            broken_reference = ref_pp
        refs_ok &= ref_ok
    findings.append(
        _finding(
            "guidance.references",
            refs_ok,
            "guidance references are safe and present"
            if refs_ok
            else "guidance reference is missing or unsafe",
            broken_reference,
        )
    )
    package = project.path.name.replace("-", "_")
    required = profile_contract.required_paths(package) if profile_contract is not None else ()
    structure_ok = all(_safe_file(project, str(path)) for path in required) and all(
        (project.path / x).is_dir() and not (project.path / x).is_symlink()
        for x in ("src", "tests")
    )
    findings.append(
        _finding(
            "repository.structure",
            structure_ok,
            "repository structure for the selected profile is present"
            if structure_ok
            else "required repository structure is missing or unsafe",
        )
    )
    map_pp, map_text = _read_safe_text(project, "docs/generated/CODEBASE_MAP.md")
    map_ok = profile_contract is not None and validate_codebase_map(
        project.path, package, profile_contract.name, map_text
    )
    findings.append(
        _finding(
            "repository.codebase_map",
            map_ok,
            "codebase map matches module structure"
            if map_ok
            else "codebase map is missing, unsafe, or stale; regenerate it",
            map_pp,
        )
    )
    independence = False
    py_pp, py_path = _safe(project, "pyproject.toml")
    if py_path is not None and py_path.is_file():
        try:
            values = _dependency_values(tomllib.loads(py_path.read_text(encoding="utf-8")))
            independence = values is not None and all(
                (name := _requirement_name(value)) is not None and name != "agentready"
                for value in values
            )
        except (OSError, UnicodeError, tomllib.TOMLDecodeError):
            independence = False
    findings.append(
        _finding(
            "repository.independence",
            independence,
            "no AgentReady dependency is declared"
            if independence
            else "pyproject dependencies are malformed or require AgentReady",
            py_pp,
        )
    )
    work_ok, work_message, work_path = validate_work(project)
    findings.append(_finding("work.registry", work_ok, work_message, work_path))
    prerequisites = all(f.status is FindingStatus.PASS for f in findings[1:])
    findings.append(
        _finding(
            "detach.ready",
            prerequisites,
            "repository is ready for future detach review"
            if prerequisites
            else "detach prerequisites are not satisfied",
        )
    )
    return DoctorReport(tuple(findings))


def format_report(report: DoctorReport) -> str:
    lines = ["AgentReady Doctor"]
    labels = {
        "project": "Project",
        "manifest": "Manifest",
        "ownership": "Ownership",
        "guidance": "Agent guidance",
        "repository": "Repository",
        "work": "Work registry",
        "detach": "Detach readiness",
    }
    current = ""
    for finding in report.findings:
        group = finding.check_id.split(".", 1)[0]
        if group != current:
            current = group
            lines.extend(["", labels[group]])
        suffix = f" [{finding.path.path.as_posix()}]" if finding.path else ""
        lines.append(f"  [{finding.status.value}] {finding.check_id}: {finding.message}{suffix}")
    lines.extend(["", "RESULT", f"  {'HEALTHY' if report.healthy else 'UNHEALTHY'}"])
    return "\n".join(lines)
