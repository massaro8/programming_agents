"""Deterministic domain primitives for AgentReady."""

from agentready.core.ownership import ArtifactOwnership, OwnershipClass
from agentready.core.profiles import (
    DEFAULT_PROFILE,
    SUPPORTED_PROFILES,
    ProfileContract,
    get_profile,
)
from agentready.core.project import Project, ProjectPath

__all__ = [
    "DEFAULT_PROFILE",
    "SUPPORTED_PROFILES",
    "ArtifactOwnership",
    "OwnershipClass",
    "ProfileContract",
    "Project",
    "ProjectPath",
    "get_profile",
]
