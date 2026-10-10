from __future__ import annotations

import json
import runpy
from pathlib import Path
from types import SimpleNamespace

import pytest

SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "src/agentready/templates/python/template/scripts/skill_routes.py"
)
ROUTER = SimpleNamespace(**runpy.run_path(str(SCRIPT)))


@pytest.mark.parametrize(
    ("work_type", "complexity", "signals", "unknown", "status", "expected"),
    [
        (
            "DOCS",
            "TRIVIAL",
            (),
            False,
            None,
            ("documentation", "none", "changed-file", "none", "targeted-check"),
        ),
        (
            "FEATURE",
            "LOCAL",
            (),
            False,
            "READY",
            (
                "feature-builder",
                "micro-plan",
                "module-and-tests",
                "none",
                "targeted-tests-and-checks",
            ),
        ),
        (
            "FEATURE",
            "CROSS_MODULE",
            (),
            True,
            "READY",
            (
                "feature-builder",
                "bounded-plan",
                "affected-boundaries-and-contracts",
                "consider-read-only-explorer",
                "affected-contracts-and-integration",
            ),
        ),
        *[
            (
                "FEATURE",
                "LOCAL",
                (signal,),
                False,
                "READY",
                (
                    "feature-builder",
                    "failure-and-rollback-plan",
                    "module-and-tests-plus-risk-contracts",
                    "none",
                    "risk-regressions-and-relevant-broad-gates",
                ),
            )
            for signal in ("auth", "migration", "concurrency")
        ],
        (
            "REFACTOR",
            "ARCHITECTURAL",
            (),
            False,
            None,
            (
                "refactoring",
                "design-plan",
                "architecture-and-affected-contracts",
                "none",
                "boundary-and-regression-gates",
            ),
        ),
        (
            "BUGFIX",
            "LOCAL",
            (),
            False,
            None,
            (
                "bug-investigation",
                "micro-plan",
                "module-and-tests",
                "none",
                "targeted-tests-and-checks",
            ),
        ),
        (
            "FEATURE",
            "LOCAL",
            (),
            False,
            "IN_PROGRESS",
            (
                "feature-builder",
                "micro-plan",
                "module-and-tests",
                "none",
                "targeted-tests-and-checks",
            ),
        ),
    ],
)
def test_required_routing_cases(work_type, complexity, signals, unknown, status, expected):
    result = ROUTER.recommend(
        work_type, complexity, risk_signals=signals, unknown_area=unknown, work_status=status
    )
    assert (
        tuple(result[key] for key in ("skill", "plan", "context", "subagent", "validation"))
        == expected
    )
    assert result["risk"] == ("HIGH" if signals else "NORMAL")
    if signals:
        assert result["review"] == "specialist-review"
        assert result["model_class"] == "STRONG"
    if work_type == "FEATURE":
        assert result["feature_workflow_allowed"] is True
    if unknown:
        assert result["context_start"] == "CODEBASE_MAP-and-search"


def test_parallel_exploration_requires_unknown_independent_domains():
    assert ROUTER.recommend("FEATURE", independent_domains=3)["subagent"] == "none"
    assert (
        ROUTER.recommend("FEATURE", unknown_area=True, independent_domains=1)["subagent"]
        == "consider-read-only-explorer"
    )
    assert (
        ROUTER.recommend("FEATURE", unknown_area=True, independent_domains=2)["subagent"]
        == "consider-scoped-parallel-explorers"
    )


def test_recommendation_preserves_feature_approval_and_explicit_high_risk():
    result = ROUTER.recommend("FEATURE", "TRIVIAL", risk="HIGH", work_status="BACKLOG")
    assert result["feature_workflow_allowed"] is False
    assert result["model_class"] == "STRONG"
    assert result["plan"] == "failure-and-rollback-plan"
    assert ROUTER.recommend("SECURITY")["risk"] == "HIGH"


def test_cli_json_is_deterministic(capsys):
    args = ["BUGFIX", "--risk-signal", "concurrency", "--format", "json"]
    assert ROUTER.main(args) == 0
    first = capsys.readouterr().out
    assert ROUTER.main(args) == 0
    assert capsys.readouterr().out == first
    assert json.loads(first)["skill"] == "bug-investigation"


@pytest.mark.parametrize(
    "kwargs",
    [
        {"complexity": "INVALID"},
        {"risk": "INVALID"},
        {"risk_signals": ("unknown",)},
        {"independent_domains": -1},
    ],
)
def test_invalid_structured_signals_are_rejected(kwargs):
    with pytest.raises(ValueError):
        ROUTER.recommend("FEATURE", **kwargs)
