---
name: pywf-priv-fix-ci
description: "Diagnose and fix a red GitHub Actions run (test or deploy-doc job, including AWS OIDC and CodeArtifact install failures) or a failed Cloudflare Pages docs deploy of a pywf internal proprietary Python library, or add or drop a supported Python version. Use when the user says CI, the tests on GitHub, the install step, the docs deploy, or Cloudflare Pages fails or shows warnings, or asks to add or drop a Python version."
---

Find from the logs why CI or the docs deploy is red, fix the cause in the repo, and confirm it is green again. Also add or drop a Python version.

Read ../pywf-priv-base/SKILL.md, then:
- ../pywf-priv-base/references/04-python-versions.md
- ../pywf-priv-base/references/05-codeartifact.md
- ../pywf-priv-base/references/20-github-actions.md
- ../pywf-priv-base/references/21-cloudflare-pages.md (only for a docs deploy failure)
- ../pywf-priv-base/references/26-python-release-cycle.md (only for adding or dropping a Python version)

## Steps

1. **Find the red job and its log** with the commands in `20-github-actions.md` section 3. Quote the decisive log lines to the user.
2. **Reproduce locally** where possible: `mise run inst` for install failures, `mise run cov` for tests, `mise run build-doc` for docs. If it passes locally, compare the Python version, the AWS identity (local profile versus the CI role), the `MISE_DISABLE_TOOLS` lists, and the working directory.
3. **Fix the cause, not the symptom.**
   - Never skip, xfail, or delete a failing test to turn CI green without the user's yes.
   - Never narrow a matrix permanently to hide a failure.
   - An IAM role, its trust policy, or a Cloudflare Access application is organization infrastructure: report what must change and who changes it; never work around it in the workflow.
4. **Verify.** Rerun locally. Then, after the user's yes, push the fix, or for an infrastructure flake run `gh run rerun <run_id> --failed`. Check the new run with `gh run view`.

## Boundaries

- Reading logs and runs needs no approval. Pushing, rerunning, deleting caches, rerunning setup tasks, and pushing to `doc` each need the user's yes.

Next step: `pywf-priv-upgrade-deps` when the cause is a dependency, or when a Python version change lifts or adds dependency caps; `pywf-priv-changelog` to record a Python version change.
