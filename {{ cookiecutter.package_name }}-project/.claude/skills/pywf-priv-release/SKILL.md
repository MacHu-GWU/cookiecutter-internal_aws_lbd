---
name: pywf-priv-release
description: "Release a new version of a pywf internal proprietary Python library: bump the version, make sure the changelog, tests, and docs are ready, then publish to the private AWS CodeArtifact repository, create the GitHub release, and, for a library with hosted docs, deploy the latest docs to Cloudflare Pages and this version's docs to S3, asking for the user's yes before each irreversible step. Use when the user asks to release, publish, ship, or cut a new version."
---

Take the repo from "the change is done" to "the version is in CodeArtifact and tagged on GitHub". Stop for the user's yes before every step that cannot be undone.

Read ../pywf-priv-base/SKILL.md, then:
- ../pywf-priv-base/references/01-secrets.md
- ../pywf-priv-base/references/03-mise.md
- ../pywf-priv-base/references/05-codeartifact.md
- ../pywf-priv-base/references/23-versioning-and-changelog.md
- ../pywf-priv-base/references/24-release.md
- ../pywf-priv-base/references/21-cloudflare-pages.md (only for a library with hosted docs)
- ../pywf-priv-base/references/22-s3-versioned-docs.md (only for a library with hosted docs)

## Steps

1. **Version.**
   - Show the last tag and the current `pyproject.toml` version.
   - If they are equal, propose a bump (PATCH, MINOR, or MAJOR) with a one-line reason from the `api.py` diff, and apply it after the user's yes. Then `mise run inst`, so `uv.lock` records it.
2. **Changelog.** If `release-history.rst` has no section for the target version, or a stale one, run the `pywf-priv-changelog` steps first.
3. **Checks.**
   - `mise run cov`, `mise run lint`, and `mise run build-doc` pass.
   - `git status` is clean, apart from the version bump (`pyproject.toml`, `uv.lock`) and the changelog edit.
   - `aws sts get-caller-identity --profile <aws_profile>` succeeds. If the session expired, ask the user to log in, and wait.
   - On any failure, report it and stop.
4. **Commit and push.** Show the commit message; commit and push to `main` after the user's yes.
5. **Publish.** Ask: "Publish `<package_name>` `<version>` to CodeArtifact?" After the user's yes, run `mise run publish`.
6. **GitHub release.** Ask, and run `mise run release` after the user's yes.
7. **Hosted docs.** Only if the library has hosted docs, one yes each:
   - Cloudflare Pages (latest): `git push origin main:doc`, then watch the `deploy-doc` job.
   - S3 (this version's frozen copy): `mise run build-doc` on the tagged commit, then `mise run deploy-versioned-doc` and `mise run deploy-latest-doc`.
8. **Report.** Give the CodeArtifact console URL (printed by `publish`), the release URL, and the docs URLs if any.

## Boundaries

- Never run `mise run remove-pkg-version` as part of a release, not even to redo a failed publish of the same version. A bad release gets a new PATCH version.

Next step: `pywf-priv-write-pypi-skill`, if the public API changed.
