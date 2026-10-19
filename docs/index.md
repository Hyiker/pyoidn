# pyoidn

Unofficial Intel [Open Image Denoise (OIDN)](https://www.openimagedenoise.org/) Python binding.

## Quickstart

```python
import numpy as np
import pyoidn

# HxWx3 float32: color/albedo in [0, 1], normal in [-1, 1]
result = pyoidn.denoise(color, albedo=albedo, normal=normal)
```

Only `color` is required. Use `hdr=True` for linear HDR renderings. Inputs must
have shape `(height, width, 3)` and dtype float32 or float16. Noncontiguous inputs
are copied to contiguous storage; inputs are preserved and each result is independent.

With the optional `pyoidn[torch]` extra, the same function accepts CPU or CUDA
tensors and returns a tensor on the input device. The call completes before
returning and does not support autograd.

Devices and filters are reused automatically across calls. NumPy and CPU Torch
inputs share a CPU device; CUDA resources follow the input device and current
Torch stream. Cached resources are released at process exit, and concurrent
calls are serialized. Use the low-level `Device` and `Filter` API when explicit
resource lifetime or asynchronous execution is needed.

See the [denoise reference](api/denoise.md) for quality settings and HDR lightmaps.
