---
description: "The release sequence from a finished change to the private CodeArtifact repository, a GitHub tag and release, and optionally the hosted docs: who does each step, the publish and release tasks, and the approval gate before each public step. Read when publishing a new version."
---

# Release

---

## 1. Sequence

| Step | Who | How |
| :--- | :--- | :--- |
| 1. Bump the version (`23-versioning-and-changelog.md`) | AI, after the user's yes on the number | edit `pyproject.toml`, then `mise run inst` |
| 2. Write that version's changelog section | AI | `23-versioning-and-changelog.md` |
| 3. Verify | AI | `mise run cov`, `mise run lint`, `mise run build-doc` all pass |
| 4. Commit and push to `main` | AI, after the user's yes | git |
| 5. Publish to CodeArtifact | AI, after the user's yes | Check the AWS session (`01-secrets.md` section 4), then `mise run publish` (builds, fetches the CodeArtifact token, then `uv publish`, `05-codeartifact.md` section 4) |
| 6. Create the GitHub tag and release | AI, after the user's yes | `mise run release` (idempotent) |
| 7. Deploy the latest hosted docs (only a library with hosted docs) | AI, after the user's yes | `git push origin main:doc` (`21-cloudflare-pages.md` section 3) |
| 8. Upload this version's docs to S3 (only a library with hosted docs) | AI, after the user's yes | `mise run build-doc`, `mise run deploy-versioned-doc`, `mise run deploy-latest-doc` (`22-s3-versioned-docs.md` section 3) |
| 9. Regenerate the API skill, if the public API changed | AI | `pywf-priv-write-pypi-skill`, then commit after the user's yes |

---

## 2. Rules

- **Steps 5 to 8 are irreversible and visible to the whole organization.** One yes per step (`03-mise.md` section 4): a yes to publish is not a yes to release.
- **Never delete or move a published tag, and never delete a published version from CodeArtifact** (`05-codeartifact.md` section 5). Fix a bad release with a new PATCH version.
- **A missing or rejected token or AWS credential** is reported by its variable or profile name, and the release stops there (`01-secrets.md`).
