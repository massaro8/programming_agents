"""Regression tests for the product repository's generated navigation map."""

from __future__ import annotations

import importlib.util
import subprocess
from pathlib import Path


def test_tracked_files_excludes_deleted_paths(tmp_path: Path) -> None:
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    present = tmp_path / "present.py"
    deleted = tmp_path / "deleted.py"
    present.write_text("pass\n", encoding="utf-8")
    deleted.write_text("pass\n", encoding="utf-8")
    subprocess.run(["git", "add", "present.py", "deleted.py"], cwd=tmp_path, check=True)
    deleted.unlink()

    script = Path(__file__).parents[1] / "scripts/generate_codebase_map.py"
    spec = importlib.util.spec_from_file_location("product_codebase_map", script)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.ROOT = tmp_path

    assert module.tracked_files() == ["present.py"]
