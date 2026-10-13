"""Repository-local verification receipts; evidence is not a security attestation."""

from __future__ import annotations

import hashlib
import json
import math
import os
import platform
import re
import shutil
import subprocess
import tempfile
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

from agentready.local_paths import MAX_BYTES, local_path, read_json, repository_write


class VerificationError(ValueError):
    """Missing, failed, or stale verification evidence."""


def safe(root: Path, relative: str) -> Path:
    try:
        return local_path(root, relative)
    except ValueError as exc:
        raise VerificationError(f"unsafe verification path: {relative}") from exc


def config(root: Path) -> dict[str, Any]:
    try:
        value = read_json(root, "docs/verification.json")
        max_age = value.get("max_age_seconds", 0)
        if (
            value.get("schema_version") != 1
            or not isinstance(max_age, (int, float))
            or isinstance(max_age, bool)
            or not math.isfinite(max_age)
            or max_age <= 0
        ):
            raise ValueError("unsupported verification configuration")
        stages = value["required_stages"]
        if not isinstance(stages, dict) or not stages.get("default"):
            raise ValueError("required_stages.default must be nonempty")
        for entries in stages.values():
            if (
                not isinstance(entries, list)
                or not entries
                or any(not isinstance(entry, str) or not entry for entry in entries)
            ):
                raise ValueError("invalid required stages")
        return value
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
        raise VerificationError(f"invalid verification configuration: {exc}") from exc


def receipt_path(root: Path, work_id: str) -> Path:
    if not re.fullmatch(r"W[0-9]{3,}", work_id):
        raise VerificationError("invalid verification work ID")
    return safe(root, f"docs/verification/{work_id}.json")


def snapshot(root: Path, work_id: str) -> dict[str, str]:
    ignored = {
        ".git",
        ".venv",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        "dist",
        "build",
        ".agentready",
    }
    result: dict[str, str] = {}
    total_bytes = 0
    for directory, dirs, files in os.walk(root, followlinks=False):
        parent = Path(directory)
        kept = []
        for name in sorted(dirs):
            path = parent / name
            relative = path.relative_to(root).as_posix()
            if name in ignored or relative in {"docs/verification", "docs/work/checkpoints"}:
                continue
            safe(root, relative)
            kept.append(name)
        dirs[:] = kept
        for filename in sorted(files):
            path = parent / filename
            name = path.relative_to(root).as_posix()
            if name in {
                "docs/work/index.md",
                "docs/changelog/index.md",
                "docs/generated/CODEBASE_MAP.md",
            }:
                continue
            if name.startswith("docs/work/W") and not path.name.startswith(work_id + "-"):
                continue
            safe(root, name)
            total_bytes += path.stat().st_size
            if len(result) >= 10000 or total_bytes > 100_000_000:
                raise VerificationError("verification input limit exceeded (10000 files / 100 MB)")
            data = path.read_bytes()
            if name.startswith("docs/work/" + work_id + "-"):
                text = data.decode("utf-8")
                text = re.sub(r"^Status:.*$", "Status: <lifecycle>", text, flags=re.M)
                # Completion prose is validated separately; preserve accepted specification.
                text = re.split(r"^## Implementation record\s*$", text, maxsplit=1, flags=re.M)[0]
                data = text.encode("utf-8")
            result[name] = hashlib.sha256(data).hexdigest()
    return result


def tool_identity(commands: list[dict[str, Any]], root: Path) -> dict[str, str]:
    identities = {"python": platform.python_version()}
    for entry in commands:
        executable = entry["command"][0]
        resolved = shutil.which(executable)
        if resolved:
            stat = Path(resolved).stat()
            identities[executable] = f"{resolved}:{stat.st_size}:{stat.st_mtime_ns}"
            name = Path(resolved).stem.lower()
            if name in {
                "uv",
                "python",
                "python3",
                "ruff",
                "mypy",
                "cfn-lint",
                "cfn-guard",
            } and not Path(resolved).resolve().is_relative_to(root.absolute()):
                try:
                    version = subprocess.run(
                        [resolved, "--version"],
                        cwd=Path(resolved).parent,
                        capture_output=True,
                        text=True,
                        check=False,
                        timeout=5,
                    )
                    if version.returncode == 0:
                        identities[f"version:{executable}"] = (
                            version.stdout + version.stderr
                        ).strip()[:500]
                except (OSError, subprocess.TimeoutExpired, UnicodeError):
                    pass
    return identities


def record(
    root: Path,
    work_id: str,
    kind: str,
    commands: list[tuple[str, list[str]]],
    runner: Callable[[str, list[str]], int] | None = None,
) -> int:
    settings = config(root)
    if any(
        not isinstance(stage, str)
        or not stage
        or not command
        or any(not isinstance(argument, str) or not argument for argument in command)
        for stage, command in commands
    ):
        raise VerificationError("invalid verification command")
    destination = receipt_path(root, work_id)
    work_directory = safe(root, "docs/work")
    work_paths = list(work_directory.glob(f"{work_id}-*.md"))
    if len(work_paths) != 1:
        raise VerificationError("verification requires exactly one matching work record")
    work_text = safe(root, work_paths[0].relative_to(root).as_posix()).read_text(encoding="utf-8")
    if not re.search(rf"^Type: {re.escape(kind)}$", work_text, re.M) or not re.search(
        r"^Status: IN_PROGRESS$", work_text, re.M
    ):
        raise VerificationError("verification requires matching type and IN_PROGRESS status")
    before = snapshot(root, work_id)
    outcomes = []
    for stage, command in commands:
        try:
            code = (
                runner(stage, command)
                if runner
                else subprocess.run(command, cwd=root, check=False).returncode
            )
        except OSError:
            code = 1
        outcomes.append({"stage": stage, "command": command, "exit_code": code})
        if code:
            break
    after = snapshot(root, work_id)
    payload = {
        "schema_version": 1,
        "work_id": work_id,
        "kind": kind,
        "created_at": time.time(),
        "commands": outcomes,
        "tool_versions": tool_identity(outcomes, root),
        "inputs": before,
        "inputs_unchanged": before == after,
        "required_stages": settings["required_stages"].get(
            kind, settings["required_stages"]["default"]
        ),
    }
    serialized = json.dumps(payload, indent=2) + "\n"
    if len(serialized.encode("utf-8")) > MAX_BYTES:
        raise VerificationError("verification receipt exceeds 128 KiB")
    with repository_write(root, destination.relative_to(root.absolute()).as_posix()):
        destination = receipt_path(root, work_id)
        temporary: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", encoding="utf-8", dir=destination.parent, delete=False
            ) as stream:
                temporary = Path(stream.name)
                stream.write(serialized)
                stream.flush()
                os.fsync(stream.fileno())
            safe(root, destination.relative_to(root.absolute()).as_posix())
            os.replace(temporary, destination)
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)
    try:
        validate(root, work_id)
    except VerificationError:
        return 1
    return 0


def validate(root: Path, work_id: str, fresh: bool = True, kind: str | None = None) -> None:
    try:
        evidence = read_json(
            root, receipt_path(root, work_id).relative_to(root.absolute()).as_posix()
        )
        if evidence["schema_version"] != 1 or evidence["work_id"] != work_id:
            raise ValueError("work identity mismatch")
        if kind is not None and evidence["kind"] != kind:
            raise ValueError("work type mismatch")
        commands = evidence["commands"]
        if not commands or any(
            entry["exit_code"] != 0
            or not entry["command"]
            or not isinstance(entry["command"], list)
            or any(not isinstance(arg, str) for arg in entry["command"])
            for entry in commands
        ):
            raise ValueError("verification commands missing or failed")
        if not evidence["inputs_unchanged"] or not evidence["inputs"]:
            raise ValueError("verification inputs changed or missing")
        required = evidence["required_stages"]
        if not required or not set(required).issubset({entry["stage"] for entry in commands}):
            raise ValueError("required verification stages missing")
        if fresh:
            settings = config(root)
            expected = settings["required_stages"].get(
                evidence["kind"], settings["required_stages"]["default"]
            )
            recorded_tools = evidence["tool_versions"]
            current_tools = tool_identity(commands, root)
            recorded_stable = {
                key: value
                for key, value in recorded_tools.items()
                if not key.startswith("version:")
            }
            current_stable = {
                key: value for key, value in current_tools.items() if not key.startswith("version:")
            }
            versions_changed = any(
                key.startswith("version:") and current_tools[key] != recorded_tools[key]
                for key in current_tools.keys() & recorded_tools.keys()
            )
            if recorded_stable != current_stable or versions_changed:
                raise ValueError("verification tools changed")
            age = time.time() - evidence["created_at"]
            if not math.isfinite(age) or age < 0 or age > settings["max_age_seconds"]:
                raise ValueError("verification evidence expired")
            if required != expected or evidence["inputs"] != snapshot(root, work_id):
                raise ValueError("verification evidence stale; inputs or contract changed")
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
        raise VerificationError(f"{work_id}: invalid verification evidence: {exc}") from exc
