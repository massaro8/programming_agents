# Bugfix Workflow

Reproduce -> Localize -> Explain root cause -> Add regression test -> Minimal fix -> Prove regression
passes -> Neighboring validation -> Required gates -> Check whether the same bug pattern exists nearby.

Stop random edit/retry loops. If the same substantive failure repeats, re-investigate before editing again.
