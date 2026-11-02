---
description: "Optional hosted docs on Cloudflare Pages behind Cloudflare Access with a one-time PIN sent to company email: when a library needs it, the one-time setup tasks, the Access application the user creates by hand, deploying through the doc branch, and diagnosing a failed deploy. Read when deciding whether a library gets hosted docs, setting them up, or when a docs deploy fails or the site is not protected."
---

# Cloudflare Pages

Hosted docs are optional. Most internal libraries never deploy their docs: the README and the `pypi-<package_name>` skill are enough (`19-knowledge-channels.md`). A library gets hosted docs when people, not only agents, need to browse its guides.

Cloudflare Pages serves only the latest docs. The docs of each released version are kept on the S3 doc-host bucket, described in the next reference; a library with hosted docs uses both.

---

## 1. The site

- **Project name:** `<slug>`. The site is `https://<slug>.pages.dev/`, which is also `[project.urls].Documentation` in `pyproject.toml`; `update-github-metadata` makes it the GitHub homepage.
- **A library without hosted docs** deletes `Documentation` from `[project.urls]`, and the Cloudflare Pages badges and links from `README.rst`, so nothing points at a site that does not exist. Its GitHub repo then has no homepage.
- **Content:** `docs/build/html`, from `mise run build-doc` (`14-sphinx.md`), uploaded as is by `wrangler pages deploy`. Cloudflare builds nothing itself, so notebooks ship with committed outputs (`18-nbsphinx.md`).
- **Access:** only colleagues. Cloudflare Access sits in front of the site and asks for an email address; only addresses in `@<company_domain>` get a one-time PIN, and the PIN unlocks the site.

---

## 2. One-time setup

Each step changes an external service, so each runs only after the user's yes (`03-mise.md` section 4).

1. `mise run create-pages-project`: `wrangler pages project create <slug> --production-branch main`, with `CLOUDFLARE_API_TOKEN` (`01-secrets.md`).
2. `mise run setup-cloudflare-token`: stores `CLOUDFLARE_API_TOKEN` as a GitHub Actions secret, for the `deploy-doc` job (`20-github-actions.md`).
3. **Protect the site, by hand, in the Cloudflare dashboard.** No task does this; give the user these steps:
   1. Zero Trust → Access → Applications → Add an application → **Self-hosted**.
   2. Application domain: `<slug>.pages.dev`. Add a second domain, `*.<slug>.pages.dev`, so preview deployments are protected too.
   3. Policy: action **Allow**, include **Emails ending in** `@<company_domain>`.
   4. Login methods: **One-time PIN** only.
   
   The **Enable access policy** switch in the Pages project's settings protects only the preview deployments, not `<slug>.pages.dev`; the application above covers both.
4. **Check** in a private browser window: `https://<slug>.pages.dev/` must show the Cloudflare Access login, not the docs. Until it does, deploy nothing that is not public information.
5. `mise run update-github-metadata`: sets the GitHub repo homepage to the docs URL.

---

## 3. Deploying

| Way | When |
| :--- | :--- |
| `git push origin main:doc` | The normal way. CI runs the tests, builds, and deploys (`20-github-actions.md` section 1). |
| `mise run build-doc`, then `mise run deploy-pages` | A local deploy, when CI is unavailable |

Both need the user's yes. Deploy after a release that changed user-facing behavior, or after a docs-only change the user wants published.

---

## 4. Diagnosing

| Symptom | Fix |
| :--- | :--- |
| `deploy-pages` fails with an authentication error | `CLOUDFLARE_API_TOKEN` is missing, expired, or lacks Pages edit permission (`01-secrets.md`); in CI, rerun `setup-cloudflare-token` |
| `Project not found` | `create-pages-project` has not run, or the project name differs from `<slug>` |
| The site opens without a login | The Access application is missing, or covers the wrong domain: redo section 2 step 3 |
| A colleague gets no PIN | Their address is not in `@<company_domain>`, or One-time PIN is not an enabled login method |
| The hosted site differs from the local build | The deploy came from an older `doc` branch: push `main` to `doc` again |
