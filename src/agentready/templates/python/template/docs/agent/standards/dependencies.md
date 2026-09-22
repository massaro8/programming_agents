# Dependency standard

Prefer the standard library when it is reasonable, then reuse an existing dependency before adding
one. A new production dependency needs a concrete requirement and a short justification. Update
`pyproject.toml` and lock state coherently and verify the resulting environment.

Do not add dependency-management infrastructure unnecessarily. AgentReady, Copier, and Jinja are
generator tooling and must never become application dependencies.
