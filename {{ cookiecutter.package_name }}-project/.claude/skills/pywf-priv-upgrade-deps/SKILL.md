---
name: pywf-priv-upgrade-deps
description: "Upgrade, hold, or replace the public and private dependencies of a pywf internal proprietary Python library: find outdated and unmaintained packages, make sure every private package (transitive ones included) is pinned to the CodeArtifact index, research changelogs and compatibility, update the constraints and lock file, and prove the result with tests, lint, and a docs build. Use when the user asks to upgrade or update dependencies, whether a new version of a package is worth it, or to replace an unmaintained package."
---

Bring the dependencies up to date, with every change justified and verified.

Read ../pywf-priv-base/SKILL.md, then:
- ../pywf-priv-base/references/04-python-versions.md
- ../pywf-priv-base/references/05-codeartifact.md
- ../pywf-priv-base/references/06-uv-dependencies.md
- ../pywf-priv-base/references/14-sphinx.md (section 2.2 and section 4: the cross-reference check and the visual check)
- ../pywf-priv-base/references/16-furo.md (only for a theme upgrade)
- ../pywf-priv-base/references/25-dependency-upgrades.md

## Steps

1. **Inventory.** Run the `uv tree --outdated --depth 1` wrapper from `25-dependency-upgrades.md` section 1, check each direct dependency's last release date, and show a table: package, public or private, extra, locked version, latest version, last release date.
   - Also run `uv tree` (inside the same wrapper) and list every private package in the tree. Each one missing from the requirements or from `[tool.uv.sources]` is a finding (`06-uv-dependencies.md` section 2), fixed in step 4 together with the upgrades.
2. **Research.** Judge each candidate as in `25-dependency-upgrades.md` section 2 (including when to delegate to a subagent). Present each verdict (upgrade / hold / replace) with the exact constraint string.
3. **Decide.** The user picks which verdicts to apply. On "just upgrade everything", apply every upgrade verdict, and still report the holds and replacements.
4. **Apply,** as in `25-dependency-upgrades.md` section 3.
5. **Prove it.** Run every regression check in `25-dependency-upgrades.md` section 4, and report each as pass or fail. A failure sends that package back to step 2: hold it, or fix the code.
6. **Commit** after the user's yes, so the changelog sees the upgrade in git history.

## Boundaries

- Upgrade the coupled packages listed in `25-dependency-upgrades.md` section 2 together. A private package's new release can bring new private packages: list those too.
- Run every uv command that reaches the private index inside the CodeArtifact wrapper; never print the token.
- Never raise `requires-python` as a side effect of an upgrade. It is the user's decision; ask it as a separate question.

Next step: `pywf-priv-changelog`, then `pywf-priv-release`.
