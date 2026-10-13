"""Independent read-only inspection of optional QA, hooks and continuity artifacts."""

from __future__ import annotations

from pathlib import Path

from agentready.continuity import inspect_checkpoints
from agentready.hooks import configuration
from agentready.local_paths import local_path
from agentready.skill_qa import check, claude_view, definition


def validate(root: Path) -> dict[str, tuple[bool, str]]:
    results: dict[str, tuple[bool, str]] = {}
    for identity in ("skills.contract", "skills.evals", "hooks.config", "work.checkpoints"):
        try:
            issues: list[dict[str, str]] = []
            if identity == "skills.contract":
                # Legacy skills remain readable. Contract errors are blocking only for v1
                # repositories that opted into eval artifacts; legacy gaps are advisory.
                issues = check(root)
                for canonical in sorted(local_path(root, ".agents/skills").glob("*/SKILL.md")):
                    view = local_path(root, f".claude/skills/{canonical.parent.name}/SKILL.md")
                    canonical_text = canonical.read_text(encoding="utf-8")
                    actual_view = view.read_text(encoding="utf-8")
                    if local_path(
                        root, "docs/verification.json"
                    ).exists() and actual_view != claude_view(
                        canonical_text, canonical.parent.name
                    ):
                        raise ValueError("Claude skill view drift; regenerate from canonical skill")
                if not any(local_path(root, ".agents/skills").glob("*/evals/cases.json")):
                    issues = [
                        {**issue, "severity": "WARNING"}
                        if issue["message"].startswith("missing or empty")
                        else issue
                        for issue in issues
                    ]
            elif identity == "skills.evals":
                for path in sorted(local_path(root, ".agents/skills").glob("*/evals/cases.json")):
                    definition(root, path.parent.parent.name)
            elif identity == "hooks.config":
                data = configuration(root)
                for name, recipe in data["hooks"].items():
                    if recipe["enabled"] and not local_path(root, "scripts/hooks.py").is_file():
                        raise ValueError(f"enabled {name} missing local implementation")
            else:
                from agentready.verification import config
                from agentready.verification import validate as validate_evidence

                if local_path(root, "docs/verification.json").exists():
                    config(root)
                    for work in sorted(local_path(root, "docs/work").glob("W*-*.md")):
                        text = work.read_text(encoding="utf-8")
                        if "Status: DONE\n" in text and "Verification evidence: REQUIRED" in text:
                            validate_evidence(root, work.name.split("-", 1)[0], fresh=False)
                issues = inspect_checkpoints(root)
            errors = [v for v in issues if v["severity"] == "ERROR"]
            message = "; ".join(f"{v['severity']}: {v['message']} [{v['path']}]" for v in issues)
            results[identity] = (not errors, message or "valid (optional artifacts may be absent)")
        except (OSError, UnicodeError, ValueError, TypeError):
            results[identity] = (False, f"ERROR: {identity} malformed, missing, or unsafe")
    return results
