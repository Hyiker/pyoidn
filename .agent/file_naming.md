# File Naming and Placement

Apply these rules when creating, moving, or renaming files.

## Package Modules

- Keep the current flat `pyoidn/` package. Use descriptive `snake_case.py` names,
  following `device.py`, `buffer.py`, `filter.py`, and `torch_utils.py`.
- Put a change in the existing component module when it belongs there. Create a
  new module only for a distinct responsibility with a concrete use.
- Use a leading underscore for a new implementation-only module when appropriate.
  Keep public module names oriented around what users need to import.
- Do not introduce an `_src/` hierarchy or impose category-first prefixes on
  existing modules as a naming cleanup.
- Use `PascalCase` class names, `snake_case` functions/parameters, and existing
  `OIDN_*` names for OIDN constants. Keep native symbol names aligned with the C API.
- A module rename is an API change when users can import it. Update imports,
  exports, tests, and reference pages together when such a change is intentional.

## Tests, Docs, and Generated Assets

- Put tests in `tests/test_<component>.py` and shared test helpers in
  `tests/utils.py`. Do not place tests inside the runtime package.
- Put documentation pages under `docs/`, using descriptive lowercase Markdown
  filenames and updating `mkdocs.yml` navigation when needed.
- Keep API pages under `docs/api/`, matching the documented component names.
- Keep existing README images under `imgs/` and test fixtures under `tests/data/`.
  New documentation-only images may live under `docs/images/`.
- Keep generated binaries in `pyoidn/oidn/`, generated version metadata in
  `pyoidn/version.py`, and build artifacts in the existing ignored output locations.
  Edit their source templates or build configuration instead of generated output.
