# Security workflow

Security work has two modes. A review-only question or target requires no READY item: perform
read-only analysis, make no production edits, and return evidence-backed findings, risks, and a
recommended next work item. Do not turn review findings into implementation without a separate
authorized work item.

SECURITY implementation is HIGH RISK and requires a READY SECURITY item, a strong coordinator
before implementation, and an independent final review. Define trust boundary → confirm safely →
analyze impact → design minimum mitigation → implement → add security regression test → run normal
regression gates → evaluate security documentation impact → complete record and changelog → DONE →
sync registry → stop.

Do not include offensive exploitation guidance. If safe completion is uncertain, record the blocker, mark BLOCKED, and stop.
