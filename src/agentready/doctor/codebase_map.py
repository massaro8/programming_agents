"""Read-only structural validation of a generated project's codebase map."""

from __future__ import annotations

import re
from pathlib import Path

from agentready.core.inventory import application_exports, discover, python_files


def validate(root: Path, package: str, profile: str, text: str | None) -> bool:
    """Check the material module/adapter inventory without executing project code."""

    if text is None or not text.startswith("# Codebase Map\n"):
        return False
    if f"Profile: `{profile}`" not in text:
        return False
    package_root = root / "src" / package
    module_root = package_root / "modules"
    try:
        inventory = discover(root, package)
    except (OSError, ValueError):
        return False
    modules = {path.name for path in inventory.modules}
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
            try:
                adapters.update(
                    f"modules.{module}.adapters."
                    + ".".join(path.relative_to(adapter_root).with_suffix("").parts)
                    for path in python_files(adapter_root)
                    if path.name != "__init__.py"
                )
            except (OSError, ValueError):
                return False
    if listed_adapters != adapters:
        return False
    # Validate coverage from source truth, never by invoking the map renderer.
    # Exact architectural paths belong to their own sections; stray mentions in
    # unrelated prose cannot mask omissions.
    for heading, expected in (
        ("Entrypoints", inventory.entrypoints),
        ("Platform and shared", (*inventory.platform, *inventory.shared)),
    ):
        section = text.split(f"## {heading}\n", 1)
        if len(section) != 2:
            return False
        tokens = set(re.findall(r"`([^`]+)`", section[1].split("\n## ", 1)[0]))
        if any(path.relative_to(root).as_posix() not in tokens for path in expected):
            return False
    if (root / "tests").is_dir() and "- Test root: `tests/`" not in text:
        return False
    for module_path in inventory.modules:
        line = next(
            (line for line in body.splitlines() if line.startswith(f"- `{module_path.name}`:")),
            "",
        )
        for layer in dict(inventory.module_layers)[module_path.name]:
            if f"`{layer}`" not in line:
                return False
        module_body = body.split(f"- `{module_path.name}`:", 1)[1].split("\n- `", 1)[0]
        application = module_path / "application" / "__init__.py"
        if not application.is_file():
            application = module_path / "application.py"
        try:
            exports = application_exports(application)
        except ValueError:
            return False
        match = re.search(r"Public application contract: `([^`]+)`", module_body)
        represented = set(match.group(1).split(", ")) if match else set()
        if set(exports) != represented:
            return False
    return True
