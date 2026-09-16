from pathlib import Path

import pytest

from agentready.core.ownership import ArtifactOwnership, OwnershipClass
from agentready.core.project import ProjectPath


def test_canonical_ownership_classes() -> None:
    assert list(OwnershipClass) == [
        OwnershipClass.PROJECT_OWNED,
        OwnershipClass.SHARED,
        OwnershipClass.GENERATED,
    ]


def test_artifact_ownership_association_and_validation() -> None:
    path = ProjectPath(Path("docs/guide.md"))
    association = ArtifactOwnership(path, OwnershipClass.SHARED)
    assert association.path == path
    assert association.ownership is OwnershipClass.SHARED
    assert association == ArtifactOwnership(path, OwnershipClass.SHARED)
    assert hash(association) == hash(ArtifactOwnership(path, OwnershipClass.SHARED))
    with pytest.raises(TypeError):
        ArtifactOwnership("docs/guide.md", OwnershipClass.SHARED)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        ArtifactOwnership(path, "shared")  # type: ignore[arg-type]
