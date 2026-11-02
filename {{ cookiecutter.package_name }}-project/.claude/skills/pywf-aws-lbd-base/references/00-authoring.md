---
description: "How this skill itself is written: one topic per file, general files that never mention a specific technology, backward-only citations, links pinned to a release tag, placeholders, how to carry the skill to another project template, and what goes in the skill versus a docstring. Read before adding, editing, or renaming any file of this skill, or copying it to another template."
---

# Authoring This Skill

---

## 1. One topic per file

Each reference covers one topic that can change on its own. When a rule changes, exactly one file changes. Split a file when two of its parts could change independently.

---

## 2. General files and specific files

- **General files** (`01` to `08`) describe the AWS project conventions shared by every template of this kind: runtime, environment, config, boto session, the `one` singleton. They never mention a specific technology of this template (its deployment tool, its resource kinds, its tasks), and never cite a specific file.
- **Specific files** (`09` and up) describe what only this template has. Each one's file name starts with a topic prefix: `lbd-` for the Lambda functions and everything that ships them (the devops environment, the config in SSM, the layer, the source asset), `cdk-` for the CDK code. They are ordered by how close they are to deployment: the code first, then CDK, then shipping.
- A fact that both need belongs in the general file; the specific file cites it.
- **Check:** outside of links, the general files contain none of the specific words. In this template: `cdk`, `stack`, `CloudFormation`, `cft`, `lambda`, `lbd`, `layer`, `devops`.

---

## 3. Cite backward only

A reference cites only lower-numbered references, written as `` `NN-slug.md` ``. When a file needs a fact from a later one, state the fact without citing it, or move it down. SKILL.md may cite any reference.

---

## 4. Links and versions

- The skill's version is the seed repo's version in `pyproject.toml`, and every link to code points to the git tag of that version: `https://github.com/<owner>/<repo>/blob/<version>/<path>`. The tag has no `v` prefix.
- Link to a file to show a rule in practice; never copy its code into a reference.
- On a new version: change the version in SKILL.md, replace the tag in every link, then check every link resolves.

---

## 5. File shape and wording

- **Name:** `NN-slug.md`. **Shape:** YAML frontmatter with only `description`, one H1, numbered H2 sections separated by `---`.
- **`description`:** one double-quoted string, what the file holds, then a trigger starting with "Read when" or "Read before". The SKILL.md index copies the trigger; regenerate it with `python3 .claude/skills/pywf-priv-base/scripts/update_skill_index.py --skill_dir .claude/skills/pywf-aws-lbd-base`, never edit it by hand.
- **Placeholders:** `<package_name>` (import package), `<env>` / `<ENV>` (environment name, lower / upper case), `<x>` (the short name of a resource, such as a stack or a Lambda function). Names from the seed repo appear only in links.
- **Approval wording:** "the user's yes", and "one yes covers one step".

---

## 6. Carrying the skill to another template

Copy the whole skill, rename it after the new template, and change the link prefix to the new repo and tag. Keep the general files that still hold and edit the ones that changed; replace the specific files with the new template's own.

---

## 7. The skill or a docstring

The skill is the source of truth for conventions; a docstring is the source of truth for the code it sits on. Each piece of knowledge lives in exactly one of them.

| | The skill | A docstring |
| :--- | :--- | :--- |
| Scope | a rule that holds in more than one place | one function, class, or module |
| Holds | naming patterns, layering, the deploy flow, which tasks need a yes, which files a change touches, why the design is what it is | what the code does, its parameters, return value, and exceptions, why its implementation looks the way it does, its own pitfalls |
| Changes when | the rule changes | the code changes |

- A rule that applies in one place only goes in that place's docstring; the skill does not restate it, and may link to the code.
- A rule that applies in several places goes in the skill; a docstring neither restates it nor names the skill or a reference file. Citations go one way, from the skill to the code, through pinned links (section 4), so renaming or renumbering a reference never breaks the code.
- When the code and the skill disagree on a local detail, the code wins.
