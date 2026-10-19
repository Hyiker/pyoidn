# Test Rules

Apply these rules before adding, changing, or running tests.

## Structure and Coverage

- Use `unittest.TestCase` in `tests/test_<component>.py`, following the existing
  device, buffer, filter, and import/version tests. Do not add a new test framework
  for an isolated case.
- Add focused regression coverage for behavior changes. Verify observable output,
  errors, ownership, or synchronization rather than mirroring private implementation.
- Use `tests/utils.py` for existing image fixtures. Keep source fixtures under
  `tests/data/` stable; write new diagnostic output to temporary directories.
- Use float32 for floating-point images and float16 for half-format coverage.
  Byte-level transfer tests may use integer buffers. Never use float64 in tests.
- Use deterministic inputs and explicit image tolerances. Do not replace a
  reference image or relax a tolerance merely to make a failing test pass.
- For touched native paths, cover relevant input types, byte ranges, layouts,
  cleanup, and sync/async results. Do not build an unrelated exhaustive test matrix.
- Check `device.get_error()` at meaningful lifecycle points. Wait for pending work
  before asserting results or cleaning up resources.

## Optional Dependencies and Native Prerequisites

- Keep base tests runnable without PyTorch. Skip Torch/CUDA cases with a clear
  reason when Torch, CUDA, or the OIDN CUDA backend is unavailable, following the
  existing availability checks.
- Base native integration tests need OIDN binaries for the host platform. If they
  are missing, report that prerequisite instead of skipping the base suite or
  claiming a successful run.
- Use `unittest.mock` for focused Python validation or C API dispatch tests when
  appropriate; keep real native integration coverage for memory/denoising behavior.
  Patch the name used by the module under test.
- Do not hide a real correctness failure with a skip or broad exception handler.

## Running Checks

Select the environment using `.agent/python_rules.md`. Install test dependencies
from `requirements-test.txt` when needed. From the repository root:

```powershell
# Focused buffer tests; change the pattern for another component.
python -m unittest discover -s tests -p 'test_buffer.py' -v

# Full suite, matching the CI runner.
python -m unittest discover -s tests -v
```

- A source checkout needs generated `pyoidn/version.py` for package imports and
  downloaded `pyoidn/oidn/` libraries for native operations. Inspect the existing
  build scripts and set `VERSION`/`OIDN_VERSION` for intentional package builds.
- Confirm which copy of `pyoidn` is being exercised when checking an installed
  wheel versus a source checkout; an installation alone does not populate source
  build inputs.
- For dependency-related changes, check the NumPy-only path and the Torch path
  separately when those environments are available. CI does both, but its Torch
  stage does not establish CUDA coverage.
- Run focused checks first, then broaden as required by the change. Report failed
  checks, skipped optional coverage, and platform limits accurately.
- Rules-only edits need link/path and diff checks, not native test execution.
