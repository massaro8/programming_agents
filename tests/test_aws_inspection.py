import json
import subprocess

from agentready.aws_inspection import discover, inspect_stack


def test_missing_tools_and_unsupported_toolkit() -> None:
    calls: list[list[str]] = []

    def missing(argv: list[str]) -> subprocess.CompletedProcess[str]:
        calls.append(argv)
        raise FileNotFoundError

    assert discover(missing) == {"aws": False, "toolkit": False}
    assert all("configure" not in call for call in calls)


def test_inspection_authorization_identity_and_redaction() -> None:
    calls: list[list[str]] = []
    identity = {
        "Account": "000000000000",
        "Arn": "arn:aws:sts::000000000000:assumed-role/ReadOnly/session",
    }
    stacks = {
        "Stacks": [
            {
                "StackName": "sandbox-storage",
                "StackStatus": "CREATE_COMPLETE",
                "Parameters": [{"ParameterValue": "hidden"}],
                "Outputs": [
                    {"OutputKey": "Endpoint", "OutputValue": "example.invalid"},
                    {"OutputKey": "Password", "OutputValue": "hidden"},
                    {"OutputKey": "Other", "OutputValue": "hidden"},
                ],
            }
        ]
    }

    def runner(argv: list[str]) -> subprocess.CompletedProcess[str]:
        calls.append(argv)
        return subprocess.CompletedProcess(
            argv, 0, json.dumps(identity if argv[1] == "sts" else stacks), ""
        )

    args = dict(
        profile="read-only",
        region="eu-west-1",
        stack="sandbox-storage",
        expected_account="000000000000",
        expected_role="ReadOnly",
        runner=runner,
    )
    assert inspect_stack(**args, authorized=False)["status"] == "offline"
    assert not calls
    result = inspect_stack(**args, authorized=True, output_allowlist=("Endpoint", "Password"))
    assert result["outputs"] == {"Endpoint": "example.invalid"}
    assert "hidden" not in json.dumps(result)
    assert [call[2] for call in calls] == ["get-caller-identity", "describe-stacks"]
    calls.clear()
    identity["Account"] = "wrong"
    assert inspect_stack(**args, authorized=True)["status"] == "offline"
    assert len(calls) == 1


def test_missing_stack_and_denied_credentials() -> None:
    count = 0

    def runner(argv: list[str]) -> subprocess.CompletedProcess[str]:
        nonlocal count
        count += 1
        body = (
            {
                "Account": "000000000000",
                "Arn": "arn:aws:sts::000000000000:assumed-role/ReadOnly/session",
            }
            if count == 1
            else {"Stacks": []}
        )
        return subprocess.CompletedProcess(argv, 0, json.dumps(body), "")

    args = dict(
        profile="readonly",
        region="eu-west-1",
        stack="sandbox-storage",
        expected_account="000000000000",
        expected_role="ReadOnly",
        authorized=True,
    )
    assert inspect_stack(**args, runner=runner)["status"] == "missing"

    def denied(argv: list[str]) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(argv, 1, "", "sensitive provider error")

    assert inspect_stack(**args, runner=denied)["status"] == "offline"
