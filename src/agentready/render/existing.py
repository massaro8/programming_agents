"""Initialize a bootstrap-only repository without modifying Git metadata."""

from __future__ import annotations

import os
import tempfile
from collections.abc import Callable
from pathlib import Path

from agentready.core.project import Project

BOOTSTRAP_FILES = frozenset(
    {"README.md", ".gitignore", "LICENSE", "LICENSE.md", "LICENSE.txt", ".gitattributes"}
)
README_MARKER = b"<!-- AgentReady development: start -->"
IGNORE_MARKER = b"# AgentReady development: start"


class ExistingInitError(ValueError):
    """An existing repository cannot be safely initialized."""


def _safe(path: Path) -> None:
    if any(p.is_symlink() or p.is_junction() for p in (path, *path.parents)):
        raise ExistingInitError(f"unsafe symlink or junction: {path}")


def _preflight(root: Path) -> dict[str, bytes]:
    _safe(root)
    if not root.is_dir():
        raise ExistingInitError("--into-existing requires an existing directory")
    originals: dict[str, bytes] = {}
    entries = sorted(root.iterdir())
    if any(p.name == ".agentready" for p in entries):
        raise ExistingInitError("repository already initialized with AgentReady; no files changed")
    for path in entries:
        _safe(path)
        if path.name == ".git":
            if not path.is_dir():
                raise ExistingInitError(
                    ".git must be a directory; linked worktrees are unsupported"
                )
            for directory, children, files in os.walk(path, followlinks=False):
                for name in (*children, *files):
                    _safe(Path(directory) / name)
            continue
        if path.name not in BOOTSTRAP_FILES or not path.is_file():
            raise ExistingInitError(
                f"unexpected existing path: {path.name}; use a bootstrap-only repository "
                "or initialize a separate empty directory; no files changed"
            )
        if path.stat().st_size > 1024 * 1024:
            raise ExistingInitError(f"bootstrap file exceeds 1 MiB: {path.name}")
        originals[path.name] = path.read_bytes()
    if entries and not (root / ".git").is_dir():
        raise ExistingInitError("nonempty --into-existing target must contain a .git directory")
    return originals


def _readme(original: bytes, generated: bytes) -> bytes:
    original.decode("utf-8")
    if README_MARKER in original:
        raise ExistingInitError("README.md already contains an AgentReady section; review it first")
    if generated.strip() in original:
        return original
    return (
        original
        + (b"\n" if original and not original.endswith(b"\n") else b"")
        + b"\n"
        + README_MARKER
        + b"\n"
        + generated.rstrip()
        + b"\n"
        + b"<!-- AgentReady development: end -->\n"
    )


def _gitignore(original: bytes, generated: bytes) -> bytes:
    text = original.decode("utf-8-sig")
    if IGNORE_MARKER in original:
        raise ExistingInitError(
            ".gitignore already contains an AgentReady section; review it first"
        )
    lines = set(text.splitlines())
    missing = [
        line for line in generated.decode("utf-8").splitlines() if line and line not in lines
    ]
    if not missing:
        return original
    # User rules come last, so existing negations and overrides retain precedence.
    block = IGNORE_MARKER + b"\n" + "\n".join(missing).encode() + b"\n"
    block += b"# AgentReady development: end\n\n"
    bom = b"\xef\xbb\xbf"
    return bom + block + original[3:] if original.startswith(bom) else block + original


def _replace_bootstrap(path: Path, data: bytes, mode: int) -> None:
    """Keep the original intact until the complete replacement is durable."""
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            dir=path.parent, prefix=".agentready-init-", delete=False
        ) as f:
            temporary = Path(f.name)
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.chmod(temporary, mode)
        os.replace(temporary, path)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def initialize_existing(root: Path, render: Callable[[Path], Project]) -> None:
    """Stage and preflight everything, then publish with rollback on write failure."""
    originals = _preflight(root)
    root_stat = root.stat()
    stats = {name: (root / name).stat() for name in originals}
    with tempfile.TemporaryDirectory(prefix="agentready-init-") as temporary:
        staged = Path(temporary) / root.name
        render(staged)
        payloads: dict[str, bytes] = {}
        for path in sorted(staged.rglob("*")):
            _safe(path)
            if not path.is_file():
                continue
            name = path.relative_to(staged).as_posix()
            if ".." in Path(name).parts or name.startswith(".git/") or name == ".git":
                raise ExistingInitError(f"unsafe generated path: {name}")
            data = path.read_bytes()
            if name in originals:
                try:
                    if name == "README.md":
                        data = _readme(originals[name], data)
                    elif name == ".gitignore":
                        data = _gitignore(originals[name], data)
                    elif name.startswith("LICENSE") or name == ".gitattributes":
                        continue
                    else:
                        raise ExistingInitError(f"generated filename collision: {name}")
                except UnicodeError as exc:
                    raise ExistingInitError(f"{name} must be UTF-8; no files changed") from exc
            elif (root / name).exists():
                raise ExistingInitError(f"generated filename collision: {name}")
            payloads[name] = data
        if _preflight(root) != originals:
            raise ExistingInitError(
                "bootstrap files changed during staging; retry; no files changed"
            )
        created: list[Path] = []
        directories: list[Path] = []
        modified: list[str] = []
        try:
            # Publish the initialization marker last, after all usable artifacts exist.
            for name in sorted(payloads, key=lambda n: (n == ".agentready/manifest.toml", n)):
                destination = root / name
                for parent in reversed(destination.parents):
                    if parent == root or root not in parent.parents:
                        continue
                    _safe(parent)
                    if not parent.exists():
                        parent.mkdir()
                        directories.append(parent)
                _safe(destination)
                if name in originals:
                    if destination.read_bytes() != originals[name]:
                        raise ExistingInitError(f"{name} changed during publication; retry")
                    if payloads[name] == originals[name]:
                        continue
                    modified.append(name)
                    _replace_bootstrap(destination, payloads[name], stats[name].st_mode)
                else:
                    with destination.open("xb") as stream:
                        created.append(destination)
                        stream.write(payloads[name])
        except BaseException:
            for path in reversed(created):
                _safe(path)
                path.unlink()
            for name in reversed(modified):
                path = root / name
                _safe(path)
                if path.read_bytes() != originals[name]:
                    _replace_bootstrap(path, originals[name], stats[name].st_mode)
                os.utime(path, ns=(stats[name].st_atime_ns, stats[name].st_mtime_ns))
            for path in reversed(directories):
                _safe(path)
                path.rmdir()
            os.utime(root, ns=(root_stat.st_atime_ns, root_stat.st_mtime_ns))
            raise
