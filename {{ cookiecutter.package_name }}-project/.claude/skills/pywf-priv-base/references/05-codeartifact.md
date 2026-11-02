---
description: "AWS CodeArtifact as the private PyPI: the [[tool.uv.index]] block and why it is explicit, how codeartifact-env.sh turns AWS credentials into a uv index token, running uv commands that reach the private index, the publish URL, deleting a version, and how consumers install the library. Read when a command must reach the private index, when publishing, or when uv reports 401 or a private package not found."
---

# AWS CodeArtifact

The library is closed source, so it is never uploaded to PyPI. Its releases, and every other internal library it depends on, live in one AWS CodeArtifact repository: the private PyPI. Public packages still come from PyPI.

---

## 1. The values

All in `mise.toml` `[env]` (`01-secrets.md` section 3), shared by every internal repo:

| Variable | Meaning |
| :--- | :--- |
| `AWS_CODEARTIFACT_PROFILE` | The local AWS CLI profile, `<aws_profile>` |
| `AWS_CODEARTIFACT_REGION` | `<aws_region>` |
| `AWS_CODEARTIFACT_DOMAIN_OWNER` | The account that owns the domain, `<aws_account_id>` |
| `AWS_CODEARTIFACT_DOMAIN` | `<codeartifact_domain>` |
| `AWS_CODEARTIFACT_REPO` | `<codeartifact_repo>` |

From them, the index URL is `https://<codeartifact_domain>-<aws_account_id>.d.codeartifact.<aws_region>.amazonaws.com/pypi/<codeartifact_repo>/simple/`.

---

## 2. The private index in `pyproject.toml`

```toml
[[tool.uv.index]]
name = "<index_name>"
url = "https://<codeartifact_domain>-<aws_account_id>.d.codeartifact.<aws_region>.amazonaws.com/pypi/<codeartifact_repo>/simple/"
authenticate = "always"
explicit = true

[tool.uv.sources]
<private_dist_name> = { index = "<index_name>" }
```

- **`explicit = true`:** uv uses this index only for the packages pinned to it in `[tool.uv.sources]`. Every other package resolves from PyPI, so a public package can never be shadowed by a same-named upload to the private repository.
- **`[tool.uv.sources]`** pins each private package to the index. A private package that is not pinned is looked up on PyPI, where it either does not exist or, worse, is someone else's package of the same name.
- **List every private package explicitly, transitive ones included.** uv applies `[tool.uv.sources]` only to the requirements this project declares itself; the sources in a dependency's own `pyproject.toml` are never read. So when private package A needs private package B, this project lists **both**: each as a requirement in `dependencies` (or in the extra that needs it), and each in `[tool.uv.sources]`. Find the private packages in the tree with `uv tree`, and check each name against the CodeArtifact repository.
- **`authenticate = "always"`:** uv errors at once when credentials are missing, instead of trying anonymously and failing later.
- The index `name` sets the credential variables: `UV_INDEX_<INDEX_NAME>_USERNAME` and `UV_INDEX_<INDEX_NAME>_PASSWORD`, with the name uppercased and every non-alphanumeric character replaced by `_`. Renaming the index means updating `.mise/tasks/codeartifact-env.sh` and the `publish` task too.

---

## 3. Authentication: `.mise/tasks/codeartifact-env.sh`

Tasks that reach the private index source this file first (`. .mise/tasks/codeartifact-env.sh`). It:

1. sets `UV_INDEX_<INDEX_NAME>_USERNAME=aws`;
2. calls `aws codeartifact get-authorization-token` with the domain and owner from `[env]`, using `--profile <aws_profile>` locally, and the ambient OIDC credentials when `CI` is set;
3. exports the token as `UV_INDEX_<INDEX_NAME>_PASSWORD`, for that shell only. It is valid for 12 hours.

**Running uv by hand.** A raw `uv sync`, `uv lock`, `uv add`, or `uv tree --outdated` that has to read the private index fails with 401 outside a task. Wrap it so the token exists only for that command, and is never printed:

```bash
mise exec -- sh -c '. .mise/tasks/codeartifact-env.sh && uv lock --upgrade-package <dist_name>'
```

---

## 4. Publishing

`mise run publish` runs `build`, sources `codeartifact-env.sh`, copies the index credentials into `UV_PUBLISH_USERNAME` and `UV_PUBLISH_PASSWORD`, prints the package URL and the AWS console URL (`.mise/tasks/publish.py`), and runs `uv publish --publish-url https://<codeartifact_domain>-<aws_account_id>.d.codeartifact.<aws_region>.amazonaws.com/pypi/<codeartifact_repo>/`. The publish URL has no `/simple/`.

- In CodeArtifact the package name is normalized: `<slug>`.
- The package's versions are listed in the AWS console at `https://<aws_region>.console.aws.amazon.com/codesuite/codeartifact/d/<aws_account_id>/<codeartifact_domain>/r/<codeartifact_repo>/p/pypi/<slug>/versions`.

---

## 5. Deleting a version

Unlike PyPI, CodeArtifact lets a version be deleted (`mise run remove-pkg-version`, `03-mise.md` section 4). Treat it as irreversible anyway:

- Consumers' `uv.lock` files pin the hash of the published files. Re-publishing the same version with different content breaks every one of those locks.
- Fix a bad release with a new PATCH version. Delete only a version that was never consumed, and only on the user's explicit request.
- If a version was deleted and re-published, consumers must run `uv cache clean <slug>` before they can install it.

---

## 6. How other projects install this library

A consuming project needs the same private index, plus a requirement and a `[tool.uv.sources]` line for this library **and for every private package this library depends on** (section 2 applies to the consumer too). Its own install task sources a `codeartifact-env.sh` the same way. The README install section shows this, and points to the `pypi-<package_name>` skill for usage.
