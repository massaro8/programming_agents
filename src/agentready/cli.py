"""CLI entry point for project generation and deterministic diagnostics."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from agentready import __version__
from agentready.core.profiles import DEFAULT_PROFILE, SUPPORTED_PROFILES
from agentready.detach.service import DetachError, detach_project
from agentready.doctor.inspector import format_report, inspect
from agentready.doctor.serialization import serialize_report
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
    init_parser.add_argument(
        "--profile",
        choices=SUPPORTED_PROFILES,
        default=DEFAULT_PROFILE,
        help="project structure profile (default: minimal)",
    )
    doctor_parser = subparsers.add_parser("doctor", help="inspect a repository")
    doctor_parser.add_argument("path", nargs="?", type=Path, default=Path("."))
    doctor_parser.add_argument("--format", choices=("human", "json"), default="human")
    detach_parser = subparsers.add_parser("detach", help="remove AgentReady maintenance metadata")
    detach_parser.add_argument("path", nargs="?", type=Path, default=Path("."))
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "init":
        try:
            generate_project(args.target, profile=args.profile)
        except (GeneratorError, TypeError) as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        print(f"Created project at {args.target}")
        return 0
    if args.command == "doctor":
        report = inspect(args.path)
        if args.format == "json":
            print(serialize_report(report, args.path), end="")
        else:
            print(format_report(report))
        return 0 if report.healthy else 1
    if args.command == "detach":
        try:
            detach_project(args.path)
        except (DetachError, TypeError, OSError) as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        print(f"Detached AgentReady metadata from {args.path}")
        return 0
    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
