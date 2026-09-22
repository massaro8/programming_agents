# Bugfix workflow

1. Reproduce the failure with a deterministic command or test.
2. Localize the failing path and identify the root cause.
3. Add a regression test that fails for that cause.
4. Implement the smallest correct fix; do not use random patch loops.
5. Run the regression test, neighboring tests, and the full required gates.
