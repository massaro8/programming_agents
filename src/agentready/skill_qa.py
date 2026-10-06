"""Portable Skill Contract v1 validation and external-result evaluation; no agent runtime."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from agentready.local_paths import local_path, read_json, read_text

SECTIONS = {
    "purpose": ("Purpose",),
    "triggers": ("Positive triggers",),
    "exclusions": ("Exclusions", "Negative triggers"),
    "scope": ("Scope", "Inputs and preconditions"),
    "process": ("Process", "Procedure"),
    "verification": ("Verification", "Evidence of completion"),
    "failure": ("Failure / escalation", "Escalate or stop"),
    "output": ("Output contract",),
}


def skill_path(name: str) -> str:
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
        raise ValueError("invalid skill name")
    return f".agents/skills/{name}/SKILL.md"


def check(root: Path, name: str | None = None) -> list[dict[str, str]]:
    base = local_path(root, ".agents/skills")
    paths = (
        [skill_path(name)]
        if name
        else [p.relative_to(root.absolute()).as_posix() for p in sorted(base.glob("*/SKILL.md"))]
    )
    if not paths:
        raise ValueError("no canonical skills found")
    issues: list[dict[str, str]] = []
    identities: set[str] = set()
    descriptions: set[str] = set()
    for relative in paths:

        def issue(severity: str, message: str, path: str = relative) -> None:
            issues.append({"severity": severity, "message": message, "path": path})

        try:
            text = read_text(root, relative)
            metadata = re.match(r"\A---\n(.*?)\n---\n", text, re.S)
            if metadata is None:
                issue("ERROR", "malformed skill frontmatter")
                continue
            fields = metadata.group(1)
            for field in ("name", "description"):
                values = re.findall(rf"^{field}:[ \t]*(\S[^\n]*)$", fields, re.M)
                if len(values) != 1:
                    issue("ERROR", f"missing or duplicate {field}")
                    continue
                value = values[0].strip()
                if field == "name":
                    if value in identities or value != Path(relative).parent.name:
                        issue("ERROR", "duplicate identity or name/path conflict")
                    identities.add(value)
                else:
                    if value.lower() in descriptions:
                        issue("WARNING", "overlapping skill description")
                    descriptions.add(value.lower())
            if len(fields) > 1024:
                issue("INFO", "always-loaded metadata exceeds recommended 1024 characters")
            body = text[metadata.end() :]
            headings = re.findall(r"^## (.+)$", body, re.M)
            if len(headings) != len(set(headings)):
                issue("ERROR", "duplicate skill section")
            for concept, aliases in SECTIONS.items():
                matches = [
                    re.search(rf"^## {re.escape(alias)}\s*\n(.*?)(?=^## |\Z)", body, re.M | re.S)
                    for alias in aliases
                ]
                present = any(m and m.group(1).strip() for m in matches)
                if not present:
                    issue(
                        "WARNING" if concept == "exclusions" else "ERROR",
                        f"missing or empty {concept} section",
                    )
            for target in re.findall(r"\]\(([^)]+)\)", body):
                target = target.strip("<>").split("#", 1)[0]
                if not target or target.startswith(("https://", "http://", "mailto:")):
                    continue
                # Existing SKILL.md links are relative to their skill directory.
                candidate = Path(relative).parent / target
                resolved = (root.absolute() / candidate).resolve()
                rel = resolved.relative_to(root.absolute()).as_posix()
                # Resolve lexical .. but inspect the original traversal for unsafe links.
                cursor = root.absolute() / Path(relative).parent
                for part in Path(target).parts:
                    cursor /= part
                    if cursor.is_symlink() or cursor.is_junction():
                        raise ValueError("unsafe reference")
                if not local_path(root, rel).is_file():
                    issue("ERROR", "broken skill reference")
        except (OSError, UnicodeError, ValueError):
            issue("ERROR", "skill or reference is missing, malformed, or unsafe")
    return issues


def definition(root: Path, name: str) -> dict[str, Any]:
    """Validate a portable JSON eval definition, not natural-language trigger semantics."""
    skill_path(name)
    data = read_json(root, f".agents/skills/{name}/evals/cases.json")
    if set(data) != {"schema", "skill", "include", "exclude", "cases"}:
        raise ValueError("unexpected eval fields")
    if type(data["schema"]) is not int or data["schema"] != 1 or data["skill"] != name:
        raise ValueError("unsupported eval identity/schema")
    for field in ("include", "exclude"):
        if not isinstance(data[field], list) or not all(
            isinstance(v, str) and v.strip() for v in data[field]
        ):
            raise ValueError("trigger terms must be nonempty strings")
    if not data["include"] or not isinstance(data["cases"], list) or not data["cases"]:
        raise ValueError("eval requires include terms and cases")
    seen: set[str] = set()
    for case in data["cases"]:
        if not isinstance(case, dict) or set(case) != {"id", "task", "trigger", "criteria"}:
            raise ValueError("invalid eval case")
        if not isinstance(case["id"], str) or not re.fullmatch(r"[a-z0-9-]+", case["id"]):
            raise ValueError("invalid case ID")
        if case["id"] in seen:
            raise ValueError("duplicate case ID")
        seen.add(case["id"])
        if not isinstance(case["task"], str) or not case["task"].strip():
            raise ValueError("case requires task")
        if not isinstance(case["trigger"], bool) or not isinstance(case["criteria"], list):
            raise ValueError("invalid expected trigger or criteria")
        if not all(
            isinstance(v, str) and re.fullmatch(r"[a-z0-9_-]+", v) for v in case["criteria"]
        ) or len(case["criteria"]) != len(set(case["criteria"])):
            raise ValueError("criteria must be unique observable IDs")
    return data


def evaluate(
    root: Path, name: str, case_id: str | None = None, results: str | None = None
) -> dict[str, Any]:
    data = definition(root, name)
    cases = [c for c in data["cases"] if case_id is None or c["id"] == case_id]
    if not cases:
        raise ValueError("unknown eval case")
    execution = read_json(root, results) if results else None
    if execution is not None:
        if set(execution) != {"schema", "skill", "variant", "cases"} or (
            execution["schema"] != 1
            or execution["skill"] != name
            or execution["variant"] not in ("with-skill", "without-skill")
            or not isinstance(execution["cases"], dict)
        ):
            raise ValueError("invalid external results")
        expected = {c["id"]: c for c in data["cases"]}
        for identity, observations in execution["cases"].items():
            if identity not in expected or not isinstance(observations, dict):
                raise ValueError("unknown result case")
            if set(observations) - set(expected[identity]["criteria"]):
                raise ValueError("unknown observable criterion")
            for observed in observations.values():
                if not isinstance(observed, dict) or set(observed) != {"passed", "evidence"}:
                    raise ValueError("criterion requires passed and evidence")
                if not isinstance(observed["passed"], bool) or not isinstance(
                    observed["evidence"], str
                ):
                    raise ValueError("invalid criterion result")
                if observed["passed"] and not observed["evidence"].strip():
                    raise ValueError("passing observation requires evidence")
    scored = []
    for case in cases:
        task = case["task"].casefold()
        actual = any(term.casefold() in task for term in data["include"]) and not any(
            term.casefold() in task for term in data["exclude"]
        )
        observations = execution["cases"].get(case["id"], {}) if execution else {}
        criteria = {
            key: observations.get(key, {"passed": False, "evidence": "MISSING"})
            for key in case["criteria"]
        }
        scored.append(
            {
                "id": case["id"],
                "trigger_passed": actual == case["trigger"],
                "criteria": criteria,
                "score": sum(v["passed"] for v in criteria.values()),
                "total": len(criteria),
            }
        )
    return {
        "schema": 1,
        "skill": name,
        "scope": "lexical contract fixtures; external observations",
        "variant": execution["variant"] if execution else None,
        "cases": scored,
        "passed": all(
            c["trigger_passed"] and (execution is None or c["score"] == c["total"]) for c in scored
        ),
    }


def main(argv: list[str] | None = None, root: Path | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    lint = sub.add_parser("check")
    lint.add_argument("name", nargs="?")
    eval_parser = sub.add_parser("eval")
    eval_parser.add_argument("name")
    eval_parser.add_argument("--case")
    eval_parser.add_argument("--results")
    for p in (lint, eval_parser):
        p.add_argument("--format", choices=("human", "json"), default="human")
    args = parser.parse_args(argv)
    root = root or Path(__file__).resolve().parents[1]
    try:
        if args.action == "check":
            issues = check(root, args.name)
            payload = {
                "schema": 1,
                "issues": issues,
                "passed": not any(v["severity"] == "ERROR" for v in issues),
            }
        else:
            payload = evaluate(root, args.name, args.case, args.results)
        print(json.dumps(payload, indent=2) if args.format == "json" else str(payload))
        return 0 if payload["passed"] else 1
    except (ValueError, OSError, UnicodeError) as exc:
        print(f"skill QA: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
