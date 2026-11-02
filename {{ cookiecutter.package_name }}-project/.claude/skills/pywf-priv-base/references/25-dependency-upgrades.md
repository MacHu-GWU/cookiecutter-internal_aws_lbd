---
description: "The dependency upgrade process: finding outdated and unmaintained packages, judging each upgrade, packages that move together, applying the change, and the regression checks that prove it. Read when upgrading or replacing a dependency, or when asked whether a new version is worth it."
---

# Dependency Upgrades

How constraints are written is in `06-uv-dependencies.md`. This file is about changing them.

---

## 1. Find what is outdated

```bash
mise exec -- sh -c '. .mise/tasks/codeartifact-env.sh && uv tree --outdated --depth 1'
```

The wrapper fetches the CodeArtifact token, which uv needs to look up the private packages (`05-codeartifact.md` section 3). It lists each direct dependency with its locked version, plus `(latest: vX)` when a newer one exists; "latest" already respects `requires-python`.

**Unmaintained packages do not show up here.** Every few upgrades, also check each direct public dependency's last release date on PyPI (`https://pypi.org/pypi/<dist_name>/json`). A private package's versions are listed by `aws codeartifact list-package-versions --profile <aws_profile> --domain <codeartifact_domain> --domain-owner <aws_account_id> --repository <codeartifact_repo> --format pypi --package <private_dist_name>`; its changelog is the `release-history.rst` of its own repo. Replace a package with no release in about two years whose maintainers point to a successor.

---

## 2. Judge each upgrade

Read each outdated package's changelog from the locked version to the latest, and answer:

1. **Breaking changes that touch this repo,** checked against how the repo uses the package: its config, command-line flags, and imported APIs.
2. **Requirements:** the package's Python floor, and minimum versions of shared dependencies (a theme needs a given Sphinx; a pytest plugin, a given pytest).
3. **Gains:** security fixes, bug fixes that affect this repo, features worth adopting.
4. **Maintenance health:** last release, last commit, whether issues get answered.

**Verdict:** **upgrade** with the new constraint, **hold** with the reason, or **replace** with the successor.

**More than two packages:** delegate the changelog reading to a subagent, require a cited source for every version number and breaking change, and spot-check the versions against PyPI or CodeArtifact yourself.

**Packages that move together:** Sphinx with its theme and extensions (furo, sphinx-design, nbsphinx, sphinx-jinja, docfly); pytest with pytest-cov; a private package with the private packages it needs, which this repo lists too (`06-uv-dependencies.md` section 2).

---

## 3. Apply

1. Edit the constraints in `pyproject.toml`, following `06-uv-dependencies.md`.
2. `uv lock --upgrade-package <dist_name>` per package (or `uv lock --upgrade` for all), inside the CodeArtifact wrapper from section 1, then `mise run inst`.
3. `mise run export`, to refresh `requirements*.txt`.
4. For a renamed or replaced package, update every import and mention: `.mise/tasks/*.py`, `mise.toml` task descriptions, the docs, and the skill references.

---

## 4. Regression checks

| Area | Check |
| :--- | :--- |
| Tests | `mise run cov` passes with no new deprecation warnings. One test file run directly proves `run_cov_test` still works (`11-test-layout.md`). |
| Code | `mise run lint` |
| Docs build | `mise run build-doc` shows no new warnings, and the cross-reference check reports 0 unresolved (`14-sphinx.md`). |
| Docs look | With the visual check of `14-sphinx.md`, the sample pages in `docs/source/` (reStructuredText, notebook, sphinx-design gallery) render: tabs switch, dropdowns open, the jinja table is filled, raw cells render. For a theme upgrade, check light and dark mode (`16-furo.md`). |
| CI | After pushing, the `test` job passes (`20-github-actions.md`). |

The changelog entry for an upgrade follows the category table in `23-versioning-and-changelog.md`.
