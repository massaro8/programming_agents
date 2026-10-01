# Security standard

Treat external input, filesystem paths, subprocesses, deserialization, credentials, and dependency
trust as security boundaries. Validate at boundaries, minimize authority, avoid exposing secrets,
and add regression coverage for security-sensitive behavior. Escalate high-risk uncertainty for
coordinator review. For user or external paths, normalize carefully and check intended containment
at use, including relevant symlink and traversal behavior; do not assume destructive intent.

Prefer subprocess argument arrays. Avoid shell execution unless required, and never interpolate
untrusted strings into shell commands. Use data-only serialization and safe readers for untrusted
input; do not use unsafe object deserialization. Network operations need finite timeouts. Validate
and limit user-controlled destinations when relevant, and do not blindly follow arbitrary external
destinations in security-sensitive flows.

Redact tokens, passwords, credentials, and sensitive payload fields from logs and errors. Libraries
must not configure logging globally. Do not include offensive exploitation instructions in project
guidance.
