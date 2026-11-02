---
description: "Versioned docs on the organization's S3 doc-host bucket: why S3 is kept next to Cloudflare Pages (one frozen copy per released version), the bucket layout, the deploy-versioned-doc, deploy-latest-doc and view-latest-doc tasks, when to run them, and diagnosing a failed upload. Read when a library with hosted docs is released, when someone needs the docs of an older version, or when an S3 docs upload fails."
---

# S3 Versioned Docs

Cloudflare Pages (`21-cloudflare-pages.md`) only ever serves the **latest** docs. Consumers of an internal library often stay on an older version for months, and they need the docs of the version they run. So a library with hosted docs also keeps one frozen copy per released version on the organization's S3 doc-host bucket. Neither host replaces the other.

---

## 1. The bucket

- **Values** in `mise.toml` `[env]` (`01-secrets.md` section 3): `DOC_HOST_S3_BUCKET`, the bucket, and `DOC_HOST_AWS_PROFILE`, the AWS profile that can write to it.
- **Layout:**

  | Prefix | Content |
  | :--- | :--- |
  | `s3://<bucket>/projects/<package_name>/<version>/` | The docs of one released version. Written once, at its release. |
  | `s3://<bucket>/projects/<package_name>/latest/` | The docs of the newest release, overwritten at each release |

- **URL:** `https://<bucket>.s3.amazonaws.com/projects/<package_name>/<version>/index.html` (or `latest/`).
- **Who can read it** is set by the bucket policy, which is organization infrastructure: never change it from a repo.

---

## 2. Tasks

All run locally with `DOC_HOST_AWS_PROFILE`; CI has no S3 access. Each uploads the current `docs/build/html` with `aws s3 sync`, so run `mise run build-doc` first, on the commit being released.

| Task | What it does |
| :--- | :--- |
| `deploy-versioned-doc` | Upload to `<version>/`, the `pyproject.toml` version |
| `deploy-latest-doc` | Upload to `latest/` |
| `view-latest-doc` | Open the `latest/` URL in the browser |

Both `deploy-*` tasks write to a shared bucket, so each runs only after the user's yes (`03-mise.md` section 4).

---

## 3. When

- **At each release** of a library with hosted docs, after the version is published and tagged: `build-doc`, then `deploy-versioned-doc`, then `deploy-latest-doc`.
- **Never** run `deploy-versioned-doc` for a version that is not released, or from a commit other than its tag: the copy is meant to match what consumers installed. A docs fix for an old version goes into the next release.
- A docs-only change between releases updates Cloudflare Pages (and, if the user wants, `latest/`), never a `<version>/` folder.

---

## 4. Diagnosing

| Symptom | Fix |
| :--- | :--- |
| `DOC_HOST_AWS_PROFILE environment variable not set` | The task was not run through mise, or `mise.toml` lacks the value |
| `ExpiredToken`, or an SSO error | The user runs `aws sso login --profile <aws_profile>` for the doc-host profile (`02-machine-setup.md`) |
| `AccessDenied` on `PutObject` | The profile's role cannot write to the bucket: report it as organization infrastructure |
| The page opens without styles, or 403 | Check the URL ends in `index.html`; access is the bucket policy's job, not the repo's |
