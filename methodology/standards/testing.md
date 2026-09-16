# Testing Standard

- Unit tests prove deterministic domain/application behavior.
- Integration tests prove real adapter/storage/filesystem/network boundaries when needed.
- Contract tests protect public API/event/schema compatibility.
- Every reproducible bug should gain a regression test unless automation is genuinely impractical.
- E2E tests cover only critical flows.
- Coverage is a signal, not a correctness target by itself.
- Local feedback starts narrow; CI remains authoritative.
