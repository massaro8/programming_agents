# Codebase Map

Structure fingerprint: `19706cab4516`

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
- `docs/audits/FLOW_001_AUDIT.md`
- `docs/audits/FLOW_002_AUDIT.md`
- `docs/audits/FLOW_003_AUDIT.md`
- `docs/audits/HARDEN_001_AUDIT.md`
- `docs/audits/INIT_001_AUDIT.md`
- `docs/audits/INIT_002_AUDIT.md`
- `docs/audits/PHASE0_BASELINE_AUDIT.md`
- `docs/audits/PYT_001_AUDIT.md`
- `docs/audits/REL_001_AUDIT.md`
- `docs/generated/CODEBASE_MAP.md`
- `docs/work/templates/feature.md`

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
- `src/agentready/bootstrap.py`
- `src/agentready/cli.py`
- `src/agentready/core/__init__.py`
- `src/agentready/core/ownership.py`
- `src/agentready/core/profiles.py`
- `src/agentready/core/project.py`
- `src/agentready/detach/__init__.py`
- `src/agentready/detach/service.py`
- `src/agentready/doctor/__init__.py`
- `src/agentready/doctor/codebase_map.py`
- `src/agentready/doctor/inspector.py`
- `src/agentready/doctor/serialization.py`
- `src/agentready/doctor/work.py`
- `src/agentready/render/__init__.py`
- `src/agentready/render/generator.py`
- `src/agentready/templates/__init__.py`
- `src/agentready/templates/python/__init__.py`
- `src/agentready/templates/python/copier.yml`
- `src/agentready/templates/python/template/.agentready/manifest.toml.jinja`
- `src/agentready/templates/python/template/.agents/skills/bug-investigation/SKILL.md`
- `src/agentready/templates/python/template/.agents/skills/documentation/SKILL.md`
- `src/agentready/templates/python/template/.agents/skills/feature-builder/SKILL.md`
- `src/agentready/templates/python/template/.agents/skills/maintenance/SKILL.md`
- `src/agentready/templates/python/template/.agents/skills/module-placement/SKILL.md`
- `src/agentready/templates/python/template/.agents/skills/refactoring/SKILL.md`
- `src/agentready/templates/python/template/.agents/skills/repo-explore/SKILL.md`
- `src/agentready/templates/python/template/.agents/skills/security-review/SKILL.md`
- `src/agentready/templates/python/template/.claude/skills/bug-investigation/SKILL.md`
- `src/agentready/templates/python/template/.claude/skills/documentation/SKILL.md`
- `src/agentready/templates/python/template/.claude/skills/feature-builder/SKILL.md`
- `src/agentready/templates/python/template/.claude/skills/maintenance/SKILL.md`
- `src/agentready/templates/python/template/.claude/skills/module-placement/SKILL.md`
- `src/agentready/templates/python/template/.claude/skills/refactoring/SKILL.md`
- `src/agentready/templates/python/template/.claude/skills/repo-explore/SKILL.md`
- `src/agentready/templates/python/template/.claude/skills/security-review/SKILL.md`
- `src/agentready/templates/python/template/.github/workflows/ci.yml`
- `src/agentready/templates/python/template/.gitignore`
- `src/agentready/templates/python/template/.python-version`
- `src/agentready/templates/python/template/AGENTS.md.jinja`
- `src/agentready/templates/python/template/CLAUDE.md`
- `src/agentready/templates/python/template/README.md.jinja`
- `src/agentready/templates/python/template/docs/ARCHITECTURE.md.jinja`
- `src/agentready/templates/python/template/docs/adr/0000-template.md`
- `src/agentready/templates/python/template/docs/agent/index.md`
- `src/agentready/templates/python/template/docs/agent/standards/architecture.md.jinja`
- `src/agentready/templates/python/template/docs/agent/standards/context-efficiency.md`
- `src/agentready/templates/python/template/docs/agent/standards/dependencies.md`
- `src/agentready/templates/python/template/docs/agent/standards/documentation.md`
- `src/agentready/templates/python/template/docs/agent/standards/module-placement.md.jinja`
- `src/agentready/templates/python/template/docs/agent/standards/python.md`
- `src/agentready/templates/python/template/docs/agent/standards/security.md`
- `src/agentready/templates/python/template/docs/agent/standards/testing.md`
- `src/agentready/templates/python/template/docs/agent/workflows/bugfix.md`
- `src/agentready/templates/python/template/docs/agent/workflows/documentation.md`
- `src/agentready/templates/python/template/docs/agent/workflows/feature.md`
- `src/agentready/templates/python/template/docs/agent/workflows/maintenance.md`
- `src/agentready/templates/python/template/docs/agent/workflows/module-placement.md`
- `src/agentready/templates/python/template/docs/agent/workflows/refactor.md`
- `src/agentready/templates/python/template/docs/agent/workflows/repo-explore.md`
- `src/agentready/templates/python/template/docs/agent/workflows/security.md`
- `src/agentready/templates/python/template/docs/changelog/index.md`
- `src/agentready/templates/python/template/docs/generated/CODEBASE_MAP.md.jinja`
- `src/agentready/templates/python/template/docs/work/index.md`
- `src/agentready/templates/python/template/docs/work/templates/bugfix.md`
- `src/agentready/templates/python/template/docs/work/templates/documentation.md`
- `src/agentready/templates/python/template/docs/work/templates/feature.md`
- `src/agentready/templates/python/template/docs/work/templates/maintenance.md`
- `src/agentready/templates/python/template/docs/work/templates/refactor.md`
- `src/agentready/templates/python/template/docs/work/templates/security.md`
- `src/agentready/templates/python/template/pyproject.toml.jinja`
- `src/agentready/templates/python/template/scripts/architecture_check.py.jinja`
- `src/agentready/templates/python/template/scripts/generate_codebase_map.py.jinja`
- `src/agentready/templates/python/template/scripts/project.py`
- `src/agentready/templates/python/template/scripts/work_registry.py`
- `src/agentready/templates/python/template/src/{{ package_name }}/__init__.py.jinja`
- `src/agentready/templates/python/template/src/{{ package_name }}/__main__.py.jinja`
- `src/agentready/templates/python/template/src/{{ package_name }}/bootstrap.py.jinja`
- `src/agentready/templates/python/template/src/{{ package_name }}/config.py.jinja`
- `src/agentready/templates/python/template/src/{{ package_name }}/entrypoints/__init__.py`
- `src/agentready/templates/python/template/src/{{ package_name }}/entrypoints/cli.py.jinja`
- `src/agentready/templates/python/template/src/{{ package_name }}/main.py.jinja`
- `src/agentready/templates/python/template/src/{{ package_name }}/modules/__init__.py.jinja`
- `src/agentready/templates/python/template/src/{{ package_name }}/modules/greeting/__init__.py.jinja`
- `src/agentready/templates/python/template/src/{{ package_name }}/modules/greeting/adapters/__init__.py.jinja`
- `src/agentready/templates/python/template/src/{{ package_name }}/modules/greeting/adapters/console.py.jinja`
- `src/agentready/templates/python/template/src/{{ package_name }}/modules/greeting/application/__init__.py.jinja`
- `src/agentready/templates/python/template/src/{{ package_name }}/modules/greeting/application/service.py.jinja`
- `src/agentready/templates/python/template/src/{{ package_name }}/modules/greeting/domain/__init__.py.jinja`
- `src/agentready/templates/python/template/src/{{ package_name }}/modules/greeting/domain/errors.py.jinja`
- `src/agentready/templates/python/template/tests/test_main.py.jinja`

### `tests`
- `tests/test_bootstrap.py`
- `tests/test_codebase_map.py`
- `tests/test_detach.py`
- `tests/test_detached_project.py`
- `tests/test_doctor.py`
- `tests/test_doctor_json.py`
- `tests/test_generated_architecture.py`
- `tests/test_generated_project.py`
- `tests/test_init.py`
- `tests/test_ownership.py`
- `tests/test_project.py`
- `tests/test_smoke.py`
- `tests/test_work_registry.py`

### `uv.lock`
- `uv.lock`
