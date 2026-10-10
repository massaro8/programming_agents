# FINAL-FIX-001 — AgentReady final stabilization

## 1. Initial state

Started: 2026-10-09. Finalized: 2026-10-10. Repository: `C:/z_personale/programming_agents`.
HEAD: `ea2d0bd7366bbcb96f01fd6ccdfad99b73868993`.
The working tree already had 36 modified tracked paths and 10 untracked status entries.
The initial snapshot records 227 repository files; user changes are preserved.
Previous adversarial qualification: 248 passed, four privilege-related skips;
one P0, three P1 and one P2 corrected, with no remaining reproduced P0/P1.

Evidence and temporary work are in `C:/z_personale/agentready_use_cases/final_fix_001`.
`initial.json` records Git status and SHA256 of tracked/non-ignored user files; `initial.diff`
records the starting diff. No commit, tag, push, publication or remote CI is authorized/performed.

Verification was defined before editing: reuse existing boundary/concurrency/CLI regressions,
run every test file in disjoint groups, run static gates, rebuild wheel/sdist, then install and
qualify all profiles and detachment. No speculative implementation change is planned.

## 2. Findings reviewed

- Read the latest adversarial audit, architecture, Detachment Contract, current Git diff,
  filesystem lifecycle changes, local write guard, CLI error handling and packaging configuration.
- Init and detach reject symlinks/junctions at the target and ancestors. Detach inventories and
  rechecks its fixed `.agentready/` boundary. Doctor rejects unsafe roots/artifact paths without
  executing project tools or repairing user data.
- Checkpoint existence checks and journal/config read/modify/write are inside an exclusive
  artifact guard. Competing writers fail; ordinary exceptions release the guard; stale locks
  are preserved and require explicit owner confirmation before removal.
- CLI handles ordinary init filesystem errors and redirected Windows output without forcing an
  output encoding. JSON serialization uses ASCII escapes. Existing CP1252/Unicode regression
  exercises actual init and detach subprocesses.
- Version is declared as 0.1.0 in pyproject and read by the CLI from installed metadata.
  Trusted bundled templates and standalone scripts are packaged without an application runtime
  dependency on AgentReady.

No additional implementation defect has been confirmed during review. Qualification results
below determine the final recommendation.

## 3. Actual fixes required

Documentation only:

1. `docs/SKILL_QA_AND_CONTINUITY.md` incorrectly said all hook mutations support `--dry-run`.
   Actual `uv run agentready hooks record --help` lists no such flag. The wording now names
   configure/enable/disable and excludes recording. This is a small documentation inconsistency,
   not a missing feature; no new CLI option is added.
2. `docs/USER_GUIDE.md` now explains supported busy/stale-lock retry, explicit checkpoint replacement,
   owner restoration of malformed hook configuration, sequential registry writes, and recovery
   from partial detach using an original trusted manifest. No automatic recovery is introduced.

No production code, dependency, template, test or behavior is changed. The generated codebase map
is regenerated solely to include this audit. Existing regressions are reused; no uncovered
concrete risk requires another test.

## 4. Regression results

The eight reused fault probes passed: three actual renderer write failures, second-index
write failure and explicit retry, partial checkpoint replacement, partial hook configuration,
late detach failure after manifest deletion, and a valid project-owned shared-file edit.
Evidence: external `fault.log` and `fault-probe-run/results.json`. Ordinary exceptions release
locks; partial content is detected; a detach retry without a valid manifest refuses safely.

The first external parallel runner completed group 2 (60 passed, one skipped), but its
900-second harness limit interrupted collection of the slower groups' results. This is a
qualification harness failure, not a reproduced product failure. Affected groups are rerun
with cached offline dependencies, direct log files and a 3600-second bound. No timed-out group
is counted as passing. The completed disjoint groups cover every collected test file exactly
once in the final totals:

| Group | Passed | Skipped | Result |
| --- | ---: | ---: | --- |
| Boundary, bootstrap, map, detach, detached projects | 39 | 2 | Exit 0; 885.53 s |
| Doctor, JSON, evolution, CLI UX | 60 | 1 | Exit 0; 533.57 s |
| Generated architecture, context, project | 45 | 0 | Exit 0; 749.35 s |
| Remaining test files | 104 | 1 | Exit 0; 757.28 s |
| Total | 248 | 4 | No failures |

The four Windows symlink privilege skips are not passes. Actual Windows junction regressions,
competing checkpoint/evidence writers, exception cleanup, stale-lock diagnostics, Unicode
redirected output, malformed inputs and permission errors pass. Results are retained in
`final-gates-results.json` (group 2), `retry-gates-results.json` (groups 1/3/4) and their logs.

## 5. Final quality gates

Ruff lint, Ruff format (116 files), mypy (22 source files), generated codebase-map check,
pytest collection (252 tests), and fresh offline wheel/sdist build passed. Complete pytest
qualification is 248 passed / 4 skipped. Installed generated-project verification, skill checks,
doctor and detach pass as detailed below. Final static checks and preservation comparison
were repeated after resuming; source and package inputs remain identical to those qualified.

## 6. Wheel/sdist qualification

Fresh wheel and sdist were built with `uv build --offline --out-dir
C:/z_personale/agentready_use_cases/final_fix_001/artifacts`. The build created the wheel from
the new sdist. No prior artifact was reused. `build.log`, `qualification.log`,
`qualification-results.json` and `artifact-sha256.json` retain evidence outside the repository.

Archive metadata and installed CLI both report exactly 0.1.0. Contents include trusted Copier
templates, all eight canonical skills/evaluation fixtures, standalone project/registry/skill
tools, and the filesystem guard. The sdist includes README, license and changelog; no environment
or bytecode is bundled. Wheel and sdist each install offline into a separate clean environment.

Installed wheel CLI generates minimal, application and service projects. Each passes doctor
without ordinary-file changes, bootstrap, complete project verification and skill checks;
detach preserves ordinary files, and verification passes again after metadata removal.
All 34 recorded qualification commands exit successfully. Each application executes without
AgentReady or Copier installed. The installed sdist also
passes version/help, init, read-only doctor and ordinary-file-preserving detach.

SHA256:

| Artifact | SHA256 |
| --- | --- |
| `agentready-0.1.0-py3-none-any.whl` | `6bd533d92b6868cce8a0e7c0d0861a931cf3598e0e099cbe8cfa4add8d09602a` |
| `agentready-0.1.0.tar.gz` | `d8bb92f1668cd49468c9a585248b6dfd827b223d6760cea9de9fbf1d242d9e6d` |

Hashes match the previously corrected build because packaged inputs are unchanged and the
build is deterministic. These are independently rebuilt and installed artifacts, not reused files.

## 7. Residual documented limitations

- Windows symlink privileges may be unavailable; skips are not passes. Real junction regressions
  are executed where available.
- Guards are local preflights/exclusive writer markers, not protection against hostile path
  replacement or concurrent manual edits. Registry updates require one writer.
- Killed writers can leave locks; no lock is stolen automatically. Partial JSON/detach failure
  is diagnosable, not transactional rollback. These are accepted limits, not confirmed defects.
- Offline qualification depends on cached dependencies and uv offline mode, not an OS network
  block or complete offline reproducibility. Remote CI remains outside this task.

## 8. Git status and cleanup

Initial status is retained in the external snapshot. Preservation comparison confirms only
`docs/USER_GUIDE.md`, `docs/SKILL_QA_AND_CONTINUITY.md` and the generated map changed; this audit
is the sole added path. No initial file was deleted. All existing source, templates, tests and
other user changes are byte-for-byte preserved. HEAD is unchanged. Status: 36 modified tracked
paths and 11 untracked status entries (the initial 10 plus this audit).

No unexpected temporary archives, locks or partial files were found outside ignored build/cache
directories. Existing ignored `dist/` artifacts were present before this task and are retained;
qualified release artifacts are in the external workspace. All six real work records are DONE;
the BACKLOG entry is a reusable template. README/changelog/version references are coherent.
No commit, tag, push or publication is performed. Final status is saved externally in `final.json`.

## 9. Release recommendation

READY — FREEZE AND RELEASE

No additional implementation defect was reproduced. Required local gates and freshly rebuilt
artifact qualification pass. v0.1.0 implementation is frozen at the preserved working-tree
source; only the documented corrections and audit/map update were needed in this task.
Accepted limitations are listed separately above. Release approval does not imply publication:
no commit, tag, push, remote CI or publish action was performed.
