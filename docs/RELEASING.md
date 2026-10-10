# Releasing AgentReady

Version is declared once in `pyproject.toml`; the CLI reads installed package metadata.
Use conventional `MAJOR.MINOR.PATCH` versions and matching annotated `vMAJOR.MINOR.PATCH` tags.
During 0.x, minor versions may change contracts; patches preserve them. Document changes in
`CHANGELOG.md`. Only the latest released version receives fixes. Python 3.12+ is the declared
requirement; CI exercises the minimum on Ubuntu/Windows and Python 3.14 on Ubuntu. Newer versions
are not individually proven by that matrix.

## Local checklist

- Review intended Git changes; version and release notes agree; no credentials or evaluation caches.
- `uv sync --locked --all-groups`; Ruff check/format, mypy, complete pytest and map check pass.
- `uv build`; inspect exact wheel/sdist, install each into fresh environments and exercise CLI.
- Qualify every generated profile, doctor, workflow, skills, build and detach/verify.
- Check README links, MIT license and public support/security guidance.
- Commit reviewed changes; require clean Git status. Keep generated project source independent.

## Human remote procedure

No publication is automatic. From the reviewed main checkout, in PowerShell:

```powershell
git diff --check
git status --short
git add -- AGENTS.md README.md pyproject.toml uv.lock .github/workflows/ci.yml CONTRIBUTING.md SECURITY.md CODE_OF_CONDUCT.md CHANGELOG.md docs src tests
git commit -m "Prepare AgentReady 0.1.0 public release"
git status --porcelain
```

Stop if status is nonempty. Only with a clean tree, continue:

```powershell
git tag -a v0.1.0 -m "AgentReady 0.1.0"
git push origin main
```

On GitHub, identify the CI run for the exact committed SHA:

```powershell
gh run list --repo massaro8/programming_agents --workflow ci.yml --branch main --limit 5
gh run watch RUN_ID --repo massaro8/programming_agents --exit-status
```

Replace `RUN_ID` with that run. Require all matrix jobs green before publishing the tag/release:

```powershell
git push origin v0.1.0
gh release create v0.1.0 --repo massaro8/programming_agents --verify-tag --title "AgentReady 0.1.0" --notes-file docs/releases/0.1.0.md dist/agentready-0.1.0-py3-none-any.whl dist/agentready-0.1.0.tar.gz
```

Enable GitHub private vulnerability reporting in repository Settings → Security before inviting
external users. Check the security advisory link works. Do not tag a different commit after CI.

Optional PyPI publication is separate: first confirm ownership/availability of `agentready`, configure
credentials or trusted publishing, validate the exact artifacts, then explicitly authorize upload:

```powershell
uvx --from twine twine check dist/agentready-0.1.0-py3-none-any.whl dist/agentready-0.1.0.tar.gz
uvx --from twine twine upload dist/agentready-0.1.0-py3-none-any.whl dist/agentready-0.1.0.tar.gz
```

Do not use `dist/*`: this directory may contain historical artifacts. Publication commands above
are instructions for a human, not steps performed by the readiness audit.
