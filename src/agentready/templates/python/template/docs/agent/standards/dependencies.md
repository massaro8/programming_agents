# Dependency standard

Prefer the standard library when it is reasonable, then reuse an existing dependency before adding
one. A new production dependency needs a concrete requirement and a short justification. Update
`pyproject.toml` and lock state coherently and verify the resulting environment.

Import only declared direct dependencies; do not rely intentionally on transitive packages. Remove
unused direct dependencies and keep `uv.lock` coherent. Choose version constraints for the
project's compatibility and support needs, not by pinning habit. Avoid broad upgrades unrelated to
the work item. For additions and upgrades, review relevant release notes, compatibility, and known
security impact, then run focused compatibility tests and required project checks.

Do not add dependency-management infrastructure unnecessarily. AgentReady, Copier, and Jinja are
generator tooling and must never become application dependencies.
