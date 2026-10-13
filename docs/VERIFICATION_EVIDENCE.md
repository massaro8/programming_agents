# Verification evidence

New projects enable evidence-backed work completion through `docs/verification.json`.
Create and accept a work item, transition it to IN_PROGRESS, implement its scope, refresh
derived metadata with `python scripts/project.py sync`, then run:

```text
python scripts/project.py verify --work W001
python scripts/project.py work transition W001 DONE
python scripts/project.py sync
```

Complete the implementation record, documentation impact and changelog before DONE.
`verify` without `--work` remains a general project check and does not produce a work receipt.

The receipt in `docs/verification/W001.json` records executed commands, exit codes, timestamp,
work identity/type, required verification stages, tool identity/version where available, and
SHA256 hashes of bounded repository inputs. It excludes environment caches, builds, maintenance
metadata, other work records, lifecycle status and completion prose. Accepted specification
content remains hashed. New or changed relevant files invalidate the receipt; changed tools,
configuration or expiration also require verification again. Documentation work runs registry,
skill and navigation checks; other work runs the selected family's complete local contract.
Python verification builds its package; CloudFormation runs cfn-lint, Guard and negative fixtures.

Compatibility: existing records without `Verification evidence: REQUIRED` remain legacy records,
including previously completed work. Newly created records in configured projects receive that
marker. To migrate an existing active item explicitly, add the marker and run real verification
before DONE. No historical accepted record is rewritten automatically. Historical DONE receipts
are checked for recorded success, not freshness against subsequent unrelated development.

The snapshot is bounded to 10,000 files / 100 MiB, and receipts to 128 KiB. Larger projects must
adapt their verification scope deliberately rather than silently accepting incomplete evidence.
The tool stores hashes and compact outcomes, not file contents or conversation transcripts.

Repository-local evidence improves correctness and staleness detection but does not guarantee
protection against a malicious agent that can edit all local files. There are no signatures,
external evidence service, host enforcement claims or independent attestation.
