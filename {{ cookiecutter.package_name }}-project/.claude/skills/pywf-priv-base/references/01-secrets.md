---
description: "How secrets and credentials reach a repo: $HOME/home_secret.toml read by the hst CLI through mise [env], AWS credentials from a named AWS CLI profile, the non-secret organization values in [env], the hard rules that keep an AI from reading or printing a secret, and how CI differs. Read before running anything that needs a token or AWS credentials, or when adding a secret."
---

# Secrets

The maintainer runs hundreds of repos on one machine, so instead of a `.env` file per repo, every token lives in one file, `$HOME/home_secret.toml`, read by the [home-secret-toml](https://github.com/MacHu-GWU/home_secret_toml-project) CLI (`hst`). AWS credentials are the one exception: they come from a named AWS CLI profile.

---

## 1. How a repo gets a token

- `$HOME/home_secret.toml` is one flat TOML file: one full dotted key path and its value per line. The key paths are the maintainer's own; the template depends on no particular shape.
- When mise loads a repo, the `[env]` block of its `mise.toml` turns key paths into environment variables:

  ```toml
  [env]
  GITHUB_TOKEN = "{% raw %}{{{% endraw %} env.GITHUB_TOKEN | default(value=exec(command='uvx --from home-secret-toml hst get <key_path> || true')) {% raw %}}}{% endraw %}"
  ```

  - `env.GITHUB_TOKEN | default(...)`: a value already in the environment wins. CI injects its secrets that way (section 4), so `hst` is not needed there.
  - The `|| true` fallback matters: a failed `exec` aborts every mise command in the repo, not only the tasks that need the token. With it, an unreadable token is an empty string, which scripts treat as not set, and the `hst` error printed on each mise command names the missing key.

  `mise.toml` is the only place that maps a variable to its key path. Read it there; never assume a path.

- Scripts read a plain environment variable, such as `os.environ["GITHUB_TOKEN"]`.

The template uses these tokens:

| Variable | The value is |
| :--- | :--- |
| `GITHUB_TOKEN` | A GitHub token for the GitHub API: repo metadata, Actions secrets, tags and releases |
| `CLOUDFLARE_API_TOKEN` | A Cloudflare API token that can create and deploy Cloudflare Pages projects. Only repos with hosted docs use it. |

---

## 2. AWS credentials

Installing private packages, publishing, and removing a version all call AWS CodeArtifact, so they need AWS credentials. They never go through `home_secret.toml`:

- **Locally,** the tasks pass `--profile <aws_profile>` to the AWS CLI. The profile is a named profile in `~/.aws/config` (often AWS IAM Identity Center, refreshed with `aws sso login --profile <aws_profile>`), and its name is a `mise.toml` `[env]` value such as `AWS_CODEARTIFACT_PROFILE`.
- **In CI,** GitHub's OIDC token is exchanged for a short-lived role session (section 4); no AWS key is stored anywhere.
- The CodeArtifact authorization token that a task fetches with these credentials lives only in that task's shell, as `UV_INDEX_<INDEX_NAME>_PASSWORD`, and expires after 12 hours.

---

## 3. Non-secret organization values

`mise.toml` `[env]` also holds plain values shared by every internal repo: the DevOps AWS account id, the AWS profile names, the CodeArtifact region, domain, domain owner, and repository, and the S3 doc-host bucket and its profile (`DOC_HOST_S3_BUCKET`, `DOC_HOST_AWS_PROFILE`). They are not secrets, so they are written in the file directly, but they are still **organization facts**: read them from `mise.toml`, and never copy them into a skill, a doc page, or a test.

---

## 4. Hard rules for an AI

- **Never read, open, cat, grep, copy, or summarize `$HOME/home_secret.toml`, `~/.aws/credentials`, or the AWS SSO cache.** Not even to check whether a key exists.
- **Never print a secret value:** no `echo $GITHUB_TOKEN`, `env`, `printenv`, `mise env`, `hst get` outside `mise.toml`, `aws codeartifact get-authorization-token` outside the task that uses it, or `aws configure export-credentials`.
- Never write a secret into a file, a commit, a log, a notebook cell, a URL, or the chat.
- **To check which tokens are loaded,** print only True or False, from a repo root:

  ```bash
  mise exec -- python3 -c "import os; print({k: bool(os.environ.get(k)) for k in ['GITHUB_TOKEN', 'CLOUDFLARE_API_TOKEN']})"
  ```

- **To check AWS credentials,** run `aws sts get-caller-identity --profile <aws_profile>`. It prints the account and the role, never a key. If the session has expired, ask the user to run `aws sso login --profile <aws_profile>`; never log in for them.
- **To add a token,** add an `[env]` line with `hst get <key_path>` to `mise.toml`, and tell the user which key path to add to their file. The user writes the value.
- **When a task fails for a missing or rejected token or credential,** report the variable or profile name and stop. Do not work around it.
- **If the user pastes a secret into the chat,** do not use it, and ask them to rotate it: it is now in the transcript.

---

## 5. CI is different

GitHub Actions has no `home_secret.toml` and no AWS profile.

- The workflow's top-level `env:` maps repository secrets to the same variable names (`GITHUB_TOKEN`, `CLOUDFLARE_API_TOKEN`, `DEVOPS_AWS_ACCOUNT_ID`), so the `env.X | default(...)` templates in `mise.toml` take the CI value and skip `hst`.
- One-time setup tasks store those repository secrets on the GitHub repo. `GITHUB_TOKEN` is GitHub's own automatic token.
- AWS access comes from `aws-actions/configure-aws-credentials` with OIDC: GitHub's identity token assumes an IAM role in the DevOps account. The role and its trust policy are organization infrastructure, created outside the repo.
