# Testing standard

Test observable behavior with deterministic inputs. Application behavior must be testable without
live services, internet, vendor credentials, cloud accounts, or developer-local state. Prefer owned
fake ports/collaborators over mocks of private implementation functions. Normal tests must not use
live network access; use deterministic boundary doubles and fixtures instead.

Use temporary directories and files for filesystem behavior. Where useful, test adapters at their
actual boundary for serialization, response parsing, error translation, and configuration mapping
with controlled inputs. Add database integration tests only when a real database boundary exists.
Keep end-to-end tests to a small number of critical assembled paths. Once multiple capabilities
exist, mirror ownership approximately under `tests/modules/<capability>/`. Do not create unused
unit/integration/e2e directory trees during initialization. Add a regression test for every fixed
bug.

Run the narrowest relevant test first, then Ruff formatting/lint, mypy, and the full test suite
before completion.
