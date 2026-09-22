# Testing standard

Test observable behavior with deterministic inputs. Use unit tests for isolated rules, add
integration tests only when real boundaries or side effects appear, and add a regression test for
every fixed bug. Do not create integration or end-to-end directories before they are needed.

Run the narrowest relevant test first, then Ruff formatting/lint, mypy, and the full test suite
before completion.
