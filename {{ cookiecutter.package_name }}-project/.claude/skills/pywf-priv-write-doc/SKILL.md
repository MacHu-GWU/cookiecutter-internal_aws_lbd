---
name: pywf-priv-write-doc
description: "Write or update a user-facing Sphinx documentation page of a pywf internal proprietary Python library, as reStructuredText or as a Jupyter notebook with raw reStructuredText cells for cross-references, then build and check it. Use when the user asks to document a feature for its users, write a guide or tutorial page, add a notebook example, or fix the docs. Maintainer knowledge goes to pywf-priv-write-maintain-skill instead."
---

Write or update one user docs page under `docs/source/` that builds cleanly, appears in the sidebar, and links correctly to the API reference and other pages.

Read ../pywf-priv-base/SKILL.md, then:
- ../pywf-priv-base/references/14-sphinx.md
- ../pywf-priv-base/references/15-docfly.md
- ../pywf-priv-base/references/16-furo.md (only when changing the look or the theme)
- ../pywf-priv-base/references/17-sphinx-design.md (only when the page needs layout or widgets: cards, tabs, dropdowns, badges, buttons)
- ../pywf-priv-base/references/18-nbsphinx.md (only for notebook pages)
- ../pywf-priv-base/references/19-knowledge-channels.md

Templates: ../pywf-priv-base/assets/notebook-page-template.ipynb and ../pywf-priv-base/assets/raw-rst-cell.json.

## Steps

1. **Pick the channel, the format, and the place.**
   - Check the fact belongs in user docs (`19-knowledge-channels.md` section 2). How to maintain this repo goes to `pywf-priv-write-maintain-skill`; say so, and stop.
   - A notebook for runnable usage guides, `.rst` for concepts and design notes. If the user did not say, choose, and state the choice.
   - List the existing page folders, then choose the `NN-Title` folder that puts the page at the right sidebar position.
2. **Gather facts** from `api.py` and the docstrings of what you document. Examples import from `<package_name>.api`, as users would.
3. **Write.**
   - Give the page a unique label and a title (in a notebook, both in a raw reStructuredText cell).
   - Use cross-reference roles for API names, and `:ref:` for other pages.
   - Edit notebooks with `NotebookEdit` or `nbformat`.
4. **Run notebooks** with the `nbconvert` command in `18-nbsphinx.md` section 5. Every cell must succeed; the outputs are committed.
5. **Build and check** as in `14-sphinx.md` section 4: no new warnings, 0 unresolved cross-references (`check_doc_xrefs.py`, `14-sphinx.md` section 2.2), and the page in the sidebar with the right title. For layout work, also run the visual check.

## Boundaries

- Never edit `docs/source/api/`. To improve the API pages, improve the docstrings, and say so.
- Keep `README.rst` short; long material goes in a docs page the README links to.
- Never deploy the docs here. Hosted docs are deployed by a push to `doc`, after the user's yes, as part of `pywf-priv-release` or on request.

Next step: `pywf-priv-changelog`.
