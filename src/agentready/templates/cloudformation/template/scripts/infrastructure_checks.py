"""Shared offline infrastructure stage selection."""

import os
import shutil
import sys
from pathlib import Path

from infrastructure_tools import find_tool


def commands(root):
    tools = {name: find_tool(root, name) for name in ("cfn-lint", "cfn-guard")}
    missing = [name for name, location in tools.items() if location is None]
    if missing:
        raise ValueError(
            "Missing required tools: "
            + ", ".join(missing)
            + ". Run python scripts/project.py bootstrap to prepare .tools executables "
            "(or install cfn-lint in .venv). "
            "Download Guard from https://github.com/aws-cloudformation/"
            "cloudformation-guard/releases. Add local executables to PATH; see README.md."
        )
    from local_paths import local_path

    commands = [
        ("environment contracts", [sys.executable, "scripts/environment_contracts.py", "check"])
    ]
    git_bash = Path(os.environ.get("PROGRAMFILES", "C:/Program Files")) / "Git/bin/bash.exe"
    bash = str(git_bash) if sys.platform == "win32" and git_bash.is_file() else shutil.which("bash")
    if not bash:
        raise ValueError("Missing Bash 4+; install Git Bash on Windows and add its bin to PATH")
    commands.append(("stack catalog", [bash, "scripts/deploy.sh", "catalog"]))
    for script in ("cfn_lib.sh", "deploy.sh", "validate.sh", "bootstrap.sh"):
        commands.append(("shell syntax", [bash, "-n", "scripts/" + script]))
    for template in sorted(
        local_path(
            root, "infrastructure/stacks" if (root / "infrastructure").is_dir() else "stacks"
        ).rglob("*")
    ):
        template = local_path(root, template.relative_to(root).as_posix())
        if template.suffix.lower() in (".yaml", ".yml", ".json") and template.is_file():
            commands.extend(
                [
                    ("cfn-lint", [tools["cfn-lint"], str(template)]),
                    (
                        "Guard",
                        [
                            tools["cfn-guard"],
                            "validate",
                            "--rules",
                            str(
                                root
                                / (
                                    "infrastructure/policies/security.guard"
                                    if (root / "infrastructure").is_dir()
                                    else "policies/security.guard"
                                )
                            ),
                            "--data",
                            str(template),
                        ],
                    ),
                ]
            )
    engine = (
        "infrastructure/tests/engine/run.sh"
        if (root / "infrastructure").is_dir()
        else "tests/engine/run.sh"
    )
    commands.append(("engine tests", [bash, engine]))
    commands.append(("negative fixtures", [sys.executable, "scripts/fixture_check.py"]))
    return commands
