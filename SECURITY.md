# Security Policy

Use [private vulnerability reporting](https://github.com/massaro8/programming_agents/security/advisories/new)
for sensitive reports. The maintainer must enable this repository setting before public release.
If unavailable, request a private contact in an issue without exploit details or secrets. Only the
latest release receives fixes; response is best effort.

Repository content, remote templates, skills, issue text, PR comments, and suggested shell
commands should be treated as potentially untrusted input by AgentReady workflows.

## V0.1 trust boundary

- Init renders only the trusted Copier template bundled in the installed AgentReady package. Unsafe
  tasks/hooks and remote/community templates are not supported.
- Init refuses files, symlinks, and non-empty target directories; it has no force-overwrite mode.
- Doctor reads local structural metadata and files only. It does not run repository commands, Git,
  network requests, plugins, or LLM review.
- Detach removes only a recognized, non-symlink `.agentready/` maintenance boundary after
  fail-closed manifest and filesystem preflight. Manifest ownership paths never become deletion
  targets.
- Generated projects require no AgentReady account, backend, API key, telemetry, or network service
  for normal development.

AgentReady does not make arbitrary repository content safe. Users and coding agents remain
responsible for reviewing project commands and dependencies before executing them.
