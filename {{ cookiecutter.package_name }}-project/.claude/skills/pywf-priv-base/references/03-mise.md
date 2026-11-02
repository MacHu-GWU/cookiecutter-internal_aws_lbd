---
description: "mise as the single entry point of a repo: the mise.toml blocks, every task and what it runs, why inst is never a task dependency, and which tasks change external services and need the user's yes. Read when unsure which mise task runs what, before running a task that changes an external service, or when adding or changing a task."
---

# mise

mise runs everything in a repo, locally and in CI. Prefer a task over the raw command it wraps: tasks load the `[env]` values and fetch the CodeArtifact token where needed.

---

## 1. `mise.toml`

| Block | What it holds |
| :--- | :--- |
| `[env]` | Tokens, loaded as in `01-secrets.md`; the organization values (AWS profile, CodeArtifact domain, owner, region, repository); and `UV_PYTHON`, which makes uv use the `[tools]` Python |
| `[tools]` | The dev Python, `uv`, `claude`, `pandoc`, `awscli`, `node`, and `npm:wrangler`, installed once per machine and shared across repos |
| `[tasks.*]` | Every workflow command, listed by `mise tasks ls` with its `description`. Longer tasks are scripts in `.mise/tasks/`. |

Run a task with `mise run <task>`.

---

## 2. `inst` is never a dependency

`inst` needs the network and valid AWS credentials, because it sources `.mise/tasks/codeartifact-env.sh` to fetch a CodeArtifact token before `uv sync --all-extras`. So no other task depends on it:

- Run `mise run inst` explicitly after cloning, after any change to the dependencies in `pyproject.toml`, and after a version bump (so `uv.lock` records it).
- Every other task (`test`, `cov`, `build-doc`, ...) assumes `.venv` is already in sync. If one fails with an import error, run `inst`, then rerun it.
- Never add `depends = ["inst"]` to a task.

---

## 3. Tasks

| Task | What it does |
| :--- | :--- |
| `venv-create` / `venv-remove` | Create / delete `.venv` |
| `inst` | Fetch the CodeArtifact token, then `uv sync --all-extras` |
| `format` / `lint` | Format all Python code with ruff / check it with ruff and the one-import-per-statement check |
| `test` / `cov` | Run the test suite / run it with coverage, writing `htmlcov/` |
| `view-cov` | Open the coverage report |
| `build-doc` / `view-doc` | Build the Sphinx HTML into `docs/build/html` / open it |
| `notebook-to-markdown` | Convert the docs notebooks to Markdown, for AI reading |
| `export` | Regenerate `requirements*.txt` from `uv.lock` |
| `build` / `publish` | Build the wheel and sdist / upload them to the private CodeArtifact repository |
| `remove-pkg-version` | Delete the current `pyproject.toml` version from CodeArtifact (asks for `Y` on the terminal) |
| `release` | Create the GitHub tag and release for the current version |
| `update-github-metadata` | Set the GitHub repo description and homepage |
| `setup-github-secrets` | Store `DEVOPS_AWS_ACCOUNT_ID` as a GitHub Actions secret, for the OIDC role in CI |
| `setup-cloudflare-token` / `create-pages-project` / `deploy-pages` | Hosted docs only: store `CLOUDFLARE_API_TOKEN` as an Actions secret / create the Cloudflare Pages project / upload `docs/build/html` to it |
| `deploy-versioned-doc` / `deploy-latest-doc` / `view-latest-doc` | Hosted docs only: upload `docs/build/html` to the S3 doc-host bucket as this version's frozen copy / as `latest` / open `latest`. Cloudflare Pages keeps only the latest docs; S3 keeps every version. |

---

## 4. Tasks that change external services

`publish`, `remove-pkg-version`, `release`, `update-github-metadata`, `setup-github-secrets`, `setup-cloudflare-token`, `create-pages-project`, `deploy-pages`, and the S3 `deploy-*-doc` tasks act on CodeArtifact, GitHub, Cloudflare, or S3. Run each only after the user's yes; one yes covers one task. Never run one as a side effect of another job.

`remove-pkg-version` is irreversible and reads a `Y` from the terminal: tell the user to run it themselves, and only when they asked to delete that version.
