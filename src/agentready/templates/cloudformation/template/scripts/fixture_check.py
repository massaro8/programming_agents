"""Prove positive acceptance and seven negative policy/lint failures."""

import subprocess
from pathlib import Path

from infrastructure_tools import find_tool

ROOT = Path(__file__).resolve().parents[1]
LINT_CASES = {"invalid-property": "E3002", "broken-reference": "E1020"}


REQUIRED = {
    "valid",
    "valid-network",
    "valid-renamed",
    "invalid-property",
    "broken-reference",
    "public-s3",
    "missing-encryption",
    "missing-public-access-block",
    "missing-tls-policy",
    "unrestricted-ingress",
}


def main():
    base = ROOT / "infrastructure" if (ROOT / "infrastructure").is_dir() else ROOT
    paths = sorted((base / "tests/fixtures").glob("*.yaml"))
    missing = REQUIRED - {path.stem for path in paths}
    if missing:
        print("Missing required fixtures: " + ", ".join(sorted(missing)))
        return 1
    for path in paths:
        lint = path.stem in LINT_CASES
        names = (
            ("cfn-lint", "cfn-guard")
            if path.stem.startswith("valid")
            else (("cfn-lint",) if lint else ("cfn-guard",))
        )
        for name in names:
            tool = find_tool(ROOT, name)
            if tool is None:
                print(f"Missing {name}; see README.md local installation instructions")
                return 1
            command = (
                [tool, str(path)]
                if name == "cfn-lint"
                else [
                    tool,
                    "validate",
                    "--rules",
                    str(base / "policies/security.guard"),
                    "--data",
                    str(path),
                ]
            )
            result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False)
            expected = 0 if path.stem.startswith("valid") else (2 if lint else 19)
            diagnostic = result.stdout + result.stderr
            invalid = (
                (result.returncode & 2 == 0 or LINT_CASES[path.stem] not in diagnostic)
                if lint
                else result.returncode != expected
            )
            if not path.stem.startswith("valid") and not lint:
                invalid = invalid or "FAIL" not in diagnostic
            if invalid:
                print(
                    f"{path.name}: expected exit {expected}, got {result.returncode}\n"
                    f"{result.stdout}\n{result.stderr}"
                )
                return 1
    print("Three positive and seven negative fixtures passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
