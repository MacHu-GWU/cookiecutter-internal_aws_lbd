---
name: pywf-priv-audit
description: "Audit a pywf internal proprietary Python library against the template conventions (Python versions, private index and dependencies, mise tasks, CI, lint, code style, public API, test layout, docs and knowledge channels, changelog) and report each deviation with the skill that fixes it, changing no source file. Use when the user asks to check, audit, or review a repo, or to bring an older repo up to the current template."
---

Compare one repo with the template conventions, and produce a prioritized list of deviations. The audit changes no source file: if a check regenerates a tracked file, report the diff as a finding, then restore the file.

Read ../pywf-priv-base/SKILL.md, then every file in ../pywf-priv-base/references/.

## Checks

Record each finding with the file, the rule broken (reference file and section), and the fixing skill.

1. **Python versions and dependencies.**
   - The `uv tree --outdated --depth 1` wrapper in `25-dependency-upgrades.md` section 1 (fixed by `pywf-priv-upgrade-deps`).
   - The Python version locations agree with `04-python-versions.md` (fixed by `pywf-priv-fix-ci`).
   - Dependency constraints follow `06-uv-dependencies.md`.
   - **Private packages:** every private package in `uv tree`, transitive ones included, is a requirement and has a `[tool.uv.sources]` line (`06-uv-dependencies.md` section 2); the `[[tool.uv.index]]` block is `explicit` with `authenticate = "always"` (`05-codeartifact.md` section 2) (fixed by `pywf-priv-upgrade-deps`).
   - `[project.urls]` points nowhere public: no PyPI `Download` link, `Documentation` is the Cloudflare Pages URL or absent (direct edit).
2. **mise and CI.**
   - `mise.toml` follows `01-secrets.md` (every token template has the `env.X | default(...)` form and `|| true`) and `03-mise.md` (no task depends on `inst`; `UV_PYTHON` is set).
   - `.github/workflows/main.yml` follows `20-github-actions.md`: the OIDC step before `inst`, every `[tools]` entry in both `MISE_DISABLE_TOOLS` lists, the full-version `.venv` cache key, setup-uv's cache off, current action majors (fixed by `pywf-priv-fix-ci`).
   - No leftover open-source services: `codecov.yml`, `.readthedocs.yml`, a Codecov upload step, or a task or script pointing at Read the Docs or PyPI (direct edit).
3. **Lint.**
   - `mise.toml` has the `format` and `lint` tasks, and `pyproject.toml` has `[tool.ruff]` and `[tool.pytest]`.
   - `mise run lint` passes.
   - `uvx ruff format --check` on the `format` task's paths in `mise.toml` passes. Never run `mise run format` during an audit: it rewrites files.
4. **Code style** against `10-code-style.md`, sampled in about 10 source files and the recently changed areas:
   - the file header;
   - one name per import, and the five-group order;
   - no absolute self-imports inside `<package_name>/`;
   - 3.11+ type hints;
   - docstrings and `#:` comments;
   - one field per line in declarative models.
5. **Public API**, against `09-package-files.md`:
   - `api.py` exports no `_private` names;
   - every exported name has a docstring;
   - `tests/test_api.py` touches every exported name.
6. **Test layout.** Run `python ${CLAUDE_SKILL_DIR}/../pywf-priv-base/scripts/check_test_layout.py --project_root .`.
7. **Docs and knowledge channels.**
   - No maintainer pages in `docs/source/` (`19-knowledge-channels.md`); they belong in the `<maintain_prefix>` family (fixed by `pywf-priv-write-maintain-skill`).
   - If `.claude/skills/pypi-<package_name>/` exists, its version header matches the last tag (fixed by `pywf-priv-write-pypi-skill`).
   - Folder names follow `15-docfly.md`.
   - Headings use 78-character underlines.
   - `mise run build-doc` shows no warnings. It regenerates the tracked `docs/source/api/`, and may change `uv.lock`: report any `git status` diff in either, then restore them with `git checkout docs/source/api uv.lock`.
   - `python ${CLAUDE_SKILL_DIR}/../pywf-priv-base/scripts/check_doc_xrefs.py` reports 0 unresolved.
   - Notebooks have committed outputs.
8. **Changelog.** The Backlog block is present, and the latest version section matches the `pyproject.toml` version or the last tag.

## Report

Group the findings by fixing skill:

- `pywf-priv-add-module`
- `pywf-priv-write-test`
- `pywf-priv-write-doc`
- `pywf-priv-write-maintain-skill`
- `pywf-priv-write-pypi-skill`
- `pywf-priv-changelog`
- `pywf-priv-fix-ci` (Python versions and CI config)
- `pywf-priv-upgrade-deps` (outdated or unmaintained dependencies, unpinned private packages)
- "direct edit" (config and style)

Within each group, order the findings by severity:

1. breaks CI or the release;
2. breaks a convention that tools rely on;
3. style.

End with counts per group, and ask which group to fix first.
