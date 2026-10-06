# Skill QA, optional hooks and work continuity

All tools are local and provider-neutral. Generated projects use the same stdlib implementations
as standalone scripts; they do not import AgentReady. Their configuration and work evidence are
project-owned. Source utilities and bundled eval fixtures are shared, subject to explicit merges.

## Skill Contract v1

A skill describes a repeatable multi-step procedure. Keep the existing `SKILL.md` format:
single-line `name:` and `description:` frontmatter, followed by nonempty level-two sections.
The supported frontmatter is a small existing convention, not a general YAML parser.

| Concept | Heading (existing aliases accepted) |
| --- | --- |
| Identity | frontmatter name matching directory |
| Purpose | Purpose |
| Positive triggers | Positive triggers |
| Negative triggers | Exclusions or Negative triggers |
| Scope | Scope or Inputs and preconditions |
| Process | Process or Procedure |
| Verification | Verification or Evidence of completion |
| Failure | Failure / escalation or Escalate or stop |
| Output | Output contract |
| Supporting references | optional Markdown links relative to the skill directory |

Missing required structure, duplicate identities/headings, and unsafe/broken local links are
ERRORs. Missing exclusions and duplicate descriptions are WARNINGs. Frontmatter over 1024
characters is INFO. Prose length and subjective writing style are not blocking opinions.
Local links can use `..` within the repository; escaping links and linked symlinks/junctions fail.
HTTP(S), mail and same-document fragment links are not fetched or verified.

`agentready skill check [name] --format json` reports individual severities. Doctor adds fixed
`skills.contract`, `skills.evals`, `hooks.config`, and `work.checkpoints` checks. Its schema-1
PASS/FAIL wire contract and keys remain unchanged: ERROR means fail; WARNING/INFO appear explicitly
in messages and do not make a repository unhealthy. Legacy schema-1 repositories without eval
artifacts receive advisory warnings for missing v1 sections; malformed identity/references still
fail. Existing ownership manifests need not list the additive capability files.

## Portable eval definitions and scoring

Optional `.agents/skills/<name>/evals/cases.json` has this shape:

```json
{
  "schema": 1,
  "skill": "feature-builder",
  "include": ["implement"],
  "exclude": ["typo"],
  "cases": [
    {"id": "positive", "task": "Implement pagination", "trigger": true,
     "criteria": ["affected_tests_identified", "validation_executed"]},
    {"id": "negative", "task": "Fix typo", "trigger": false, "criteria": []}
  ]
}
```

Trigger evaluation is deliberately lexical: a case matches any include term and no exclude term,
case-insensitively. Fixtures test the declared routing examples, not a model's natural-language
understanding. Skill prose remains authoritative; keep terms/examples consistent with it.

Behavioral cases mean GIVEN the task, WHEN an external agent executes the workflow, EXPECT the
listed observable criteria. An external runner supplies repository-relative `results.json`:

```json
{
  "schema": 1,
  "skill": "feature-builder",
  "variant": "with-skill",
  "cases": {
    "positive": {
      "affected_tests_identified": {"passed": true, "evidence": "tests/test_orders.py"},
      "validation_executed": {"passed": true, "evidence": "pytest: exit 0"}
    }
  }
}
```

`agentready skill eval feature-builder [--case positive] [--results results.json] --format json`
validates definitions and results, scores boolean observations, and reports evidence, score/total
and overall pass. Missing observations score zero; a passing observation requires nonempty
evidence. Without results only trigger fixtures are scored; behavioral observations remain
unexecuted (MISSING), never fabricated. Use variant `without-skill` for a baseline comparison.
The definition JSON is itself the portable export: no provider, execution runner or downloads.
Supplied evidence is an external assertion, not independently proven behavior.

## Optional hooks

**Hooks are disabled by default and require explicit user activation.**
**AgentReady does not change global agent configuration.**

The project-local `docs/agent/hooks.json` uses schema 1 and named built-in recipes, following
existing JSON machine-artifact conventions and a bounded stdlib reader/writer shared with evals
and checkpoints. It is created only by an explicit configure/enable/disable action. Init never
activates recipes; this work adds no update engine.
No host integration is installed automatically. A developer or existing host calls the local
preflight/recorder commands explicitly; enabling a recipe makes that interface active, not an
automatic interception of every shell command.

```text
agentready hooks list
agentready hooks inspect safe-shell
agentready hooks configure safe-shell --mode block --protected-branches main release
agentready hooks enable safe-shell --dry-run
agentready hooks enable safe-shell
agentready hooks status
agentready hooks check "git push origin feature" --branch feature
agentready hooks disable safe-shell
```

`safe-shell` reports understandable rules for recursive deletion, force push, hard reset and
protected-branch push. Configure `warn` (allowed with findings) or `block` (exit 1). Use
`--exclude <rule IDs>` to exclude individual rules; an empty `--exclude` clears exclusions.
An unknown current branch is conservatively treated as potentially protected for a push.
Protected destinations include fully qualified `refs/heads/<branch>` targets.
This bounded lexical preflight is not a shell parser or security sandbox. It never executes
commands. A caller must honor its exit status to enforce blocking.

`evidence-recorder` explicitly ingests `hooks record "pytest tests/test_orders.py" --exit-status 0
--work W001` after activation. It records only the executable name, caller-reported exit status,
work ID, UTC timestamp and source `external-report` in `docs/work/evidence/hooks.json`. It accepts
signed or unsigned 32-bit native exit statuses, including Windows codes above 255, and captures
no arguments, output, environment, or shell history. Output capture is unsupported and invalid
configuration fails closed. The bounded journal requires explicit archiving after 200 entries.
The record is not proof that a command ran. Completion interception is deferred because there is
no existing host completion callback; no completion evidence is fabricated.

All mutations offer `--dry-run`. Unknown recipes/modes/fields are rejected; unrelated project
configuration is not touched. Disable writes an explicit disabled state without deleting evidence.
Detach preserves local recipes, configuration and evidence as usable project files.

## Work checkpoints

```text
agentready checkpoint W001 --state checkpoint-input.json --dry-run
agentready checkpoint W001 --state checkpoint-input.json
agentready resume W001 --format json
```

State input contains exactly `objective`, `files`, `decisions`, `validation`, `risks`, `questions`,
and `next_step`. Objective/next_step are short strings; the others are lists of short strings.
Files are repository-relative file paths. Each list has at most 50 entries and each summary at
most 2000 characters. Omit `--state` to create a minimal checkpoint pointing to the work title.
Existing checkpoints require explicit `--replace`. Store only durable facts, never transcripts,
private reasoning, shell history or raw logs. Recognizable credential patterns are rejected;
users must still keep arbitrary secrets out of their summaries.

Checkpoint files are project-owned `docs/work/checkpoints/Wxxx.json`. They capture current status,
HEAD (or null outside Git), hashes of referenced files and the work specification, and a digest
of tracked file contents. Resume is read-only and compact. It reports revision, status, referenced
file and tracked-file changes, missing files, and potentially stale validation. An already DONE
item is not actionable; creating a checkpoint for it fails. Doctor detects malformed/orphaned
checkpoints as errors and stale checkpoints as warnings. No semantic merge is attempted.
Untracked changes outside listed files are not covered. Git absence is supported with file hashes.

Authority is always code/tests/config > accepted decisions > work item > checkpoint. Recheck
stale claims before continuing. These files survive detach without a memory database or service.

For another target put `--path <repository>` immediately after the AgentReady command, before its
remaining arguments. Generated repositories expose the same actions through
`python scripts/project.py skill ...`, `hooks ...`, `checkpoint ...`, and `resume ...`, or their
standalone scripts. Direct script help shows the full supported arguments.
