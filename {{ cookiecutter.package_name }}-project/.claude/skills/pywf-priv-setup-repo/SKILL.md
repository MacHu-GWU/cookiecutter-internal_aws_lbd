---
name: pywf-priv-setup-repo
description: "Take a freshly generated pywf internal proprietary Python library repo live: verify it locally against the private CodeArtifact index, create and push the private GitHub repo, set its metadata and Actions secrets, enable CI with AWS OIDC, and optionally set up Cloudflare Pages docs behind Cloudflare Access, with the user's yes before each external step. Use when the user has a new repo from the template and wants it on GitHub with CI, and possibly hosted docs."
---

Turn a local repo generated from the template into a live private project, with GitHub and CI green, and hosted docs only if the library needs them. Each external step waits for the user's yes; one yes covers one step.

Read ../pywf-priv-base/SKILL.md, then:
- ../pywf-priv-base/references/01-secrets.md
- ../pywf-priv-base/references/03-mise.md
- ../pywf-priv-base/references/05-codeartifact.md
- ../pywf-priv-base/references/06-uv-dependencies.md (section 2: private packages)
- ../pywf-priv-base/references/20-github-actions.md
- ../pywf-priv-base/references/21-cloudflare-pages.md (only for hosted docs)

## Steps

1. **Preflight.**
   - Run the token True/False check and `aws sts get-caller-identity --profile <aws_profile>`. If `GITHUB_TOKEN` is `False` or the AWS session fails, stop and hand off to `pywf-priv-setup-machine`.
   - Read `[project].name` from `pyproject.toml`, and run `git remote -v`.
   - No `origin` yet: propose the GitHub owner (the organization) and the repo name `<package_name>-project`, and wait for the user to confirm. Step 3 creates the repo and remote.
   - `origin` exists: show the GitHub repo URL, the `<slug>`, and the docs URL the tasks will use (`.mise/tasks/utils.py` derives them from `origin` and the project name), and ask the user to confirm.
   - Ask whether this library needs hosted docs. The default is no.
2. **Local green.** `mise run inst`, `mise run cov`, `mise run lint`, and `mise run build-doc` pass; template-fresh code should. Fix any failure before going online. Check that every private package is pinned in `[tool.uv.sources]` (`06-uv-dependencies.md` section 2).
3. **GitHub repo.** If none exists, propose `gh repo create <owner>/<repo> --private --source . --remote origin --push`, and run it after the user's yes. Never `--public`. Then show the URL and slug derived from the new `origin`.
4. **GitHub metadata.** `mise run update-github-metadata`, after the user's yes.
5. **AWS secret for CI.** `mise run setup-github-secrets`, after the user's yes. Confirm with `gh secret list` (names only).
6. **CI.** Push `main` and watch the `test` job with `gh run list` and `gh run view`. If the OIDC step fails because the role's trust policy does not allow this repo, report it as an organization step for the user, with the repo's full name; do not try to change IAM.
7. **Hosted docs (only if the user said yes in step 1).** Follow `21-cloudflare-pages.md` section 2 step by step, one yes each: `create-pages-project`, `setup-cloudflare-token`, the Cloudflare Access application (the user does it in the dashboard), the private-window check, then the first deploy with `git push origin main:doc`.
8. **Confirm.** Report the CI run, and the docs site if any, as green or red. Diagnose anything red with `20-github-actions.md` or `21-cloudflare-pages.md`, or hand off to `pywf-priv-fix-ci`.

## Boundaries

- Never change repo visibility, branch protection, or any repo setting not listed in these steps.
- Never deploy docs before the Cloudflare Access check passes.

Next steps: `pywf-priv-add-module` to start coding, `pywf-priv-release` for the first version, and `pywf-priv-write-maintain-skill` once there is something to say about maintaining it.
