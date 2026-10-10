"""Bounded durable Wxxx checkpoints with read-only staleness detection."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
from contextlib import nullcontext
from pathlib import Path
from typing import Any

from agentready.local_paths import (
    durable_text,
    local_path,
    read_json,
    read_text,
    repository_write,
    write_json,
)

FIELDS = {"objective", "files", "decisions", "validation", "risks", "questions", "next_step"}


def git_executable(root: Path) -> str | None:
    """Resolve native Git before changing cwd; never invoke a repository-local executable."""
    candidate = shutil.which("git")
    if candidate is None:
        return None
    path = Path(candidate).resolve()
    if path.is_relative_to(root.absolute()):
        return None
    return str(path)


def work(root: Path, work_id: str) -> dict[str, str]:
    if not re.fullmatch(r"W[0-9]{3,}", work_id) or int(work_id[1:]) < 1:
        raise ValueError("invalid work ID")
    matches = sorted(local_path(root, "docs/work").glob(f"{work_id}-*.md"))
    if len(matches) != 1:
        raise ValueError("work item missing or ambiguous")
    relative = matches[0].relative_to(root.absolute()).as_posix()
    text = read_text(root, relative)
    header = re.match(rf"# {work_id} — (.+)\n\nType: ([A-Z]+)\nStatus: ([A-Z_]+)\n", text)
    if header is None or header[3] not in ("BACKLOG", "READY", "IN_PROGRESS", "BLOCKED", "DONE"):
        raise ValueError("malformed work item")
    return {"work_id": work_id, "title": header[1], "status": header[3], "path": relative}


def revision(root: Path) -> str | None:
    executable = git_executable(root)
    if executable is None:
        return None
    try:
        result = subprocess.run(
            [executable, "rev-parse", "HEAD"],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
            timeout=10,
        )
        return result.stdout.strip() if result.returncode == 0 else None
    except (OSError, subprocess.TimeoutExpired):
        return None


def digest(root: Path, relative: str) -> str:
    path = local_path(root, relative)
    if not path.is_file():
        raise ValueError("checkpoint file is missing")
    hasher = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(65536), b""):
            hasher.update(block)
    return hasher.hexdigest()


def tracked_digest(root: Path) -> str | None:
    """Track committed/indexed files, including dirty content, without storing it."""
    executable = git_executable(root)
    if executable is None:
        return None
    try:
        result = subprocess.run(
            [executable, "ls-files", "-z"], cwd=root, capture_output=True, check=False, timeout=10
        )
        if result.returncode:
            return None
        names = result.stdout.decode("utf-8").split("\0")
        hashes = []
        for name in sorted(set(names)):
            if not name or name.startswith(("docs/work/checkpoints/", "docs/work/evidence/")):
                continue
            try:
                value = digest(root, name)
            except (OSError, ValueError):
                value = "MISSING_OR_UNSAFE"
            hashes.append(f"{name}:{value}")
        return hashlib.sha256("\n".join(hashes).encode()).hexdigest()
    except (OSError, UnicodeError, subprocess.TimeoutExpired):
        return None


def validate_state(state: dict[str, Any]) -> None:
    if set(state) != FIELDS:
        raise ValueError(
            "state requires objective, files, decisions, validation, risks, questions, next_step"
        )
    for key in ("objective", "next_step"):
        durable_text(state[key])
    for key in FIELDS - {"objective", "next_step"}:
        values = state[key]
        if not isinstance(values, list) or len(values) > 50:
            raise ValueError("state lists may contain at most 50 summaries")
        for value in values:
            durable_text(value)


def checkpoint(
    root: Path,
    work_id: str,
    state: dict[str, Any] | None = None,
    *,
    replace: bool = False,
    dry_run: bool = False,
) -> dict[str, Any]:
    item = work(root, work_id)
    if item["status"] == "DONE":
        raise ValueError("DONE work item cannot create a continuation checkpoint")
    state = (
        state
        if state is not None
        else {
            "objective": item["title"],
            "next_step": "Review the current work specification",
            "files": [],
            "decisions": [],
            "validation": [],
            "risks": [],
            "questions": [],
        }
    )
    validate_state(state)
    files = sorted(set([item["path"], *state["files"]]))
    hashes = {name: digest(root, name) for name in files}
    data = {
        "schema": 1,
        "work_id": work_id,
        "status": item["status"],
        "state": state,
        "revision": revision(root),
        "tracked_digest": tracked_digest(root),
        "hashes": hashes,
    }
    relative = f"docs/work/checkpoints/{work_id}.json"
    with repository_write(root, relative) if not dry_run else nullcontext():
        if local_path(root, relative).exists() and not replace:
            raise ValueError("checkpoint already exists; use --replace explicitly")
        if not dry_run:
            write_json(root, relative, data)
    return data


def resume(root: Path, work_id: str) -> dict[str, Any]:
    item = work(root, work_id)
    data = read_json(root, f"docs/work/checkpoints/{work_id}.json")
    if set(data) != {
        "schema",
        "work_id",
        "status",
        "state",
        "revision",
        "tracked_digest",
        "hashes",
    }:
        raise ValueError("malformed checkpoint fields")
    if data["schema"] != 1 or data["work_id"] != work_id or not isinstance(data["state"], dict):
        raise ValueError("unsupported checkpoint")
    validate_state(data["state"])
    if data["status"] not in ("BACKLOG", "READY", "IN_PROGRESS", "BLOCKED"):
        raise ValueError("invalid checkpoint status")
    for key in ("revision", "tracked_digest"):
        if data[key] is not None and not isinstance(data[key], str):
            raise ValueError("invalid checkpoint revision/digest")
    hashes = data["hashes"]
    if not isinstance(hashes, dict) or set(hashes) != {item["path"], *data["state"]["files"]}:
        raise ValueError("invalid checkpoint file inventory")
    warnings: list[str] = []
    if item["status"] == "DONE":
        warnings.append("work item is DONE; no continuation is actionable")
    elif item["status"] != data["status"]:
        warnings.append("work status changed")
    if revision(root) != data["revision"]:
        warnings.append("repository revision changed")
    if tracked_digest(root) != data["tracked_digest"]:
        warnings.append("tracked files changed; previous validation must be reviewed")
    for relative, expected in sorted(hashes.items()):
        if not isinstance(expected, str) or not re.fullmatch(r"[a-f0-9]{64}", expected):
            raise ValueError("invalid checkpoint file hash")
        try:
            if digest(root, relative) != expected:
                warnings.append(f"file changed: {relative}; previous validation may be stale")
        except (OSError, ValueError):
            warnings.append(f"file missing or unsafe: {relative}")
    return {
        "schema": 1,
        "work": item,
        "state": data["state"],
        "checkpoint_revision": data["revision"],
        "stale": bool(warnings),
        "warnings": warnings,
        "actionable": item["status"] != "DONE",
        "authority": "code/tests/config > accepted decisions > work item > checkpoint",
    }


def inspect_checkpoints(root: Path) -> list[dict[str, str]]:
    issues = []
    base = local_path(root, "docs/work/checkpoints")
    for path in sorted(base.glob("*.json")):
        try:
            result = resume(root, path.stem)
            if result["stale"]:
                issues.append(
                    {
                        "severity": "WARNING",
                        "message": "; ".join(result["warnings"]),
                        "path": path.relative_to(root.absolute()).as_posix(),
                    }
                )
        except (OSError, UnicodeError, ValueError):
            issues.append(
                {
                    "severity": "ERROR",
                    "message": "checkpoint is malformed or orphaned",
                    "path": path.relative_to(root.absolute()).as_posix(),
                }
            )
    return issues


def main(argv: list[str] | None = None, root: Path | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="action", required=True)
    create = commands.add_parser("checkpoint")
    create.add_argument("work_id")
    create.add_argument("--state", help="repository-relative JSON state file")
    create.add_argument("--replace", action="store_true")
    create.add_argument("--dry-run", action="store_true")
    view = commands.add_parser("resume")
    view.add_argument("work_id")
    for p in (create, view):
        p.add_argument("--format", choices=("human", "json"), default="human")
    args = parser.parse_args(argv)
    root = root or Path(__file__).resolve().parents[1]
    try:
        if args.action == "checkpoint":
            state = read_json(root, args.state) if args.state else None
            payload = checkpoint(
                root, args.work_id, state, replace=args.replace, dry_run=args.dry_run
            )
        else:
            payload = resume(root, args.work_id)
        if args.format == "json":
            print(json.dumps(payload, indent=2))
        else:
            for key, value in payload.items():
                print(f"{key}: {json.dumps(value, ensure_ascii=False)}")
        return 0
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"work continuity: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
