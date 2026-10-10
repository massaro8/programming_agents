"""Deterministic work-type to skill and required-context routes."""

from __future__ import annotations

import argparse
import json

EXPECTED_SKILLS = (
    "bug-investigation",
    "documentation",
    "feature-builder",
    "maintenance",
    "module-placement",
    "refactoring",
    "repo-explore",
    "security-review",
)

ROUTES = {
    "FEATURE": {
        "skill": "feature-builder",
        "workflow": "docs/agent/workflows/feature.md",
        "standards": ("docs/agent/standards/architecture.md", "docs/agent/standards/testing.md"),
    },
    "BUGFIX": {
        "skill": "bug-investigation",
        "workflow": "docs/agent/workflows/bugfix.md",
        "standards": ("docs/agent/standards/testing.md",),
    },
    "REFACTOR": {
        "skill": "refactoring",
        "workflow": "docs/agent/workflows/refactor.md",
        "standards": ("docs/agent/standards/architecture.md", "docs/agent/standards/testing.md"),
    },
    "MAINTENANCE": {
        "skill": "maintenance",
        "workflow": "docs/agent/workflows/maintenance.md",
        "standards": ("docs/agent/standards/dependencies.md",),
    },
    "DOCS": {
        "skill": "documentation",
        "workflow": "docs/agent/workflows/documentation.md",
        "standards": ("docs/agent/standards/documentation.md",),
    },
    "SECURITY": {
        "skill": "security-review",
        "workflow": "docs/agent/workflows/security.md",
        "standards": ("docs/agent/standards/security.md",),
    },
}

SECURITY_MODES = {
    "review-only": {"ready_item_required": False, "production_edits_allowed": False},
    "implementation": {"ready_item_required": True, "production_edits_allowed": True},
}

COMPLEXITIES = ("TRIVIAL", "LOCAL", "CROSS_MODULE", "ARCHITECTURAL")
RISK_SIGNALS = (
    "security",
    "auth",
    "permissions",
    "money",
    "payments",
    "migration",
    "concurrency",
    "secrets",
    "infrastructure",
    "destructive-data",
)


def recommend(
    work_type: str,
    complexity: str = "LOCAL",
    risk: str = "NORMAL",
    risk_signals: tuple[str, ...] = (),
    unknown_area: bool = False,
    independent_domains: int = 0,
    work_status: str | None = None,
) -> dict[str, object]:
    """Recommend a bounded workflow from explicit signals; execute nothing."""
    if work_type not in ROUTES:
        raise ValueError(f"unsupported work type: {work_type}")
    if complexity not in COMPLEXITIES or risk not in ("NORMAL", "HIGH"):
        raise ValueError("invalid complexity or risk")
    if any(signal not in RISK_SIGNALS for signal in risk_signals):
        raise ValueError("unsupported risk signal")
    if independent_domains < 0:
        raise ValueError("independent domains must be nonnegative")
    if work_status not in (None, "BACKLOG", "READY", "IN_PROGRESS", "BLOCKED", "DONE"):
        raise ValueError("unsupported work status")
    high_risk = risk == "HIGH" or bool(risk_signals) or work_type == "SECURITY"
    level = COMPLEXITIES.index(complexity)
    plan = ("none", "micro-plan", "bounded-plan", "design-plan")[level]
    context = (
        "changed-file",
        "module-and-tests",
        "affected-boundaries-and-contracts",
        "architecture-and-affected-contracts",
    )[level]
    validation = (
        "targeted-check",
        "targeted-tests-and-checks",
        "affected-contracts-and-integration",
        "boundary-and-regression-gates",
    )[level]
    review = "self-review"
    model_class = ("FAST", "FAST", "BALANCED", "STRONG")[level]
    if high_risk:
        plan = "failure-and-rollback-plan"
        validation = "risk-regressions-and-relevant-broad-gates"
        review = "specialist-review"
        model_class = "STRONG"
        context = f"{context}-plus-risk-contracts"
    elif complexity == "ARCHITECTURAL":
        review = "architecture-review"
    subagent = "none"
    if unknown_area:
        subagent = "consider-read-only-explorer"
        if independent_domains >= 2:
            subagent = "consider-scoped-parallel-explorers"
    route = ROUTES[work_type]
    return {
        "work_type": work_type,
        "complexity": complexity,
        "risk": "HIGH" if high_risk else "NORMAL",
        "risk_signals": sorted(set(risk_signals)),
        "skill": route["skill"],
        "workflow": route["workflow"],
        "standards": list(route["standards"]),
        "plan": plan,
        "context": context,
        "context_start": "CODEBASE_MAP-and-search" if unknown_area else "relevant-paths",
        "subagent": subagent,
        "validation": validation,
        "review": review,
        "model_class": model_class,
        "work_status": work_status,
        "feature_workflow_allowed": (
            work_status in ("READY", "IN_PROGRESS") if work_type == "FEATURE" else None
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("work_type", choices=tuple(ROUTES))
    parser.add_argument("--complexity", choices=COMPLEXITIES, default="LOCAL")
    parser.add_argument("--risk", choices=("NORMAL", "HIGH"), default="NORMAL")
    parser.add_argument("--risk-signal", choices=RISK_SIGNALS, action="append", default=[])
    parser.add_argument("--unknown-area", action="store_true")
    parser.add_argument("--independent-domains", type=int, default=0)
    parser.add_argument(
        "--work-status", choices=("BACKLOG", "READY", "IN_PROGRESS", "BLOCKED", "DONE")
    )
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args(argv)
    try:
        result = recommend(
            args.work_type,
            args.complexity,
            args.risk,
            tuple(args.risk_signal),
            args.unknown_area,
            args.independent_domains,
            args.work_status,
        )
    except ValueError as exc:
        parser.error(str(exc))
    if args.format == "json":
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        for key, value in result.items():
            print(f"{key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
