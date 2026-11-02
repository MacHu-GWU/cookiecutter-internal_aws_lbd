---
description: "The yearly Python routine: what to change when a new CPython is released, and when the oldest reaches end of life. Read when a new CPython is released or the oldest reaches end of life, or when asked to add or drop a supported Python version."
---

# Following the Python Release Cycle

A new CPython is released every October, and the oldest supported one reaches end of life around then. The policy is in `04-python-versions.md`.

---

## 1. A new version is released

1. Add it to the `test` job's `python-version` matrix next to the dev Python (`20-github-actions.md`), and run CI. If a dependency, private ones included, does not support it yet, take it out again and wait for that dependency.
2. Once it passes, add it to the classifiers (`04-python-versions.md`), raise the `requires-python` cap if one is set, and drop it from the matrix again: CI tests the dev Python only, unless a consumer runs on another version.
3. Record it in the changelog as a Minor Improvement (`23-versioning-and-changelog.md`).
4. Moving the dev Python to it is a separate decision, for the user: change `mise.toml` `[tools] python` and every number in the workflow together (`04-python-versions.md`).

---

## 2. A version reaches end of life

1. Remove it from the classifiers, and from the CI matrix if it is there.
2. Raise the `requires-python` floor. Check first that no consuming project still runs on it.
3. Lift the dependency caps that existed only for the old floor (`06-uv-dependencies.md` section 3), through the process in `25-dependency-upgrades.md`.
4. If the dev Python itself reached end of life, move it as in section 1 step 4.
5. Record it in the changelog as a Breaking Change (`23-versioning-and-changelog.md`): users on that Python get no new releases.
