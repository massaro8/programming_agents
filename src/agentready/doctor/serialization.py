"""Stable machine-readable serialization for doctor reports."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from agentready.core.project import Project
from agentready.doctor.inspector import DoctorReport


def serialize_report(report: DoctorReport, target: Path | str = ".") -> str:
    """Return schema-1 JSON without exposing absolute machine paths."""

    path = Path(target)
    absolute = path if path.is_absolute() else Path.cwd() / path
    project = Project(absolute).path.name or "."
    checks: list[dict[str, Any]] = []
    for finding in report.findings:
        checks.append(
            {
                "id": finding.check_id,
                "status": finding.status.value.lower(),
                "message": finding.message,
                "path": finding.path.path.as_posix() if finding.path else None,
            }
        )
    payload = {
        "schema": 1,
        "status": "healthy" if report.healthy else "unhealthy",
        "project": project,
        "checks": checks,
    }
    return json.dumps(payload, indent=2) + "\n"
