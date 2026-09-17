"""Safe removal of AgentReady maintenance metadata."""

from agentready.detach.service import DetachError, detach_project

__all__ = ["DetachError", "detach_project"]
