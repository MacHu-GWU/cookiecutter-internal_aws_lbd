---
description: "One-time setup of a maintainer's Mac: global mise, uv, git and gh, shell activation, the per-repo tools mise installs (AWS CLI, Node.js, wrangler), the AWS CLI profile, the secrets file, where and with which scopes to create each token, account settings, and token rotation. Read when setting up a new machine, rotating a token, or when a tool is missing, AWS credentials have expired, or a token is missing or rejected (HTTP 401 or 403)."
---

# Machine Setup

Everything here is done **once per machine**, not per repo. Afterwards, every template repo works with `mise run inst`. Secrets and credentials follow `01-secrets.md`.

---

## 1. Global tools

| Tool | Install | Why it is global |
| :--- | :--- | :--- |
| mise | `brew install mise` | Installs each per-repo tool version once per machine, and runs the tasks |
| uv | `brew install uv` | `uvx` keeps one tool cache shared by all repos (for `hst`, `ruff`, ...). Each repo still pins its own uv version. |
| git, gh | `brew install git gh`, then `gh auth login` | `gh` reads CI runs and manages GitHub repos from the terminal |

Activate mise in the shell: add this line to `~/.zshrc`, then open a new terminal.

```bash
eval "$(mise activate zsh)"
```

Check with `mise --version`, `uv --version`, and `gh auth status`. In each repo, run `mise trust` once (mise asks the first time), then `mise install`, then `mise run inst`.

**Per-repo tools.** `mise.toml` `[tools]` also pins the AWS CLI (`awscli`), Node.js, and `npm:wrangler` (the Cloudflare CLI). `mise install` fetches them; nothing needs brew.

---

## 2. The AWS CLI profile

Every task that talks to CodeArtifact uses one named profile, `<aws_profile>`, whose name is in `mise.toml` `[env]` (`01-secrets.md` section 2).

1. The user creates the profile in `~/.aws/config`, usually with `aws configure sso --profile <aws_profile>`, using the start URL, account, and role the platform team gives them. An AI never edits `~/.aws/`.
2. When the session expires, the user runs `aws sso login --profile <aws_profile>`.
3. Check with `aws sts get-caller-identity --profile <aws_profile>`: the account must be the `AWS_CODEARTIFACT_DOMAIN_OWNER` in `mise.toml`.

A library with hosted docs also uses the doc-host profile in `DOC_HOST_AWS_PROFILE` (often the same one), which needs write access to the doc-host bucket.

The CodeArtifact role needs `codeartifact:GetAuthorizationToken`, `codeartifact:ReadFromRepository`, `sts:GetServiceBearerToken`, and, to publish or remove versions, `codeartifact:PublishPackageVersion` and `codeartifact:DeletePackageVersions`.

---

## 3. The secrets file

Create `$HOME/home_secret.toml` with one key path per token in `01-secrets.md` section 1, matching the `hst get <key_path>` commands in the repos' `mise.toml`. Then restrict it to the owner:

```bash
chmod 600 ~/home_secret.toml
```

- The user writes the values. An AI only says which key paths must exist.
- Never commit the file or copy it into a repo.

---

## 4. Tokens

| Variable | Where to create it | Scope |
| :--- | :--- | :--- |
| `GITHUB_TOKEN` | <https://github.com/settings/tokens> | Classic: `repo` and `workflow`. Or fine-grained, on the organization's repos, with Administration, Contents, Secrets, and Actions set to read and write. |
| `CLOUDFLARE_API_TOKEN` | <https://dash.cloudflare.com/profile/api-tokens> | Custom token: Account → Cloudflare Pages → Edit, on the company account. Only needed for repos with hosted docs. |

**Account settings, once each:**

- The GitHub organization must allow GitHub Actions to request OIDC tokens; the IAM role that CI assumes is created by the platform team, not per repo.
- For hosted docs, the Cloudflare account needs Zero Trust enabled with the **One-time PIN** login method, so Cloudflare Access can send codes to company email addresses.

**Rotating a token:**

1. Create the new token.
2. Replace the value in `home_secret.toml` (the user does this).
3. Run the True/False check in `01-secrets.md`.
4. A token that CI also uses (`CLOUDFLARE_API_TOKEN`) is stored as a repository secret too: rerun `mise run setup-cloudflare-token` for each repo with hosted docs, after the user's yes.

---

## 5. Diagnosing a missing tool, token, or credential

| What happens | Cause |
| :--- | :--- |
| The True/False check prints `False` | The key path is missing from `home_secret.toml`, or `mise.toml` points at the wrong path. |
| mise prints an `hst` error while loading the env | The file or the key path is missing. The `\|\| true` fallback keeps other tasks working. |
| The token is present, but a task fails with HTTP 401 or 403 | The token has expired or lacks scopes (section 4). |
| `aws: command not found`, or `wrangler: command not found` | `mise install` has not run in this repo. |
| `Error when retrieving token from sso: Token has expired`, or `ExpiredToken` | The AWS session expired: the user runs `aws sso login --profile <aws_profile>`. |
| `uv sync` fails with 401 on the private index | The CodeArtifact token was not fetched: the task was not run through mise, or the AWS profile failed. |
