import os
from pathlib import Path

import pytest

from agentready.core.project import Project, ProjectPath


def test_project_requires_absolute_root_and_normalizes_lexically() -> None:
    project = Project(Path.cwd() / "workspace" / ".." / "repo")
    assert project.path == Path.cwd() / "repo"


@pytest.mark.parametrize("value", [Path(""), Path("."), Path("../file"), Path("a/../file")])
def test_project_path_rejects_empty_or_traversal(value: Path) -> None:
    with pytest.raises(ValueError):
        ProjectPath(value)


def test_project_path_rejects_absolute_and_wrong_types() -> None:
    with pytest.raises(ValueError):
        ProjectPath(Path.cwd() / "file.txt")
    with pytest.raises(ValueError):
        ProjectPath(Path(f"{os.sep}file.txt"))
    with pytest.raises(TypeError):
        ProjectPath("file.txt")  # type: ignore[arg-type]


def test_path_conversion_and_cwd_independence(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path / "repo"
    project = Project(root)
    relative = ProjectPath(Path("src") / "main.py")
    assert project.path_for(relative) == project.path / "src" / "main.py"
    assert project.relative_path(project.path / "src" / "main.py") == relative
    monkeypatch.chdir(tmp_path.parent)
    assert project.path_for(relative) == root / "src" / "main.py"


def test_relative_path_rejects_root_outside_and_relative_inputs() -> None:
    project = Project(Path.cwd() / "repo")
    with pytest.raises(ValueError):
        project.relative_path(project.path)
    with pytest.raises(ValueError):
        project.relative_path(project.path.parent / "other" / "file")
    with pytest.raises(ValueError):
        project.relative_path(Path("src/main.py"))


def test_value_equality_and_hashing() -> None:
    assert ProjectPath(Path("src") / "main.py") == ProjectPath(Path("src/main.py"))
    assert hash(ProjectPath(Path("src/main.py"))) == hash(ProjectPath(Path("src") / "main.py"))
