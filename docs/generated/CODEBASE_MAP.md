# Codebase Map

Structure fingerprint: `d46c1caf097c`

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
- `.agents/skills/bug-investigation/evals/cases.json`
- `.agents/skills/feature-builder/SKILL.md`
- `.agents/skills/feature-builder/evals/cases.json`
- `.agents/skills/project-bootstrap/SKILL.md`
- `.agents/skills/project-bootstrap/evals/cases.json`
- `.agents/skills/repo-explore/SKILL.md`
- `.agents/skills/repo-explore/evals/cases.json`

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

### `CHANGELOG.md`
- `CHANGELOG.md`

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
- `docs/RELEASING.md`
- `docs/ROADMAP.md`
- `docs/SKILL_QA_AND_CONTINUITY.md`
- `docs/USER_GUIDE.md`
- `docs/VERIFICATION_EVIDENCE.md`
- `docs/adr/0000-template.md`
- `docs/adr/0001-static-project-families.md`
- `docs/adr/0002-bundled-infrastructure-composition.md`
- `docs/adr/0003-catalog-driven-cloudformation.md`
- `docs/audits/ADVERSARIAL_STRESS_AUDIT.md`
- `docs/audits/BOOT_001_AUDIT.md`
- `docs/audits/BOOT_002_AUDIT.md`
- `docs/audits/CFN_STANDARDIZATION_001.md`
- `docs/audits/CLOUDFORMATION_FEASIBILITY.md`
- `docs/audits/DET_001_AUDIT.md`
- `docs/audits/DET_002_AUDIT.md`
- `docs/audits/DOC_001_AUDIT.md`
- `docs/audits/DOC_002_AUDIT.md`
- `docs/audits/FEATURE_EVOLUTION_AUDIT.md`
- `docs/audits/FINAL_FIX_001.md`
- `docs/audits/FINAL_PRODUCTIZATION_AUDIT.md`
- `docs/audits/FLOW_001_AUDIT.md`
- `docs/audits/FLOW_002_AUDIT.md`
- `docs/audits/FLOW_003_AUDIT.md`
- `docs/audits/HARDEN_001_AUDIT.md`
- `docs/audits/HARDEN_002_AUDIT.md`
- `docs/audits/INIT_001_AUDIT.md`
- `docs/audits/INIT_002_AUDIT.md`
- `docs/audits/MULTI_PROJECT_FINAL_AUDIT.md`
- `docs/audits/PHASE0_BASELINE_AUDIT.md`
- `docs/audits/PRODUCTIZE_001_AUDIT.md`
- `docs/audits/PYT_001_AUDIT.md`
- `docs/audits/READY_FOR_PROJECTS_FINAL.md`
- `docs/audits/RELEASE_READINESS_AUDIT.md`
- `docs/audits/REL_001_AUDIT.md`
- `docs/audits/STRESS_FIX_001_AUDIT.md`
- `docs/changelog/index.md`
- `docs/generated/CODEBASE_MAP.md`
- `docs/releases/0.1.0.md`
- `docs/verification.json`
- `docs/verification/W007.json`
- `docs/work/W001-skill-contract-and-doctor-validation.md`
- `docs/work/W002-portable-skill-evaluation.md`
- `docs/work/W003-opt-in-repository-hooks.md`
- `docs/work/W004-work-checkpoint-and-resume.md`
- `docs/work/W005-extension-architecture-decision.md`
- `docs/work/W006-feature-evolution-regression-audit.md`
- `docs/work/W007-cloudformation-catalog-standardization.md`
- `docs/work/index.md`
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
- `src/agentready/aws_inspection.py`
- `src/agentready/bootstrap.py`
- `src/agentready/cli.py`
- `src/agentready/continuity.py`
- `src/agentready/core/__init__.py`
- `src/agentready/core/families.py`
- `src/agentready/core/inventory.py`
- `src/agentready/core/ownership.py`
- `src/agentready/core/profiles.py`
- `src/agentready/core/project.py`
- `src/agentready/detach/__init__.py`
- `src/agentready/detach/service.py`
- `src/agentready/doctor/__init__.py`
- `src/agentready/doctor/codebase_map.py`
- `src/agentready/doctor/evolution.py`
- `src/agentready/doctor/infrastructure.py`
- `src/agentready/doctor/inspector.py`
- `src/agentready/doctor/serialization.py`
- `src/agentready/doctor/work.py`
- `src/agentready/environment_contracts.py`
- `src/agentready/hooks.py`
- `src/agentready/infrastructure_tools.py`
- `src/agentready/local_paths.py`
- `src/agentready/render/__init__.py`
- `src/agentready/render/existing.py`
- `src/agentready/render/generator.py`
- `src/agentready/skill_qa.py`
- `src/agentready/templates/__init__.py`
- `src/agentready/templates/cloudformation/__init__.py`
- `src/agentready/templates/cloudformation/copier.yml`
- `src/agentready/templates/cloudformation/template/.agentready/manifest.toml.jinja`
- `src/agentready/templates/cloudformation/template/.agents/skills/aws-infrastructure-inspection/SKILL.md`
- `src/agentready/templates/cloudformation/template/.agents/skills/aws-infrastructure-inspection/evals/cases.json`
- `src/agentready/templates/cloudformation/template/.agents/skills/bug-investigation/SKILL.md`
- `src/agentready/templates/cloudformation/template/.agents/skills/bug-investigation/evals/cases.json`
- `src/agentready/templates/cloudformation/template/.agents/skills/cloudformation-change/SKILL.md`
- `src/agentready/templates/cloudformation/template/.agents/skills/cloudformation-change/evals/cases.json`
- `src/agentready/templates/cloudformation/template/.agents/skills/documentation/SKILL.md`
- `src/agentready/templates/cloudformation/template/.agents/skills/documentation/evals/cases.json`
- `src/agentready/templates/cloudformation/template/.agents/skills/maintenance/SKILL.md`
- `src/agentready/templates/cloudformation/template/.agents/skills/maintenance/evals/cases.json`
- `src/agentready/templates/cloudformation/template/.agents/skills/module-placement/SKILL.md`
- `src/agentready/templates/cloudformation/template/.agents/skills/module-placement/evals/cases.json`
- `src/agentready/templates/cloudformation/template/.agents/skills/refactoring/SKILL.md`
- `src/agentready/templates/cloudformation/template/.agents/skills/refactoring/evals/cases.json`
- `src/agentready/templates/cloudformation/template/.agents/skills/repo-explore/SKILL.md`
- `src/agentready/templates/cloudformation/template/.agents/skills/repo-explore/evals/cases.json`
- `src/agentready/templates/cloudformation/template/.agents/skills/security-review/SKILL.md`
- `src/agentready/templates/cloudformation/template/.agents/skills/security-review/evals/cases.json`
- `src/agentready/templates/cloudformation/template/.cfnlintrc`
- `src/agentready/templates/cloudformation/template/.claude/skills/aws-infrastructure-inspection/SKILL.md`
- `src/agentready/templates/cloudformation/template/.claude/skills/bug-investigation/SKILL.md.jinja`
- `src/agentready/templates/cloudformation/template/.claude/skills/cloudformation-change/SKILL.md.jinja`
- `src/agentready/templates/cloudformation/template/.claude/skills/documentation/SKILL.md.jinja`
- `src/agentready/templates/cloudformation/template/.claude/skills/maintenance/SKILL.md.jinja`
- `src/agentready/templates/cloudformation/template/.claude/skills/module-placement/SKILL.md.jinja`
- `src/agentready/templates/cloudformation/template/.claude/skills/refactoring/SKILL.md.jinja`
- `src/agentready/templates/cloudformation/template/.claude/skills/repo-explore/SKILL.md.jinja`
- `src/agentready/templates/cloudformation/template/.claude/skills/security-review/SKILL.md.jinja`
- `src/agentready/templates/cloudformation/template/.gitattributes`
- `src/agentready/templates/cloudformation/template/.githooks/pre-push`
- `src/agentready/templates/cloudformation/template/.github/workflows/ci.yml`
- `src/agentready/templates/cloudformation/template/.gitignore`
- `src/agentready/templates/cloudformation/template/AGENTS.md`
- `src/agentready/templates/cloudformation/template/CLAUDE.md`
- `src/agentready/templates/cloudformation/template/README.md.jinja`
- `src/agentready/templates/cloudformation/template/bitbucket-pipelines.yml`
- `src/agentready/templates/cloudformation/template/deployment/bitbucket-pipelines.yml.example`
- `src/agentready/templates/cloudformation/template/deployment/environments.conf`
- `src/agentready/templates/cloudformation/template/docs/ARCHITECTURE.md`
- `src/agentready/templates/cloudformation/template/docs/adr/0000-template.md`
- `src/agentready/templates/cloudformation/template/docs/adr/0001-catalog-driven-cloudformation.md`
- `src/agentready/templates/cloudformation/template/docs/agent/index.md`
- `src/agentready/templates/cloudformation/template/docs/agent/standards/architecture.md.jinja`
- `src/agentready/templates/cloudformation/template/docs/agent/standards/context-efficiency.md`
- `src/agentready/templates/cloudformation/template/docs/agent/standards/dependencies.md`
- `src/agentready/templates/cloudformation/template/docs/agent/standards/documentation.md`
- `src/agentready/templates/cloudformation/template/docs/agent/standards/module-placement.md.jinja`
- `src/agentready/templates/cloudformation/template/docs/agent/standards/security.md`
- `src/agentready/templates/cloudformation/template/docs/agent/standards/testing.md`
- `src/agentready/templates/cloudformation/template/docs/agent/workflows/bugfix.md`
- `src/agentready/templates/cloudformation/template/docs/agent/workflows/documentation.md`
- `src/agentready/templates/cloudformation/template/docs/agent/workflows/feature.md`
- `src/agentready/templates/cloudformation/template/docs/agent/workflows/maintenance.md`
- `src/agentready/templates/cloudformation/template/docs/agent/workflows/module-placement.md`
- `src/agentready/templates/cloudformation/template/docs/agent/workflows/refactor.md`
- `src/agentready/templates/cloudformation/template/docs/agent/workflows/repo-explore.md`
- `src/agentready/templates/cloudformation/template/docs/agent/workflows/security.md`
- `src/agentready/templates/cloudformation/template/docs/changelog/index.md`
- `src/agentready/templates/cloudformation/template/docs/generated/CODEBASE_MAP.md.jinja`
- `src/agentready/templates/cloudformation/template/docs/infrastructure/ENGINEERING.md`
- `src/agentready/templates/cloudformation/template/docs/infrastructure/environments.json`
- `src/agentready/templates/cloudformation/template/docs/infrastructure/parameters.json`
- `src/agentready/templates/cloudformation/template/docs/verification.json`
- `src/agentready/templates/cloudformation/template/docs/work/index.md`
- `src/agentready/templates/cloudformation/template/docs/work/templates/bugfix.md`
- `src/agentready/templates/cloudformation/template/docs/work/templates/documentation.md`
- `src/agentready/templates/cloudformation/template/docs/work/templates/feature.md`
- `src/agentready/templates/cloudformation/template/docs/work/templates/maintenance.md`
- `src/agentready/templates/cloudformation/template/docs/work/templates/refactor.md`
- `src/agentready/templates/cloudformation/template/docs/work/templates/security.md`
- `src/agentready/templates/cloudformation/template/parameters/sandbox.json`
- `src/agentready/templates/cloudformation/template/policies/security.guard`
- `src/agentready/templates/cloudformation/template/scripts/aws_inspection.py.jinja`
- `src/agentready/templates/cloudformation/template/scripts/bootstrap.sh`
- `src/agentready/templates/cloudformation/template/scripts/cfn_lib.sh`
- `src/agentready/templates/cloudformation/template/scripts/context.py.jinja`
- `src/agentready/templates/cloudformation/template/scripts/continuity.py.jinja`
- `src/agentready/templates/cloudformation/template/scripts/deploy.sh`
- `src/agentready/templates/cloudformation/template/scripts/environment_contracts.py.jinja`
- `src/agentready/templates/cloudformation/template/scripts/fixture_check.py`
- `src/agentready/templates/cloudformation/template/scripts/generate_codebase_map.py`
- `src/agentready/templates/cloudformation/template/scripts/hooks.py.jinja`
- `src/agentready/templates/cloudformation/template/scripts/infrastructure_checks.py`
- `src/agentready/templates/cloudformation/template/scripts/infrastructure_tools.py.jinja`
- `src/agentready/templates/cloudformation/template/scripts/local_paths.py.jinja`
- `src/agentready/templates/cloudformation/template/scripts/project.py`
- `src/agentready/templates/cloudformation/template/scripts/skill_check.py.jinja`
- `src/agentready/templates/cloudformation/template/scripts/skill_qa.py.jinja`
- `src/agentready/templates/cloudformation/template/scripts/skill_routes.py.jinja`
- `src/agentready/templates/cloudformation/template/scripts/status.py.jinja`
- `src/agentready/templates/cloudformation/template/scripts/validate.sh`
- `src/agentready/templates/cloudformation/template/scripts/verification.py.jinja`
- `src/agentready/templates/cloudformation/template/scripts/work_registry.py.jinja`
- `src/agentready/templates/cloudformation/template/stacks/catalog.conf`
- `src/agentready/templates/cloudformation/template/stacks/storage/artifacts.yaml`
- `src/agentready/templates/cloudformation/template/tests/engine/aws-fake.sh`
- `src/agentready/templates/cloudformation/template/tests/engine/run.sh`
- `src/agentready/templates/cloudformation/template/tests/fixtures/broken-reference.yaml`
- `src/agentready/templates/cloudformation/template/tests/fixtures/invalid-property.yaml`
- `src/agentready/templates/cloudformation/template/tests/fixtures/missing-encryption.yaml`
- `src/agentready/templates/cloudformation/template/tests/fixtures/missing-public-access-block.yaml`
- `src/agentready/templates/cloudformation/template/tests/fixtures/missing-tls-policy.yaml`
- `src/agentready/templates/cloudformation/template/tests/fixtures/public-s3.yaml`
- `src/agentready/templates/cloudformation/template/tests/fixtures/skill_routing.json`
- `src/agentready/templates/cloudformation/template/tests/fixtures/unrestricted-ingress.yaml`
- `src/agentready/templates/cloudformation/template/tests/fixtures/valid-network.yaml`
- `src/agentready/templates/cloudformation/template/tests/fixtures/valid-renamed.yaml`
- `src/agentready/templates/cloudformation/template/tests/fixtures/valid.yaml`
- `src/agentready/templates/python/__init__.py`
- `src/agentready/templates/python/copier.yml`
- `src/agentready/templates/python/template/.agentready/manifest.toml.jinja`
- `src/agentready/templates/python/template/.agents/skills/bug-investigation/SKILL.md`
- `src/agentready/templates/python/template/.agents/skills/bug-investigation/evals/cases.json`
- `src/agentready/templates/python/template/.agents/skills/documentation/SKILL.md`
- `src/agentready/templates/python/template/.agents/skills/documentation/evals/cases.json`
- `src/agentready/templates/python/template/.agents/skills/feature-builder/SKILL.md`
- `src/agentready/templates/python/template/.agents/skills/feature-builder/evals/cases.json`
- `src/agentready/templates/python/template/.agents/skills/maintenance/SKILL.md`
- `src/agentready/templates/python/template/.agents/skills/maintenance/evals/cases.json`
- `src/agentready/templates/python/template/.agents/skills/module-placement/SKILL.md`
- `src/agentready/templates/python/template/.agents/skills/module-placement/evals/cases.json`
- `src/agentready/templates/python/template/.agents/skills/refactoring/SKILL.md`
- `src/agentready/templates/python/template/.agents/skills/refactoring/evals/cases.json`
- `src/agentready/templates/python/template/.agents/skills/repo-explore/SKILL.md`
- `src/agentready/templates/python/template/.agents/skills/repo-explore/evals/cases.json`
- `src/agentready/templates/python/template/.agents/skills/security-review/SKILL.md`
- `src/agentready/templates/python/template/.agents/skills/security-review/evals/cases.json`
- `src/agentready/templates/python/template/.claude/skills/bug-investigation/SKILL.md.jinja`
- `src/agentready/templates/python/template/.claude/skills/documentation/SKILL.md.jinja`
- `src/agentready/templates/python/template/.claude/skills/feature-builder/SKILL.md.jinja`
- `src/agentready/templates/python/template/.claude/skills/maintenance/SKILL.md.jinja`
- `src/agentready/templates/python/template/.claude/skills/module-placement/SKILL.md.jinja`
- `src/agentready/templates/python/template/.claude/skills/refactoring/SKILL.md.jinja`
- `src/agentready/templates/python/template/.claude/skills/repo-explore/SKILL.md.jinja`
- `src/agentready/templates/python/template/.claude/skills/security-review/SKILL.md.jinja`
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
- `src/agentready/templates/python/template/docs/modules/greeting.md.jinja`
- `src/agentready/templates/python/template/docs/verification.json`
- `src/agentready/templates/python/template/docs/work/index.md`
- `src/agentready/templates/python/template/docs/work/templates/bugfix.md`
- `src/agentready/templates/python/template/docs/work/templates/documentation.md`
- `src/agentready/templates/python/template/docs/work/templates/feature.md`
- `src/agentready/templates/python/template/docs/work/templates/maintenance.md`
- `src/agentready/templates/python/template/docs/work/templates/refactor.md`
- `src/agentready/templates/python/template/docs/work/templates/security.md`
- `src/agentready/templates/python/template/pyproject.toml.jinja`
- `src/agentready/templates/python/template/scripts/architecture_check.py.jinja`
- `src/agentready/templates/python/template/scripts/command_check.py`
- `src/agentready/templates/python/template/scripts/context.py`
- `src/agentready/templates/python/template/scripts/continuity.py.jinja`
- `src/agentready/templates/python/template/scripts/generate_codebase_map.py.jinja`
- `src/agentready/templates/python/template/scripts/hooks.py.jinja`
- `src/agentready/templates/python/template/scripts/local_paths.py.jinja`
- `src/agentready/templates/python/template/scripts/module_knowledge.py.jinja`
- `src/agentready/templates/python/template/scripts/package_check.py.jinja`
- `src/agentready/templates/python/template/scripts/project.py`
- `src/agentready/templates/python/template/scripts/repository_inventory.py.jinja`
- `src/agentready/templates/python/template/scripts/skill_check.py`
- `src/agentready/templates/python/template/scripts/skill_qa.py.jinja`
- `src/agentready/templates/python/template/scripts/skill_routes.py`
- `src/agentready/templates/python/template/scripts/status.py`
- `src/agentready/templates/python/template/scripts/verification.py.jinja`
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
- `src/agentready/templates/python/template/tests/fixtures/skill_routing.json`
- `src/agentready/templates/python/template/tests/test_main.py.jinja`
- `src/agentready/verification.py`

### `tests`
- `tests/test_adversarial_boundaries.py`
- `tests/test_aws_inspection.py`
- `tests/test_bootstrap.py`
- `tests/test_cfn_standard.py`
- `tests/test_cloudformation.py`
- `tests/test_codebase_map.py`
- `tests/test_composition.py`
- `tests/test_continuity_untracked.py`
- `tests/test_detach.py`
- `tests/test_detached_project.py`
- `tests/test_doctor.py`
- `tests/test_doctor_json.py`
- `tests/test_environment_contracts.py`
- `tests/test_evolution.py`
- `tests/test_existing_init.py`
- `tests/test_family_lifecycle.py`
- `tests/test_final_ux.py`
- `tests/test_generated_architecture.py`
- `tests/test_generated_context.py`
- `tests/test_generated_project.py`
- `tests/test_infrastructure_tools.py`
- `tests/test_init.py`
- `tests/test_ownership.py`
- `tests/test_package_check.py`
- `tests/test_project.py`
- `tests/test_skill_contract.py`
- `tests/test_smoke.py`
- `tests/test_stress_diagnostics.py`
- `tests/test_stress_guidance.py`
- `tests/test_stress_inventory.py`
- `tests/test_stress_maintenance.py`
- `tests/test_task_routing.py`
- `tests/test_verification.py`
- `tests/test_work_registry.py`

### `uv.lock`
- `uv.lock`
