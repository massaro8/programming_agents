#!/usr/bin/env bash
# Local validation only; project bootstrap installs local tools, never IAM.
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.."
exec "${PYTHON:-python}" scripts/project.py verify
