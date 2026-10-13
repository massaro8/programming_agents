import json
import shutil
from pathlib import Path

import pytest

from agentready.environment_contracts import resolve_environment, validate_contracts


@pytest.fixture
def root(tmp_path: Path) -> Path:
    source = Path("src/agentready/templates/cloudformation/template/docs/infrastructure")
    shutil.copytree(source, tmp_path / "docs/infrastructure")
    return tmp_path


def test_offline_contract_and_context(root: Path) -> None:
    assert validate_contracts(root) == []
    refs = {"SANDBOX_ACCOUNT": "000000000000", "SANDBOX_READ_ONLY_ROLE": "ReadOnly"}
    assert (
        resolve_environment(root, "sandbox", refs, "000000000000", "eu-west-1")["namespace"]
        == "sandbox"
    )
    for branch, account, region in (
        ("main", "000000000000", "eu-west-1"),
        ("sandbox", "wrong", "eu-west-1"),
        ("sandbox", "000000000000", "wrong"),
    ):
        with pytest.raises(ValueError):
            resolve_environment(root, branch, refs, account, region)


def test_sensitive_declarations_cannot_store_values(root: Path) -> None:
    path = root / "docs/infrastructure/parameters.json"
    parameter = {
        "name": "Password",
        "type": "String",
        "required": True,
        "environment": "sandbox",
        "sensitive": True,
        "source": "dynamic-reference",
        "reference": "{{resolve:ssm-secure:example}}",
    }
    path.write_text(json.dumps({"schema": 1, "parameters": [parameter]}))
    assert validate_contracts(root) == []
    parameter["default"] = "forbidden"
    path.write_text(json.dumps({"schema": 1, "parameters": [parameter]}))
    assert validate_contracts(root)
