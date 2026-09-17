# Codebase Map

Structure fingerprint: `bce7489e8295`

Do not edit manually. Regenerate with `python scripts/generate_codebase_map.py`.

## Primary entry points

- CLI: `src/agentready/cli.py:main`
- Shared agent policy: `AGENTS.md`
- Product scope: `docs/PRODUCT_SPEC.md`
- Architecture: `docs/ARCHITECTURE.md`
- Roadmap: `docs/ROADMAP.md`
- Detachment contract: `docs/DETACHMENT_CONTRACT.md`

## Repository areas

### `.agents`
- `.agents/skills/bug-investigation/SKILL.md`
- `.agents/skills/feature-builder/SKILL.md`
- `.agents/skills/project-bootstrap/SKILL.md`
- `.agents/skills/repo-explore/SKILL.md`

### `.claude`
- `.claude/skills/bug-investigation/SKILL.md`
- `.claude/skills/feature-builder/SKILL.md`
- `.claude/skills/repo-explore/SKILL.md`

### `.github`
- `.github/ISSUE_TEMPLATE/bug.yml`
- `.github/ISSUE_TEMPLATE/feature.yml`
- `.github/pull_request_template.md`
- `.github/workflows/ci.yml`

### `.gitignore`
- `.gitignore`

### `.python-version`
- `.python-version`

### `AGENTS.md`
- `AGENTS.md`

### `CLAUDE.md`
- `CLAUDE.md`

### `CODE_OF_CONDUCT.md`
- `CODE_OF_CONDUCT.md`

### `CONTRIBUTING.md`
- `CONTRIBUTING.md`

### `LICENSE`
- `LICENSE`

### `OPERATING_PLAN.md`
- `OPERATING_PLAN.md`

### `README.md`
- `README.md`

### `SECURITY.md`
- `SECURITY.md`

### `START_SOL_COORDINATOR.md`
- `START_SOL_COORDINATOR.md`

### `docs`
- `docs/ARCHITECTURE.md`
- `docs/DETACHMENT_CONTRACT.md`
- `docs/PRACTICAL_VALIDATION_PLAN.md`
- `docs/PRODUCT_SPEC.md`
- `docs/ROADMAP.md`
- `docs/adr/0000-template.md`
- `docs/audits/BOOT_001_AUDIT.md`
- `docs/audits/BOOT_002_AUDIT.md`
- `docs/audits/DET_001_AUDIT.md`
- `docs/audits/DET_002_AUDIT.md`
- `docs/audits/DOC_001_AUDIT.md`
- `docs/audits/DOC_002_AUDIT.md`
- `docs/audits/INIT_001_AUDIT.md`
- `docs/audits/INIT_002_AUDIT.md`
- `docs/audits/PHASE0_BASELINE_AUDIT.md`
- `docs/audits/REL_001_AUDIT.md`
- `docs/features/template.md`
- `docs/generated/CODEBASE_MAP.md`

### `methodology`
- `methodology/core/context-policy.md`
- `methodology/core/definition-of-done.md`
- `methodology/core/operating-principles.md`
- `methodology/standards/dependencies.md`
- `methodology/standards/testing.md`
- `methodology/workflows/audit.md`
- `methodology/workflows/bugfix.md`
- `methodology/workflows/feature.md`
- `methodology/workflows/refactor.md`

### `pyproject.toml`
- `pyproject.toml`

### `schemas`
- `schemas/audit.schema.json`
- `schemas/doctor.schema.json`
- `schemas/manifest.schema.json`

### `scripts`
- `scripts/generate_codebase_map.py`

### `src`
- `src/agentready/__init__.py`
- `src/agentready/cli.py`
- `src/agentready/core/__init__.py`
- `src/agentready/core/ownership.py`
- `src/agentready/core/project.py`
- `src/agentready/detach/__init__.py`
- `src/agentready/detach/service.py`
- `src/agentready/doctor/__init__.py`
- `src/agentready/doctor/inspector.py`
- `src/agentready/doctor/serialization.py`
- `src/agentready/render/__init__.py`
- `src/agentready/render/generator.py`
- `src/agentready/templates/__init__.py`
- `src/agentready/templates/python/__init__.py`
- `src/agentready/templates/python/copier.yml`
- `src/agentready/templates/python/template/.agentready/manifest.toml.jinja`
- `src/agentready/templates/python/template/.github/workflows/ci.yml`
- `src/agentready/templates/python/template/.gitignore`
- `src/agentready/templates/python/template/.python-version`
- `src/agentready/templates/python/template/AGENTS.md`
- `src/agentready/templates/python/template/CLAUDE.md`
- `src/agentready/templates/python/template/README.md.jinja`
- `src/agentready/templates/python/template/docs/ARCHITECTURE.md`
- `src/agentready/templates/python/template/docs/agent/standards/testing.md`
- `src/agentready/templates/python/template/docs/agent/workflows/feature.md`
- `src/agentready/templates/python/template/pyproject.toml.jinja`
- `src/agentready/templates/python/template/src/{{ package_name }}/__init__.py.jinja`
- `src/agentready/templates/python/template/src/{{ package_name }}/main.py`
- `src/agentready/templates/python/template/tests/test_main.py.jinja`

### `tests`
- `tests/test_detach.py`
- `tests/test_detached_project.py`
- `tests/test_doctor.py`
- `tests/test_doctor_json.py`
- `tests/test_generated_project.py`
- `tests/test_init.py`
- `tests/test_ownership.py`
- `tests/test_project.py`
- `tests/test_smoke.py`

### `uv.lock`
- `uv.lock`
