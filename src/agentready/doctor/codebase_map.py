"""Read-only structural validation of a generated project's codebase map."""

from __future__ import annotations

import re
from pathlib import Path


def _visible_directories(root: Path) -> set[str] | None:
    if not root.exists():
        return set()
    if not root.is_dir() or root.is_symlink():
        return None
    return {
        path.name
        for path in root.iterdir()
        if path.is_dir() and not path.is_symlink() and not path.name.startswith((".", "__"))
    }


def validate(root: Path, package: str, profile: str, text: str | None) -> bool:
    """Check the material module/adapter inventory without executing project code."""

    if text is None or not text.startswith("# Codebase Map\n"):
        return False
    if f"Profile: `{profile}`" not in text:
        return False
    package_root = root / "src" / package
    module_root = package_root / "modules"
    modules = _visible_directories(module_root)
    if modules is None:
        return False
    section = text.split("## Modules\n", 1)
    if len(section) != 2:
        return False
    body = section[1].split("\n## ", 1)[0]
    listed_modules = set(re.findall(r"(?m)^- `([^`]+)`: ", body))
    if listed_modules != modules:
        return False
    listed_adapters = set(re.findall(r"(?m)^  - Adapter: `([^`]+)`", body))
    adapters: set[str] = set()
    for module in modules:
        adapter_root = module_root / module / "adapters"
        if adapter_root.is_symlink():
            return False
        if adapter_root.is_dir():
            adapters.update(
                f"modules.{module}.adapters.{path.stem}"
                for path in adapter_root.glob("*.py")
                if path.name != "__init__.py" and not path.is_symlink()
            )
    return listed_adapters == adapters
