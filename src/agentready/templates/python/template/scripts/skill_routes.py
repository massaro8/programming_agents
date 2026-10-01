"""Deterministic work-type to skill and required-context routes."""

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
