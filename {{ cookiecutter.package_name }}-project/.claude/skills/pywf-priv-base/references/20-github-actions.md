---
description: "The GitHub Actions workflow: the test and deploy-doc jobs, which tool comes from an action and which from mise, MISE_DISABLE_TOOLS, AWS access through OIDC, the .venv cache key, triggers and the doc branch, keeping actions current, and diagnosing a red run from its log. Read when changing .github/workflows/main.yml, or when a CI run fails or shows warnings."
---

# GitHub Actions

---

## 1. The workflow: `.github/workflows/main.yml`

Two jobs. Both run their commands as `mise run <task>`, like a maintainer does locally (`03-mise.md`).

| Job | Runs on | What it does |
| :--- | :--- | :--- |
| `test` | every push and pull request to `main` or `doc` | Install, then `mise run cov`. Coverage is printed in the log only: no third-party coverage service, so the code and its reports stay inside the organization. |
| `deploy-doc` | a push to `doc`, after `test` passes | Install, `mise run build-doc`, then `mise run deploy-pages` to Cloudflare Pages |

**Who provides each tool.** Tools with an official action come from that action, which caches better; mise provides only the rest:

| Tool | Source |
| :--- | :--- |
| Python, uv, Node.js | `actions/setup-python`, `astral-sh/setup-uv`, `actions/setup-node` |
| mise itself | `jdx/mise-action`. In `test` it installs no tool; in `deploy-doc`, `install_args: "pandoc"` installs only pandoc, at the `mise.toml` version. |
| wrangler | `npm install -g wrangler`, in `deploy-doc` only. mise's `npm:` backend would use mise's own Node.js, which CI does not install. |
| The AWS CLI | preinstalled on the GitHub runner |

**`MISE_DISABLE_TOOLS`,** set at job level, lists every `[tools]` entry the job must not install, using mise's exact names (`npm:wrangler`, not `wrangler`). Without it, the first `mise run` installs the missing tools on its own. **A tool added to `mise.toml` `[tools]` must be added to both jobs' lists,** unless that job needs mise to install it.

**Steps, in order, in both jobs:**

1. checkout;
2. setup-python, setup-uv, setup-node, then mise-action;
3. `aws-actions/configure-aws-credentials` with OIDC: it assumes the CodeArtifact IAM role in the DevOps account, `arn:aws:iam::${% raw %}{{{% endraw %} secrets.DEVOPS_AWS_ACCOUNT_ID {% raw %}}}{% endraw %}:role/<role_name>`. This needs `permissions: id-token: write`, and must come before installing, because `inst` fetches the CodeArtifact token (`05-codeartifact.md` section 3);
4. restore the cached `.venv`, keyed on the OS, the Python version, and the hash of `uv.lock`;
5. `mise run inst`, **skipped on a cache hit**;
6. the job's own tasks.

**Secrets.** The workflow's top-level `env:` maps `GITHUB_TOKEN`, `DEVOPS_AWS_ACCOUNT_ID`, and `CLOUDFLARE_API_TOKEN` from repository secrets (`01-secrets.md` section 5). `setup-github-secrets` and `setup-cloudflare-token` store the last two.

**The `doc` branch.** Hosted docs are published by pushing `main` to `doc`: `git push origin main:doc`. A separate branch makes each docs deploy a deliberate, visible step in git history, instead of a side effect of every push to `main`. A library without hosted docs never pushes `doc`, so `deploy-doc` never runs, and the Cloudflare secret is not needed.

---

## 2. Keeping actions current

- Keep every action on its latest major version. Old majors first get warnings (a deprecated Node.js runtime, a removed input), then break.
- Use the floating major tag (`@v7`) when the action publishes one. setup-uv does not, so pin its full version (`@v10.3.0`).
- **Cache key:** use the **full** Python version that setup-python reports (give that step `id: setup-python`, then `${% raw %}{{{% endraw %} steps.setup-python.outputs.python-version {% raw %}}}{% endraw %}`, such as 3.12.13), not the short version. A `.venv` points at its interpreter's path, so a venv cached under an older patch release breaks when the runner image moves on.
- **Turn off setup-uv's own cache** (`enable-cache: false`) when the whole `.venv` is cached: with both on, reruns warn "Unable to reserve cache".
- After any workflow change, read the run's **Annotations** panel: warnings appear there even on a green run.

---

## 3. Diagnosing a red run

Start from the log, never from a guess.

```bash
gh run list --limit 5                 # recent runs and their status
gh run view <run_id> --log-failed     # only the log lines of the failed steps
gh run rerun <run_id> --failed        # retry only the failed jobs (for flaky infrastructure)
gh workflow run main.yml              # start a run by hand (workflow_dispatch)
```

| Symptom | Usual cause | Fix |
| :--- | :--- | :--- |
| `Could not assume role with OIDC`, or `Not authorized to perform sts:AssumeRoleWithWebIdentity` | The `DEVOPS_AWS_ACCOUNT_ID` secret is missing, or the role's trust policy does not allow this repo | `gh secret list` (names only); if missing, `mise run setup-github-secrets` after the user's yes. A trust policy is organization infrastructure: report it to the user. |
| `inst` fails with 401 or 403 on the private index | The role lacks CodeArtifact permissions, or step 3 ran after the install | Check the step order, then report the role to the user |
| `inst` fails with "not found" for a private package | A private package, often a transitive one, is not pinned in `[tool.uv.sources]` | List it as in `06-uv-dependencies.md` section 2 |
| A `mise run` step starts installing Python, Node.js, or another tool | A `[tools]` entry is missing from `MISE_DISABLE_TOOLS` | Add its exact mise name to the job's list |
| `deploy-pages` fails with an authentication error | The `CLOUDFLARE_API_TOKEN` secret is missing or expired | `mise run setup-cloudflare-token` after the user's yes |
| `wrangler: command not found` | The `npm install -g wrangler` step is missing or ran before setup-node | Restore the step order |
| `uv sync` fails | `uv.lock` is out of date with `pyproject.toml` | Run `mise run inst` locally, then commit `uv.lock` |
| Passes locally, fails in CI | It depends on local state: a file in `tmp/`, an environment variable, an AWS profile, the working directory | Build the state inside the test (`tmp_path`, `path_enum`) |
| `Ignoring existing virtual environment linked to non-existent Python interpreter` | A `.venv` cached under an older Python patch release | The full-version cache key (section 2). Meanwhile, `gh cache delete --all`, then rerun. |
| Any other stale `.venv` | The cache key does not cover what changed | `gh cache delete --all`, then rerun |
