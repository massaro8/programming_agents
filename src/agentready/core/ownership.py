"""Ownership vocabulary for generated repository artifacts."""

from dataclasses import dataclass
from enum import Enum

from agentready.core.project import ProjectPath


class OwnershipClass(Enum):
    """Canonical artifact classes; classification does not define lifecycle policy."""

    PROJECT_OWNED = "project_owned"
    SHARED = "shared"
    GENERATED = "generated"


@dataclass(frozen=True, slots=True)
class ArtifactOwnership:
    """Associate one repository-relative artifact path with one ownership class."""

    path: ProjectPath
    ownership: OwnershipClass

    def __post_init__(self) -> None:
        if not isinstance(self.path, ProjectPath):
            raise TypeError("path must be a ProjectPath")
        if not isinstance(self.ownership, OwnershipClass):
            raise TypeError("ownership must be an OwnershipClass")
