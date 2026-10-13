"""Explicitly authorized, bounded AWS metadata inspection with injectable execution."""

from __future__ import annotations

import json
import re
import subprocess
from collections.abc import Callable
from typing import Any

Runner = Callable[[list[str]], subprocess.CompletedProcess[str]]


def run(argv: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(argv, capture_output=True, text=True, timeout=30, check=False)


def discover(runner: Runner = run) -> dict[str, bool]:
    """Discover local capabilities only; do not install or configure anything."""
    result = {"aws": False, "toolkit": False}
    for executable, key in (("aws", "aws"), ("agent-toolkit", "toolkit")):
        try:
            help_result = runner([executable, "--help"])
            if key == "aws":
                result[key] = runner([executable, "--version"]).returncode == 0
            elif help_result.returncode == 0 and "list-installed-skills" in help_result.stdout:
                result[key] = runner([executable, "list-installed-skills"]).returncode == 0
        except (OSError, subprocess.SubprocessError):
            pass
    return result


def inspect_stack(
    *,
    profile: str,
    region: str,
    stack: str,
    expected_account: str,
    expected_role: str,
    authorized: bool,
    runner: Runner = run,
    output_allowlist: tuple[str, ...] = (),
) -> dict[str, Any]:
    """Return safe selected metadata; IAM permissions remain the security boundary."""
    if not authorized or not all((profile, region, stack, expected_account, expected_role)):
        return {"status": "offline", "reason": "explicit authorization and context required"}
    if not all(re.fullmatch(r"[A-Za-z0-9_.:/-]+", value) for value in (profile, region, stack)):
        return {"status": "offline", "reason": "invalid named target"}

    def query(service: str, operation: str, arguments: list[str]) -> dict[str, Any]:
        response = runner(
            [
                "aws",
                service,
                operation,
                *arguments,
                "--profile",
                profile,
                "--region",
                region,
                "--output",
                "json",
                "--no-cli-pager",
            ]
        )
        if response.returncode or len(response.stdout) > 128 * 1024:
            raise ValueError("AWS unavailable, denied, or response exceeds bound")
        data = json.loads(response.stdout)
        if not isinstance(data, dict):
            raise ValueError("unexpected AWS response")
        return data

    try:
        identity = query("sts", "get-caller-identity", [])
        arn = str(identity.get("Arn", ""))
        role_match = re.fullmatch(
            r"arn:aws(?:-[a-z]+)?:sts::([0-9]{12}):assumed-role/([^/]+)/[^/]+", arn
        )
        if (
            identity.get("Account") != expected_account
            or not role_match
            or role_match[2] != expected_role
        ):
            return {"status": "offline", "reason": "caller account or role mismatch"}
        response = query("cloudformation", "describe-stacks", ["--stack-name", stack])
        stacks = response.get("Stacks", [])
        if not stacks:
            return {"status": "missing", "stack": stack}
        entry = stacks[0]
        if entry.get("StackName") != stack:
            raise ValueError("target stack mismatch")
        outputs = {
            item["OutputKey"]: item.get("OutputValue", "")
            for item in entry.get("Outputs", [])[:100]
            if item.get("OutputKey") in output_allowlist
            and not re.search(r"(?i)secret|password|token|credential|key", item["OutputKey"])
            and not re.search(
                r"(?i)resolve:|secret|password|token|credential|sk-|AKIA",
                str(item.get("OutputValue", "")),
            )
        }
        return {
            "status": "inspected",
            "stack": stack,
            "region": region,
            "stack_status": entry.get("StackStatus", "unknown"),
            "outputs": outputs,
        }
    except (OSError, subprocess.SubprocessError, ValueError, KeyError, TypeError):
        return {
            "status": "offline",
            "reason": "inspection unavailable; use local templates and contracts",
        }
