# Code and Package Conventions

Apply these rules to Python formatting, imports, exports, and packaging changes.

## Formatting and Docstrings

- Follow the surrounding style, using four spaces for new Python blocks. Avoid
  unrelated whitespace changes, especially in the existing tab-indented initializer.
- Use descriptive names, standard import groups, and concise triple-double-quoted
  docstrings with the summary on the opening line.
- Keep prose near 99 columns where practical. Do not add or claim a formatter or
  linter configuration that the repository does not contain.
- Use Sphinx-style fields such as `:param name:`, `:return:`, and `:raises ValueError:`
  for API docstrings, matching `mkdocs.yml`.
- Document shapes, dtypes, byte units, ownership, and async completion where
  relevant. Document dataclass fields at their declarations.

## Imports and Public API

- `pyoidn/__init__.py` deliberately aggregates the public API. Keep its imports
  and `__all__` aligned when adding or removing public symbols.
- Maintain existing module-level `__all__` lists where present. Do not export
  private native handles or helper functions solely for convenience.
- Import concrete sibling modules internally instead of importing through
  `pyoidn` and creating cycles. Preserve the existing flat layout.
- Keep base imports functional without PyTorch or installed native binaries.

## Packaging and Generated Files

- `setup.py` requires `VERSION` for the distribution version and uses
  `OIDN_VERSION` to generate `pyoidn/version.py` from `version.py.tmpl`.
- Keep the package version's first three components consistent with
  `oidn_version.txt`; consult `.github/workflows/scripts/check_version.sh`.
- Edit `version.py.tmpl` for template changes, not generated `version.py`. Change
  `oidn_version.txt` only as part of an intentional OIDN version update.
- Native libraries under `pyoidn/oidn/` are downloaded build inputs. Preserve
  inclusion through both `setup.py` and `MANIFEST.in`, including bundled licenses.
- Follow the build/download scripts and platform tags when changing distribution
  behavior. Check Windows, Linux, Intel macOS, and Apple Silicon implications.
- Keep runtime, test, and documentation dependencies in their existing metadata
  locations; do not introduce mandatory Torch or a packaging migration incidentally.
