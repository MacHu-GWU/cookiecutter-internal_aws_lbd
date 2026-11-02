---
name: pywf-priv-setup-machine
description: "Guide the maintainer through setting up a Mac for pywf internal proprietary Python libraries: global mise, uv and gh, shell activation, the mise-managed AWS CLI and wrangler, the AWS CLI profile for CodeArtifact, the home_secret.toml key paths, and the GitHub and Cloudflare tokens, verified without printing any secret. Use when the user sets up a new machine, asks how the environment works, rotates a token, or a task fails for a missing tool, token, or expired AWS session."
---

Take a machine from nothing to "every template repo runs `mise run inst` against the private index, and every setup task finds its token", as a guided runbook: check, report, and leave every step that touches a secret or a credential to the user.

Read ../pywf-priv-base/SKILL.md, then:
- ../pywf-priv-base/references/01-secrets.md
- ../pywf-priv-base/references/02-machine-setup.md

## Steps

1. **Check the tools:** `mise --version`, `uv --version`, `gh auth status`, and `mise activate` in `~/.zshrc`. In a template repo, also `mise install` and then `aws --version`. Report what is present and missing in a short table.
2. **Install what is missing.** Show the `brew install ...` lines, and run them after the user's yes. `gh auth login` is interactive; run it only if the user asks.
3. **AWS profile.**
   - Read the profile name from `mise.toml` `[env]` (`AWS_CODEARTIFACT_PROFILE`).
   - Run `aws sts get-caller-identity --profile <aws_profile>`, and compare the account with `AWS_CODEARTIFACT_DOMAIN_OWNER`.
   - If the profile is missing or expired, give the user the `aws configure sso` or `aws sso login` command to run themselves. Never open `~/.aws/`.
4. **Secrets file.**
   - Check only that the file exists and its permissions, with `ls -l ~/home_secret.toml`. Never read its content.
   - If it is missing, list the key paths in the `[env]` block of `mise.toml`, say what each value is for, and show the `chmod 600` line.
5. **Tokens.** For each token, give the creation URL and the exact scopes. `CLOUDFLARE_API_TOKEN` is needed only for repos with hosted docs. The user creates each token and writes it into the file. Never ask for a token in the chat.
6. **Verify.** In a template repo, run `mise trust` if needed, then `mise run inst` (it proves the AWS profile and the private index) and the True/False check. Report each variable as present or missing, naming the `mise.toml` key path of a missing one.

## Boundaries

- The user makes account-level settings, such as AWS IAM Identity Center access or Cloudflare Zero Trust, in the browser. Give the link and say what to click.

Next step for a new repo: `pywf-priv-setup-repo`.
