# Native Binding Rules

Apply these rules to CFFI declarations, native loading, pointers, and resources.

## CFFI and Loading

- Keep `OIDN_*` declarations, enum values, pointer types, integer signedness, and
  byte-size arguments consistent with the OIDN version selected by the project.
  Check that version's headers when changing the ABI; do not guess declarations.
- Keep `oidn_ffi` and its declarations available at import time, and preserve lazy
  loading through `oidn_Capi`. Do not load OIDN merely to inspect documentation.
- Preserve platform-specific names and locations: `bin` on Windows and `lib` on
  Unix platforms, with `.dll`, `.so`, or `.dylib` as appropriate.
- Account for Windows device-library load order. Avoid hard-coded local paths or
  process-wide library-path changes as a shortcut.

## Resource Lifecycle

- Preserve explicit device/filter commits. Do not add automatic commits or waits
  that change existing behavior without a deliberate API change.
- Keep the owning device alive while its filters and buffers are in use. Release
  dependent resources before the device, including on exception paths.
- Prefer context managers in examples and tests, or `try/finally` for explicit
  cleanup. Cleanup must not suppress an exception from the caller's block.
- Avoid double release. Preserve the documented idempotence of `Buffer.release()`;
  do not assume every other wrapper currently has that guarantee.
- Keep native errors observable through `Device.get_error()`, including after
  synchronization for asynchronous operations.

## Shared Images and Memory

- Distinguish an OIDN-owned buffer from an external allocation wrapped by a shared
  buffer or image. Releasing a wrapper must not free memory owned by NumPy or Torch.
- Keep the backing allocation alive while OIDN can access it. Document caller
  lifetime responsibilities for APIs that do not retain the owner; retain a strong
  reference when implementing a contract that promises managed ownership.
- Match image shape `(height, width, channels)`, dtype, channel count, and device
  to the selected OIDN format and backend. Use float32 for `FLOAT*` and float16
  for `HALF*`; do not reinterpret an incompatible allocation as a matching image.
- Treat offsets and pixel/row strides as bytes. Check contiguous-layout
  requirements, writable destinations, and accessible byte ranges on affected paths.
- Do not silently copy shared inputs to hide layout problems. Make any required
  conversion explicit, particularly when it would detach the caller's output.
- Host buffer read/write methods use host memory; do not dereference CUDA device
  pointers as host buffers.

## Asynchronous Work and Torch

- Keep async calls nonblocking. Call `Device.wait()` before consuming results or
  releasing allocations used by pending operations.
- Keep async transfer source/destination storage valid until completion, including
  any temporary buffer views needed to preserve its address.
- Preserve the device and CUDA stream selected by `Device.from_torch()`. Test
  stream-sensitive changes without introducing global synchronization in runtime code.
- Do not advertise CUDA graph capture or additional backend support without
  validating that behavior; CUDA availability alone does not establish support.
