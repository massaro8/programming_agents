"""Deterministic file-level infrastructure navigation; no YAML inference."""
from pathlib import Path
import argparse
import hashlib
import os
from local_paths import local_path, repository_write

ROOT = Path(__file__).resolve().parents[1]
AREAS = ("stacks", "deployment", ".githooks", "templates", "parameters", "policies", "scripts", ".agents/skills", ".claude/skills", "docs/work", "docs/agent", "tests/fixtures", "tests/engine")

def render(root):
    paths = []
    for area in AREAS:
        base = local_path(root, area)
        if base.is_symlink() or base.is_junction():
            raise ValueError(f"unsafe inventory area: {area}")
        for directory, dirs, files in os.walk(base, followlinks=False):
            parent = Path(directory)
            dirs[:] = sorted(name for name in dirs if name != "__pycache__" and not (parent == root / "docs/work" and name in {"checkpoints", "evidence"}))
            for name in [*dirs, *files]:
                path = parent / name
                if path.is_symlink() or path.is_junction():
                    raise ValueError(f"unsafe inventory path: {path}")
            for name in files:
                if not name.endswith(".pyc"):
                    paths.append((parent / name).relative_to(root).as_posix())
                    if len(paths) > 10000:
                        raise ValueError("inventory limit exceeded")
    paths.sort()
    fingerprint = hashlib.sha256("\n".join(paths).encode()).hexdigest()[:12]
    return "# Codebase Map\n\nStructure fingerprint: `" + fingerprint + "`\n\nFile-level inventory; regenerate with python scripts/project.py sync.\n\n" + "".join("- `" + p + "`\n" for p in paths)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    relative = "docs/generated/CODEBASE_MAP.md"
    path = local_path(ROOT, relative)
    expected = render(ROOT)
    if args.check:
        if not path.is_file() or path.read_text(encoding="utf-8") != expected:
            print("Codebase map stale; run python scripts/project.py sync")
            return 1
    else:
        with repository_write(ROOT, relative):
            path = local_path(ROOT, relative)
            temporary = local_path(ROOT, relative + ".tmp")
            with temporary.open("x", encoding="utf-8", newline="\n") as stream:
                stream.write(expected)
            try:
                os.replace(temporary, local_path(ROOT, relative))
            finally:
                if temporary.exists():
                    local_path(ROOT, relative + ".tmp").unlink()
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
