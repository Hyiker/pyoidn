# Documentation Guidance

Apply these rules to README text, documentation pages, examples, and docstrings.

- Start with the user's outcome and the smallest working example. Explain OIDN
  concepts only to the depth needed to use the API correctly.
- Keep tutorials, task guides, concept explanations, and API reference distinct.
  Use the existing navigation and add structure only when enough content needs it.
- Write concise English documentation to match the repository, unless the task
  explicitly requests another language. Use clear terms and prose near 99 columns.
- Verify signatures and examples against the implementation and tests. Resolve
  conflicting examples from the actual API instead of copying them uncritically.
- Prefer public imports such as `import pyoidn`. Use `pyoidn.capi` only for an
  explicitly developer-facing explanation of the binding.
- Show required device/filter commits, error checks, and resource cleanup. For
  async examples, show `device.wait()` before consuming results or releasing memory.
- State image shape, dtype, contiguity, device, and shared-memory lifetime when
  relevant. Distinguish byte counts and strides from pixel dimensions.
- Explain base installation separately from the optional `pyoidn[torch]` extra.
  CUDA examples should use `Device.from_torch()` and check actual backend support.
- Describe implemented and validated backend behavior. Constants in the public API
  are not proof of complete SYCL, HIP, or Metal integration.
- Keep API facts in docstrings and task explanations in Markdown. Update affected
  reference pages and examples when a user-facing contract changes.
- Use a few well-labeled images for denoising comparisons; avoid long metric dumps.
- Follow `.agent/mkdocs_md.md` for syntax, navigation, and documentation validation.
