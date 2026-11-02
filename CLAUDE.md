# CLAUDE.md

This is the **tpl repo** of a cookiecutter template for internal proprietary AWS Lambda projects: closed source, multi-environment Lambda functions deployed with AWS CDK, private packages from AWS CodeArtifact, docs on Cloudflare Pages and S3. The template is never edited directly: it is generated from a runnable **seed repo** (path: `CCTPL_SEED_DIR` in `mise.toml`) and published from here.

All maintenance rules live in the `cctpl-*-cn` skill family under `.claude/skills/`. Start with `cctpl-base-cn/SKILL.md`; it is the single source of truth and says which invoker fits which job:

| Job | Skill |
| :--- | :--- |
| Change the template (content or mechanism) | `/cctpl-change-cn` |
| Add, change, or remove a cookiecutter variable | `/cctpl-add-param-cn` |
| Regenerate the template from the seed and run all checks | `/cctpl-sync-cn` |
| Try a generated project locally | `/cctpl-try-cn` |
| Write this repo's changelog section for the current version | `/cctpl-changelog-cn` |
| Prepare a release (user only) | `/cctpl-release-cn` |
| Verify the published template (user only) | `/cctpl-verify-cn` |
| Copy this skill family to another tpl / seed repo pair, once (user only) | `/cctpl-fork-cn` |

Rules that hold even before a skill is loaded (details: `cctpl-base-cn/references/04-safety-rules.md`):

- Never run git write operations, `mise run publish-template` or `mise run publish-presets`; print the commands for the user instead.
- Never edit `cookiecutter.json`, `{{ cookiecutter.package_name }}-project/` or `README.rst` by hand; change the seed (or the parameterization) and run `mise run sync`.
- Never edit the version here: the seed and this repo share one version, its only source is the seed's `pyproject.toml`, and `mise run sync` copies it here.
- Never read `$HOME/home_secret.toml` or `~/.aws/`, and never print a token. Generated projects install from AWS CodeArtifact, so only a project rendered with `TRIAL_PRESET` (`.mise/tasks/cctpl/pair.py`) can install; `test-output`, `try-template` and `e2e` use it and fetch a read-only CodeArtifact token with its AWS profile.

## Current Status

Open items for this pair (keep this short; delete items when done):

- Bootstrapped from cookiecutter-pywf_open_source (structure), cookiecutter-pywf_internal_proprietary (CodeArtifact, Trial Preset) and cookiecutter-aws_lbd (Lambda, CDK). The shared version is the seed's `1.0.0`. Still to do: create the GitHub repo `MacHu-GWU/cookiecutter-internal_aws_lbd` and push, tag the seed `1.0.0`, `/cctpl-release-cn`, `mise run publish-template`, then `/cctpl-verify-cn`.
- `presets/bmt-sanhe-dev.json`: a bmt project still depends on the esc-only demo package `esc-aws-org-struct`; bmt users replace it after generating.
