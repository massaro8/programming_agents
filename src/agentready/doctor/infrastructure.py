"""Read-only infrastructure inventory checks; never execute repository scripts."""

from __future__ import annotations

import ast
import hashlib
import os
import re
from pathlib import Path

AREAS = (
    "templates",
    "stacks",
    "deployment",
    ".githooks",
    "parameters",
    "policies",
    "scripts",
    ".agents/skills",
    ".claude/skills",
    "docs/work",
    "docs/agent",
    "tests/fixtures",
    "tests/engine",
)


def inventory(root: Path, *, composed: bool = False) -> set[str]:
    paths: set[str] = set()
    areas = ("infrastructure", "docs/infrastructure") if composed else AREAS
    for area in areas:
        base = root / area
        if any(path.is_symlink() or path.is_junction() for path in (base, *base.parents)):
            raise ValueError("unsafe infrastructure inventory")
        for directory, children, files in os.walk(base, followlinks=False):
            children[:] = [
                name
                for name in children
                if name != "__pycache__"
                and not (
                    Path(directory) == root / "docs/work" and name in ("checkpoints", "evidence")
                )
            ]
            for name in (*children, *files):
                path = Path(directory) / name
                if path.is_symlink() or path.is_junction():
                    raise ValueError("unsafe infrastructure inventory")
            for name in files:
                if not name.endswith(".pyc"):
                    paths.add((Path(directory) / name).relative_to(root).as_posix())
            if len(paths) > 10000:
                raise ValueError("infrastructure inventory exceeds 10000 files")
    return paths


def render_map(root: Path) -> str:
    paths = sorted(inventory(root))
    fingerprint = hashlib.sha256("\n".join(paths).encode()).hexdigest()[:12]
    return (
        f"# Codebase Map\n\nStructure fingerprint: `{fingerprint}`\n\n"
        "File-level inventory; regenerate with python scripts/project.py sync.\n\n"
        + "".join(f"- `{path}`\n" for path in paths)
    )


def validate_map(root: Path, text: str | None, *, composed: bool = False) -> bool:
    if text is None or not text.startswith("# Codebase Map\n"):
        return False
    try:
        listed = set(re.findall(r"(?m)^- `([^`]+)`$", text))
        expected = inventory(root, composed=composed)
        return expected <= listed if composed else listed == expected
    except (OSError, ValueError):
        return False


def independent(root: Path) -> bool:
    """Confirm shipped standalone Python tools have no AgentReady imports."""
    try:
        for name in inventory(root):
            if not name.startswith("scripts/") or not name.endswith(".py"):
                continue
            tree = ast.parse((root / name).read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    modules = [alias.name for alias in node.names]
                elif isinstance(node, ast.ImportFrom):
                    modules = [node.module or ""]
                else:
                    continue
                if any(module.split(".")[0] == "agentready" for module in modules):
                    return False
        return not (root / "pyproject.toml").exists()
    except (OSError, UnicodeError, ValueError, SyntaxError):
        return False
