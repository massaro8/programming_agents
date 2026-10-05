"""Deterministic architectural inventory, also exported as standalone project tooling.

Coverage concerns responsibility roots, capability layers and public surfaces, not
every implementation/helper file. No project code is imported or executed.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path


def _unsafe(path: Path) -> bool:
    return path.is_symlink() or path.is_junction()


def application_exports(path: Path) -> tuple[str, ...]:
    """Read a literal public __all__ declaration without importing source code."""
    if _unsafe(path):
        raise ValueError(f"unsafe public application surface: {path}")
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError):
        return ()
    for node in tree.body:
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            if any(isinstance(target, ast.Name) and target.id == "__all__" for target in targets):
                try:
                    value = ast.literal_eval(node.value) if node.value is not None else None
                except (ValueError, TypeError):
                    return ()
                if isinstance(value, (list, tuple)) and all(
                    isinstance(item, str) for item in value
                ):
                    return tuple(sorted(value))
    return ()


def _module_layers(module: Path) -> tuple[str, ...]:
    found = []
    for layer in ("domain", "application", "adapters"):
        directory, file = module / layer, module / f"{layer}.py"
        if _unsafe(directory) or _unsafe(file):
            raise ValueError(f"unsafe capability layer: {module.name}/{layer}")
        if directory.is_dir() or file.is_file():
            found.append(layer)
    return tuple(found)


def responsibilities(root: Path) -> tuple[Path, ...]:
    """Immediate Python files and source-containing packages, in stable order."""
    if _unsafe(root):
        raise ValueError(f"unsafe inventory root: {root}")
    if not root.is_dir():
        return ()
    found: list[Path] = []
    for child in sorted(root.iterdir()):
        if child.name.startswith((".", "_")):
            continue
        if _unsafe(child):
            raise ValueError(f"unsafe inventory item: {child}")
        if (child.is_file() and child.suffix == ".py") or (child.is_dir() and python_files(child)):
            found.append(child)
    return tuple(found)


def python_files(root: Path) -> tuple[Path, ...]:
    """Walk only source directories, rejecting links and ignoring cache/build areas."""
    if _unsafe(root):
        raise ValueError(f"unsafe source root: {root}")
    if not root.is_dir():
        return ()
    found: list[Path] = []
    for child in sorted(root.iterdir()):
        if child.name.startswith(".") or child.name in {"__pycache__", "build", "dist"}:
            continue
        if _unsafe(child):
            raise ValueError(f"unsafe source item: {child}")
        if child.is_dir():
            found.extend(python_files(child))
        elif child.suffix == ".py":
            found.append(child)
    return tuple(found)


@dataclass(frozen=True)
class Inventory:
    """Normalized source paths and architectural responsibility boundaries."""

    modules: tuple[Path, ...]
    entrypoints: tuple[Path, ...]
    platform: tuple[Path, ...]
    shared: tuple[Path, ...]
    tests: tuple[Path, ...]
    module_layers: tuple[tuple[str, tuple[str, ...]], ...]


def discover(root: Path, package: str) -> Inventory:
    package_root = root / "src" / package
    modules_root = package_root / "modules"
    if _unsafe(root / "src") or _unsafe(package_root) or _unsafe(modules_root):
        raise ValueError("unsafe package/module inventory root")
    modules = (
        tuple(
            child
            for child in sorted(modules_root.iterdir())
            if child.is_dir() and not child.name.startswith((".", "__"))
        )
        if modules_root.is_dir()
        else ()
    )
    for module in modules:
        if _unsafe(module):
            raise ValueError(f"unsafe capability module: {module}")
    return Inventory(
        modules,
        responsibilities(package_root / "entrypoints"),
        responsibilities(package_root / "platform"),
        responsibilities(package_root / "shared"),
        tuple(path for path in python_files(root / "tests") if path.name.startswith("test_")),
        tuple((module.name, _module_layers(module)) for module in modules),
    )
