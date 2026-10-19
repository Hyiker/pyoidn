# Python Rules

Apply these rules to Python implementation, test, and development commands.

## Environment

- Check whether conda is available and whether it contains `ilm`. Activate `ilm`
  before running Python commands when that environment exists.
- Otherwise prefer the existing repository virtual environment: on Windows use
  `env/Scripts/Activate.ps1` or invoke `env/Scripts/python.exe` directly.
- If neither environment exists, inspect the configured interpreter and its
  dependencies before running commands. Do not assume the reference project's
  environment is required to build PyOIDN.
- Run commands from the repository root unless a check explicitly needs another
  working directory. Use `python -m pip` with the selected interpreter.
- Install only dependencies needed for the task. Keep PyTorch optional and avoid
  environment recreation or unrelated upgrades.

## Compatibility and Types

- Follow `python_requires` in `setup.py`; the current base-package minimum is
  Python 3.7. Optional PyTorch support may have a higher interpreter requirement.
- Add type hints to all new or changed signatures, including return values.
- Prefer `typing.Optional`, `typing.Union`, and `typing` collection types where
  necessary for supported interpreters. Avoid Python 3.10 union syntax and newer
  runtime APIs unless the supported-version policy is intentionally updated.
- Use `from __future__ import annotations` when postponed annotations are needed;
  ensure runtime annotation inspection still works on supported versions.
- Use `TYPE_CHECKING`, forward references, or existing `Any` conventions when a
  type annotation would otherwise make PyTorch mandatory at import time.

## Errors and Helpers

- Reuse `c_str`, `np2c_ptr`, `require_torch`, and `torch2c_ptr` where appropriate.
  Import `torch_utils` only on PyTorch paths, after checking availability.
- Raise descriptive built-in exceptions such as `TypeError`, `ValueError`, and
  `ImportError` for Python-side errors. Do not use assertions for public input
  validation or introduce a logging/error dependency from another repository.
- Avoid `print()` in runtime library code. Use standard logging only when a
  diagnostic is needed; keep native errors available through `Device.get_error()`.
- Catch exceptions only where recovery or useful context is possible. Preserve
  useful native-loader and dependency errors rather than silently continuing.
