"""Shared offline infrastructure stage selection."""

import sys

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
    for template in sorted(
        local_path(
            root, "infrastructure/templates" if (root / "infrastructure").is_dir() else "templates"
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
    commands.append(("negative fixtures", [sys.executable, "scripts/fixture_check.py"]))
    return commands
