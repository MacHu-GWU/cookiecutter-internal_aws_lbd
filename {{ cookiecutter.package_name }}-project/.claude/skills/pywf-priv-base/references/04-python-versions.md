---
description: "The supported Python policy (floor 3.11, every CPython not at end of life), the four places a Python version number lives, and why CI tests only the dev Python. Read when checking or changing where a Python version number is written, or when those numbers disagree."
---

# Python Versions

---

## 1. Policy

- **The floor is 3.11.** Code uses 3.11+ syntax.
- **The supported range is every CPython version not at end of life** (schedule: <https://devguide.python.org/versions/>). A few months' lag either way is fine.

---

## 2. Where each number lives

| Where | What it means |
| :--- | :--- |
| `pyproject.toml` `requires-python` | The supported range, for example `">=3.11,<4.0"` |
| `pyproject.toml` classifiers | One `Programming Language :: Python :: 3.x` per supported version |
| `mise.toml` `[tools] python` | The one dev Python, for `.venv`; must lie inside the range |
| `.github/workflows/main.yml` | The `test` job's `python-version` matrix, and the `deploy-doc` job's `setup-python` version and `.venv` cache key. Both equal the dev Python. |

- **CI tests the dev Python only, on Linux.** An internal library runs on a few known runtimes, so the matrix stays at the dev Python unless a consumer needs another version; then add that version to the `test` matrix. The `deploy-doc` job always uses the dev Python.
- `mise.toml` `[env]` sets `UV_PYTHON = "python"`, so every `uv venv` and `uv sync` run through mise uses the first `python` on PATH: the mise one locally, the `setup-python` one in CI. Without it, uv prefers its own managed Pythons and a global `~/.config/uv/.python-version` pin, and `uv sync` silently rebuilds `.venv` with that version.
- `[tools] python` must be a plain version such as `"3.12"`, never `"latest"` or a list, so it can be compared with the CI numbers.

uv resolves dependencies against `requires-python`, whatever the dev Python is.

When the range changes, change `requires-python` and the classifiers together, in one commit. When the dev Python changes, change `mise.toml` and every number in `.github/workflows/main.yml` together.
