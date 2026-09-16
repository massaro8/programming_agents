"""CLI entry point.

The `init` command is implemented; `doctor` and `detach` remain deferred per the product roadmap.
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from agentready import __version__
from agentready.render.generator import GeneratorError, generate_project


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="agentready",
        description="Detachable repository engineering layer for coding agents.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"agentready {__version__}",
    )
    subparsers = parser.add_subparsers(dest="command")
    init_parser = subparsers.add_parser("init", help="create a trusted Python project")
    init_parser.add_argument("target", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "init":
        try:
            generate_project(args.target)
        except (GeneratorError, TypeError) as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        print(f"Created project at {args.target}")
        return 0
    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
