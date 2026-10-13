"""Offline environment and parameter declarations; never resolves remote values."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from agentready.local_paths import read_json


def validate_contracts(root: Path) -> list[str]:
    """Return declaration errors without consulting credentials or network services."""
    errors: list[str] = []
    try:
        environments = read_json(root, "docs/infrastructure/environments.json")
        parameters = read_json(root, "docs/infrastructure/parameters.json")
        if environments.get("schema") != 1 or parameters.get("schema") != 1:
            errors.append("unsupported infrastructure contract schema")
        entries = environments.get("environments", {})
        branches = environments.get("branches", {})
        if not isinstance(entries, dict) or not entries or not isinstance(branches, dict):
            raise ValueError("environment and branch maps are required")
        for name, entry in entries.items():
            if not isinstance(entry, dict) or not all(
                isinstance(entry.get(key), str) and entry[key]
                for key in ("account_ref", "region", "namespace", "role_ref", "stack_pattern")
            ):
                errors.append(f"invalid environment declaration: {name}")
                continue
            if "{namespace}" not in entry["stack_pattern"]:
                errors.append(f"stack pattern must include namespace: {name}")
        if any(name not in entries for name in branches.values()) or "*" in branches:
            errors.append("branch map must name declared environments without a fallback")
        declarations = parameters.get("parameters", [])
        if not isinstance(declarations, list):
            raise ValueError("parameters must be a list")
        names: set[str] = set()
        for declaration in declarations:
            if not isinstance(declaration, dict):
                raise ValueError("parameter must be an object")
            name = declaration.get("name")
            if not isinstance(name, str) or not name or name in names:
                errors.append("parameter names must be unique and nonempty")
            else:
                names.add(name)
            if declaration.get("type") not in ("String", "Number", "CommaDelimitedList"):
                errors.append(f"unsupported parameter type: {name}")
            if not isinstance(declaration.get("required"), bool):
                errors.append(f"required must be boolean: {name}")
            if declaration.get("environment") not in entries:
                errors.append(f"unknown parameter environment: {name}")
            if declaration.get("sensitive") is True:
                if declaration.get("source") != "dynamic-reference" or "default" in declaration:
                    errors.append(
                        f"sensitive parameter must declare dynamic reference only: {name}"
                    )
                if not re.fullmatch(
                    r"\{\{resolve:(?:secretsmanager|ssm-secure):[^{}]+\}\}",
                    str(declaration.get("reference", "")),
                ):
                    errors.append(f"invalid dynamic reference declaration: {name}")
            elif declaration.get("source") not in ("literal", "environment", "ssm", "stack-output"):
                errors.append(f"unsupported parameter source: {name}")
            if any(key in declaration for key in ("value", "resolved_value", "secret_value")):
                errors.append(f"resolved values are forbidden in declarations: {name}")
    except (OSError, ValueError, TypeError) as exc:
        errors.append(f"invalid infrastructure contracts: {exc}")
    return errors


def resolve_environment(
    root: Path,
    branch: str,
    references: dict[str, str],
    caller_account: str,
    caller_region: str,
) -> dict[str, Any]:
    """Resolve explicit caller-provided references, failing closed on context mismatch."""
    errors = validate_contracts(root)
    if errors:
        raise ValueError("; ".join(errors))
    contract = read_json(root, "docs/infrastructure/environments.json")
    name = contract["branches"].get(branch)
    if name is None:
        raise ValueError("branch has no explicit environment mapping")
    entry = dict(contract["environments"][name])
    account = references.get(entry["account_ref"])
    role = references.get(entry["role_ref"])
    if not account or not role or account != caller_account or entry["region"] != caller_region:
        raise ValueError("unresolved reference or caller account/region mismatch")
    entry.update(environment=name, account=account, role=role)
    return entry
