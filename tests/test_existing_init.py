"""Bootstrap adoption preserves user files and never touches Git metadata."""

from __future__ import annotations

import hashlib
import os
import subprocess
import zlib
from pathlib import Path

import pytest

from agentready.cli import main
from agentready.detach.service import detach_project
from agentready.doctor.inspector import inspect
from agentready.render.existing import IGNORE_MARKER, README_MARKER
from agentready.render.generator import GeneratorError, generate_project


def tree(root: Path) -> dict[str, bytes]:
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob("*") if p.is_file()}


@pytest.fixture
def repository(tmp_path: Path) -> Path:
    root = tmp_path / "owner-project"
    root.mkdir()
    subprocess.run(["git", "init", "--quiet", str(root)], check=True)
    subprocess.run(
        [
            "git",
            "-C",
            str(root),
            "remote",
            "add",
            "origin",
            "https://example.invalid/owner/repo.git",
        ],
        check=True,
    )

    # Seed existing history/branches without executing commit or checkout commands.
    def object_id(kind: str, data: bytes) -> str:
        raw = f"{kind} {len(data)}\0".encode() + data
        digest = hashlib.sha1(raw, usedforsecurity=False).hexdigest()
        path = root / ".git/objects" / digest[:2] / digest[2:]
        path.parent.mkdir(exist_ok=True)
        path.write_bytes(zlib.compress(raw))
        return digest

    tree_id = object_id("tree", b"")
    commit_id = object_id(
        "commit",
        f"tree {tree_id}\nauthor Owner <owner@example.invalid> 0 +0000\n"
        "committer Owner <owner@example.invalid> 0 +0000\n\nExisting history\n".encode(),
    )
    (root / ".git/refs/heads/main").write_text(commit_id + "\n")
    (root / ".git/refs/heads/owner-branch").write_text(commit_id + "\n")
    (root / ".git/HEAD").write_text("ref: refs/heads/main\n")
    (root / "README.md").write_bytes(b"# Owner project\r\n\r\nOriginal instructions.\r\n")
    (root / ".gitignore").write_bytes(b"owner.tmp\r\n!.venv/\r\n")
    (root / "LICENSE").write_bytes(b"OWNER LICENSE\r\n")
    (root / ".gitattributes").write_bytes(b"*.py text eol=lf\n")
    return root


@pytest.mark.parametrize(
    "options",
    [
        {},
        {"family": "cloudformation"},
        {"components": ["cloudformation"]},
        {"profile": "application"},
        {"profile": "service"},
    ],
)
def test_existing_repository_preservation(repository: Path, options: dict[str, object]) -> None:
    before = tree(repository)
    generate_project(repository, into_existing=True, **options)  # type: ignore[arg-type]
    after = tree(repository)
    assert all(
        after[name] == content
        for name, content in before.items()
        if name.startswith(".git/") or name in ("LICENSE", ".gitattributes")
    )
    assert before["README.md"] in after["README.md"]
    assert before[".gitignore"] in after[".gitignore"]
    assert after["README.md"].count(README_MARKER) == 1
    assert after[".gitignore"].count(IGNORE_MARKER) == 1
    assert after[".gitignore"].endswith(before[".gitignore"])
    assert inspect(repository).healthy
    with pytest.raises(GeneratorError, match="already initialized"):
        generate_project(repository, into_existing=True, **options)  # type: ignore[arg-type]
    assert tree(repository) == after
    detach_project(repository)
    assert tree(repository) == {
        name: data for name, data in after.items() if not name.startswith(".agentready/")
    }


@pytest.mark.parametrize("collision", ["AGENTS.md", "src", "pyproject.toml", "README.md/bad"])
def test_collisions_leave_repository_unchanged(repository: Path, collision: str) -> None:
    if "/" in collision:
        (repository / "README.md").unlink()
        (repository / "README.md").mkdir()
        (repository / collision).write_text("user content")
    elif collision == "src":
        (repository / collision).mkdir()
        (repository / collision / "owner.py").write_text("user content")
    else:
        (repository / collision).write_text("user content")
    before = tree(repository)
    with pytest.raises(GeneratorError, match="unexpected existing path"):
        generate_project(repository, into_existing=True)
    assert tree(repository) == before


def test_generation_failure_is_staged(repository: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from agentready.render import generator

    before = tree(repository)

    def fail(*args: object, **kwargs: object) -> None:
        raise OSError("injected renderer failure")

    monkeypatch.setattr(generator.copier, "run_copy", fail)
    with pytest.raises(GeneratorError, match="injected renderer failure"):
        generate_project(repository, into_existing=True)
    assert tree(repository) == before


def test_publication_failure_rolls_back(repository: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from agentready.render.existing import initialize_existing

    before = tree(repository)

    def render(staged: Path):
        project = generate_project(staged)
        real_open = Path.open

        def fail(path: Path, *args, **kwargs):
            if path == repository / "pyproject.toml" and args and args[0] == "xb":
                raise OSError("injected publication failure")
            return real_open(path, *args, **kwargs)

        monkeypatch.setattr(Path, "open", fail)
        return project

    with pytest.raises(OSError, match="injected publication failure"):
        initialize_existing(repository, render)
    assert tree(repository) == before
    assert {p.name for p in repository.iterdir()} == {
        ".git",
        "README.md",
        ".gitignore",
        "LICENSE",
        ".gitattributes",
    }


def test_legacy_nonempty_guard_and_fresh_directory(repository: Path, tmp_path: Path) -> None:
    before = tree(repository)
    with pytest.raises(GeneratorError, match="must be empty"):
        generate_project(repository)
    assert tree(repository) == before
    fresh = tmp_path / "fresh-project"
    generate_project(fresh)
    assert inspect(fresh).healthy
    empty = tmp_path / "empty-project"
    empty.mkdir()
    assert main(["init", str(empty), "--into-existing"]) == 0
    assert inspect(empty).healthy


def test_invalid_bootstrap_encoding_is_rejected(repository: Path) -> None:
    (repository / "README.md").write_bytes(b"\xff not UTF8")
    before = tree(repository)
    with pytest.raises(GeneratorError, match="must be UTF-8"):
        generate_project(repository, into_existing=True)
    assert tree(repository) == before


def test_unsafe_git_link_is_rejected(repository: Path, tmp_path: Path) -> None:
    external = tmp_path / "external"
    external.mkdir()
    link = repository / ".git/unsafe"
    if os.name == "nt":
        subprocess.run(
            ["cmd", "/c", "mklink", "/J", str(link), str(external)], check=True, capture_output=True
        )
    else:
        link.symlink_to(external, target_is_directory=True)
    try:
        with pytest.raises(GeneratorError, match="unsafe symlink or junction"):
            generate_project(repository, into_existing=True)
        assert not (repository / ".agentready").exists()
    finally:
        if os.name == "nt":
            link.rmdir()
        else:
            link.unlink()


def test_parent_traversal_and_linked_worktree_rejected(repository: Path, tmp_path: Path) -> None:
    with pytest.raises(GeneratorError, match=r"without '\.\.'"):
        generate_project(repository / ".." / repository.name, into_existing=True)
    root = tmp_path / "linked-project"
    root.mkdir()
    (root / ".git").write_text("gitdir: ../../external\n")
    before = tree(root)
    with pytest.raises(GeneratorError, match="linked worktrees"):
        generate_project(root, into_existing=True)
    assert tree(root) == before
