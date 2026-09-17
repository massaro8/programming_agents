from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from agentready.cli import main
from agentready.doctor.inspector import inspect
from agentready.doctor.serialization import serialize_report
from agentready.render.generator import generate_project


def _project(tmp_path: Path) -> Path:
    target = tmp_path / "demo_agentready"
    generate_project(target)
    return target


def _snapshot(root: Path) -> tuple[tuple[str, str, bytes], ...]:
    entries: list[tuple[str, str, bytes]] = []
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix()
        if path.is_dir():
            entries.append((relative, "directory", b""))
        else:
            entries.append((relative, "file", path.read_bytes()))
    return tuple(entries)


def test_json_is_ordered_deterministic_and_relative(tmp_path: Path) -> None:
    target = _project(tmp_path)
    report = inspect(target)

    first = serialize_report(report, target)
    second = serialize_report(report, target)
    parsed = json.loads(first)

    assert first == second
    assert list(parsed) == ["schema", "status", "project", "checks"]
    assert parsed["schema"] == 1
    assert parsed["status"] == "healthy"
    assert parsed["project"] == "demo_agentready"
    assert str(tmp_path) not in first
    assert [check["id"] for check in parsed["checks"]] == [
        finding.check_id for finding in report.findings
    ]
    assert all(list(check) == ["id", "status", "message", "path"] for check in parsed["checks"])
    assert all(check["status"] == "pass" for check in parsed["checks"])
    assert all(
        check["path"] is None or not Path(check["path"]).is_absolute() for check in parsed["checks"]
    )


def test_absolute_and_relative_targets_have_same_project_identifier(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    target = _project(tmp_path)
    caller = tmp_path / "unrelated"
    caller.mkdir()
    relative = Path(os.path.relpath(target, caller))

    absolute_json = serialize_report(inspect(target), target)
    monkeypatch.chdir(caller)
    relative_json = serialize_report(inspect(relative), relative)

    assert json.loads(absolute_json)["project"] == "demo_agentready"
    assert json.loads(relative_json)["project"] == "demo_agentready"


def test_unhealthy_json_and_human_modes_have_exit_parity(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    target = _project(tmp_path)
    (target / ".agentready/manifest.toml").unlink()

    human_exit = main(["doctor", str(target)])
    capsys.readouterr()
    json_exit = main(["doctor", str(target), "--format", "json"])
    output = capsys.readouterr().out
    parsed = json.loads(output)

    assert human_exit == json_exit == 1
    assert parsed["status"] == "unhealthy"
    assert any(check["status"] == "fail" for check in parsed["checks"])


def test_healthy_json_cli_is_read_only(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    target = _project(tmp_path)
    before = _snapshot(target)

    exit_code = main(["doctor", str(target), "--format", "json"])
    output = capsys.readouterr().out

    assert exit_code == 0
    assert json.loads(output)["status"] == "healthy"
    assert _snapshot(target) == before


def test_authoritative_schema_matches_emitted_contract(tmp_path: Path) -> None:
    schema_path = Path(__file__).parents[1] / "schemas/doctor.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    payload = json.loads(serialize_report(inspect(_project(tmp_path)), "demo_agentready"))

    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert schema["properties"]["schema"]["const"] == payload["schema"] == 1
    assert schema["required"] == ["schema", "status", "project", "checks"]
    assert schema["additionalProperties"] is False
    assert payload["status"] in schema["properties"]["status"]["enum"]
    item_schema = schema["properties"]["checks"]["items"]
    assert item_schema["required"] == ["id", "status", "message", "path"]
    assert item_schema["additionalProperties"] is False
    assert all(
        check["status"] in item_schema["properties"]["status"]["enum"]
        for check in payload["checks"]
    )
