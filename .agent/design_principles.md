# Design Principles

Apply these rules before non-trivial implementation changes.

## Keep the Binding Thin

- Mirror OIDN concepts through `Device`, `Buffer`, and `Filter`. Prefer a small
  wrapper over a new framework, backend registry, or configuration layer.
- Put C declarations and library loading in `pyoidn/capi.py`, resource operations
  in their matching modules, and shared conversions in the existing helpers.
- Keep changes focused. Extract helpers when they remove meaningful duplication;
  avoid abstractions for hypothetical future features.
- Preserve public import paths, constants, defaults, and return values unless the
  task deliberately changes their contract.
- Treat existing behavior as something to inspect, not proof of correctness.
  Fix relevant defects with focused regression coverage rather than copying them.

## Make Contracts Explicit

- Distinguish Python validation errors from native errors retrieved through
  `Device.get_error()`. Preserve that API's `None`-or-message contract.
- Specify memory ownership, valid layouts, byte offsets, and synchronization
  requirements whenever an API passes a pointer to OIDN.
- Keep NumPy and CFFI as base dependencies; keep PyTorch optional.
- Preserve importability without OIDN binaries by keeping native loading lazy.
  Actual native operations should report loading failures clearly.
- Use `.agent/native_bindings.md` for resource and asynchronous behavior.

## Respect Platform and Performance Boundaries

- Account for the Windows, Linux, and macOS targets in the existing CI matrix.
  Do not assume that an advertised OIDN enum implies a working Python backend.
- Preserve shared-memory paths. Make copies or device transfers explicit when
  required by a feature's contract.
- Avoid extra waits in asynchronous paths; synchronize at the point where results
  or resource cleanup require completion.
- Validate behavioral changes with focused tests before widening the check scope.
  Do not add tests for prose-only changes or mechanically restate the implementation.
