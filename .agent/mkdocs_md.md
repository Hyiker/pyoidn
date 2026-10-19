# MkDocs Markdown Rules

Apply these rules to `docs/`, `mkdocs.yml`, README links, and generated API reference.

## Stack and Syntax

- The project uses MkDocs Material, mkdocstrings' Python handler, and the Markdown
  extensions configured in `mkdocs.yml`. Keep this stack for documentation changes.
- Write new pages as Markdown (`.md`). Use ordinary fenced code blocks with a
  language and existing admonition/formatting extensions where useful.
- Do not add Sphinx/MyST directives such as `{toctree}` or `{include}` to MkDocs
  pages, or assume an unconfigured extension will render.
- API reference pages use mkdocstrings directives, for example:

  ```markdown
  # Device

  ::: pyoidn.device
  ```

- Python docstrings use Sphinx-style parameter/return/raises fields because the
  Python handler has `docstring_style: sphinx`. This setting does not make the
  site a Sphinx project.

## Navigation, Links, and Assets

- Add user-facing pages to the appropriate section of `mkdocs.yml` navigation.
  Keep `docs/api/index.md` links aligned with available reference pages.
- Resolve links and image paths relative to the Markdown file. Check root README
  links on GitHub separately from links in the built site.
- Keep README images in `imgs/`; use `docs/images/` for new site-only assets and
  provide meaningful alt text.
- Link to shared material rather than duplicating long examples. Do not introduce
  symlinks or include directives requiring a new plugin for a small docs change.

## Validation

- Use the Python environment selected in `.agent/python_rules.md` and dependencies
  from `requirements-docs.txt` when building user-facing documentation.
- Run `python -m mkdocs build --strict` from the repository root, matching the CI
  strictness. Investigate warnings rather than suppressing them globally.
- API reference generation should not require loading native OIDN libraries.
- For navigation or layout changes, preview the affected pages and verify code
  blocks, reference rendering, and images. Do not commit generated `site/` output.
- Changes confined to `AGENTS.md` and `.agent/` need link/path checks; they are not
  part of the published site and do not require a site build.
