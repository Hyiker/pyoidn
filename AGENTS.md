# Agent Instructions

This file is the entry point for coding agents working in this repository. Keep
changes small, inspect the existing code before editing, and follow the
repository-specific rules in `.agent/`.

## Project Layout

PyOIDN is a thin CFFI binding for Intel Open Image Denoise, with NumPy support and
optional PyTorch integration. Keep the existing flat package structure.

| Path | Responsibility |
| --- | --- |
| `pyoidn/__init__.py` | Curated public imports and `__all__` |
| `pyoidn/device.py` | OIDN device creation, properties, errors, and synchronization |
| `pyoidn/buffer.py` | Native buffers, shared memory, and host transfers |
| `pyoidn/filter.py` | Filter configuration, image binding, and execution |
| `pyoidn/capi.py` | CFFI declarations and lazy native-library loading |
| `pyoidn/utils.py`, `pyoidn/torch_utils.py` | Pointer conversion and dependency helpers |
| `tests/` | `unittest` tests, shared helpers, and image fixtures |
| `docs/`, `mkdocs.yml` | Markdown documentation and MkDocs configuration |
| `setup.py`, `MANIFEST.in` | Package metadata and native-library inclusion |
| `.github/workflows/` | Cross-platform builds, tests, documentation, and releases |

## Rule Files

- Read [design principles](.agent/design_principles.md) before non-trivial changes.
- Use [Python rules](.agent/python_rules.md) and
  [package conventions](.agent/package_format_rules.md) for Python and packaging changes.
- Use [native binding rules](.agent/native_bindings.md) for CFFI, resource ownership,
  image memory, transfers, and asynchronous execution.
- Read [test rules](.agent/tests.md) before adding, changing, or running tests.
- Use [documentation guidance](.agent/documenter.md) and
  [MkDocs rules](.agent/mkdocs_md.md) for documentation and docstring changes.
- Use [file naming rules](.agent/file_naming.md) when creating or moving files.

## Development Workflow

- Prefer `rg`/`rg --files` for repository search.
- Preserve user changes in the working tree. Do not revert unrelated files.
- Activate the `ilm` conda environment before running Python commands when it exists;
  otherwise follow the environment selection in `.agent/python_rules.md`.
- Inspect source, tests, and the relevant CI scripts before changing behavior.
- Keep public APIs minimal and user-focused. Do not expose implementation details
  unless they are required by the user-facing contract.
- Prefer existing local patterns and helpers over new abstractions.
- Use only `Copyright (c) 2026` in SPDX copyright headers for new files;
  preserve existing headers when modifying older files.
- Add focused tests for behavioral changes. Use `float32` for image fixtures and
  `float16` when testing half formats. Do not use `float64` in tests.
- Run checks appropriate to the change and state any unavailable prerequisites.
- Treat `pyoidn/oidn/` and `pyoidn/version.py` as generated inputs. Do not hand-edit
  them or commit build output, downloaded binaries, or local environments.

## Python Conventions

- Add type hints to new or changed function signatures, keeping compatibility with
  the Python minimum declared in `setup.py` (currently 3.7).
- Use concise docstrings describing behavior, inputs, outputs, image shapes,
  dtypes, byte units, and ownership where relevant.
- For dataclasses, document fields where they are declared.
- Use standard Python exceptions for argument errors and optional dependencies;
  preserve `Device.get_error()` for native OIDN errors.
- Keep NumPy-only use working without PyTorch and preserve lazy native loading.
- Curate public imports in `pyoidn/__init__.py`; internal imports should target
  concrete modules.

## Native Resources

- Preserve explicit `commit()`, `wait()`, and `release()` semantics.
- Keep shared allocations alive until native use finishes. Synchronize asynchronous
  work before reading its results or releasing resources.
- Preserve zero-copy and stream behavior; avoid implicit copies, host transfers,
  or extra synchronization in performance-sensitive paths.

## Visualization

- Keep image comparisons intuitive and simple, with clear labels and few metrics.
- Keep test fixtures stable; write diagnostic output to temporary locations.

## Documentation

- Use Markdown with the existing MkDocs Material and mkdocstrings configuration.
- Use Sphinx-style field lists in Python docstrings, as configured in `mkdocs.yml`.
- Keep docs in the correct Diataxis category: tutorial, guide, concept, or
  reference, without reorganizing unrelated pages.
- Write user-facing docs around the outcome and contract, not internal
  implementation details.
