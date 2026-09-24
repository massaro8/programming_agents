#!/usr/bin/env python3
"""Generate a compact deterministic repository navigation map.

The map is intentionally structural. It helps an agent decide where to look; it does not duplicate
source code or describe every symbol.
"""

from __future__ import annotations

import argparse
import hashlib
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "generated" / "CODEBASE_MAP.md"
OUTPUT_REL = OUTPUT.relative_to(ROOT).as_posix()


def tracked_files() -> list[str]:
    """Return tracked and untracked, non-ignored repository files deterministically."""
    try:
        result = subprocess.run(
            ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        files = [line for line in result.stdout.splitlines() if line and (ROOT / line).is_file()]
    except (subprocess.CalledProcessError, FileNotFoundError):
        excluded = {
            ".git",
            ".venv",
            "__pycache__",
            ".mypy_cache",
            ".pytest_cache",
            ".ruff_cache",
        }
        files = []
        for path in ROOT.rglob("*"):
            if path.is_file() and not any(part in excluded for part in path.parts):
                files.append(path.relative_to(ROOT).as_posix())

    return sorted(set(files))


def structure_fingerprint(files: list[str]) -> str:
    """Fingerprint only the structural file list, avoiding self-referential Git commit hashes."""
    structural = [file for file in files if file != OUTPUT_REL]
    payload = "\n".join(structural).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:12]


def render(files: list[str]) -> str:
    groups: dict[str, list[str]] = {}
    for file in files:
        top = file.split("/", 1)[0]
        groups.setdefault(top, []).append(file)

    lines = [
        "# Codebase Map",
        "",
        f"Structure fingerprint: `{structure_fingerprint(files)}`",
        "",
        "Do not edit manually. Regenerate with `python scripts/generate_codebase_map.py`.",
        "",
        "## Primary entry points",
        "",
        "- CLI: `src/agentready/cli.py:main`",
        "- Shared agent policy: `AGENTS.md`",
        "- Product scope: `docs/PRODUCT_SPEC.md`",
        "- Architecture: `docs/ARCHITECTURE.md`",
        "- Roadmap: `docs/ROADMAP.md`",
        "- Detachment contract: `docs/DETACHMENT_CONTRACT.md`",
        "",
        "## Repository areas",
        "",
    ]

    for group in sorted(groups):
        lines.append(f"### `{group}`")
        for file in groups[group]:
            lines.append(f"- `{file}`")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    content = render(tracked_files())
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != content:
            print(f"{OUTPUT.relative_to(ROOT)} is stale")
            return 1
        print("CODEBASE_MAP is current")
        return 0

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(content, encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
