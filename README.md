# PyOIDN: Intel Open Image Denoise Python binding

[![GitHub Tag](https://img.shields.io/github/v/tag/Hyiker/pyoidn)](https://github.com/Hyiker/pyoidn/tags) [![Tests](https://img.shields.io/github/actions/workflow/status/Hyiker/pyoidn/testing.yml?branch=master)](https://github.com/Hyiker/pyoidn/actions/workflows/testing.yml) [![Docs](https://img.shields.io/github/actions/workflow/status/Hyiker/pyoidn/docs.yml?branch=master&label=docs)](https://github.com/Hyiker/pyoidn/actions/workflows/docs.yml)

Yet another unofficial Intel [Open Image Denoise (OIDN)](https://www.openimagedenoise.org/) Python binding -- but more Pythonic.

## Features

- Directly use NumPy arrays as input/output images.
- Support all OIDN filter types.
- Simple and clean API design.
- Lightweight: only depends on NumPy and the OIDN shared library.

## Install

```bash
pip install pyoidn
```

## Quickstart

Given a noisy image, plus its normal map and albedo map, denoise and save the result.

![noisy_color](imgs/result_noisy.png)

```python
import numpy as np
from PIL import Image
import pyoidn


def load_image(path: str) -> np.ndarray:
    return np.array(Image.open(path), dtype=np.float32) / 255.0


color = load_image(color_path)
normal = load_image(normal_path)
albedo = load_image(albedo_path)
result = np.zeros_like(color, dtype=np.float32)

device = pyoidn.Device()
device.commit()

flt = pyoidn.Filter(device, "RT")
flt.set_image(pyoidn.OIDN_IMAGE_COLOR, color, pyoidn.OIDN_FORMAT_FLOAT3)
flt.set_image(pyoidn.OIDN_IMAGE_NORMAL, normal, pyoidn.OIDN_FORMAT_FLOAT3)
flt.set_image(pyoidn.OIDN_IMAGE_ALBEDO, albedo, pyoidn.OIDN_FORMAT_FLOAT3)
flt.set_image(pyoidn.OIDN_IMAGE_OUTPUT, result, pyoidn.OIDN_FORMAT_FLOAT3)

flt.commit()
flt.execute()

# Always check errors if something looks off
assert device.get_error() is None

result_u8 = np.array(np.clip(result * 255, 0, 255), dtype=np.uint8)
Image.fromarray(result_u8).save(output_path)

flt.release()
device.release()
```

The result:

![denoised_result](imgs/result_denoised.png)

pyoidn also supports RAII-style resource management using context managers:

```python
with pyoidn.Device() as device:
    device.commit()
    with pyoidn.Filter(device, "RT") as flt:
        flt.set_bool("hdr", True)
        # set images and other parameters
        flt.commit()
        flt.execute()
```

## Notes

- Error handling: use `device.get_error()` after creating/committing/executing.
- Async example: see `tests/test.py`.

## Documentation

Build locally:

```bash
pip install -r requirements-docs.txt
mkdocs serve
```

## Roadmap

- [x] CPU device support
- [x] NumPy array support
- [x] All filter types support
- [x] OIDN buffer support
- [x] RAII-style resource management
- [ ] More device types
  - [ ] CUDA
  - [ ] SYCL
  - [ ] Metal
- [x] Documents
- [ ] Examples

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).

This project includes:

- [Intel Open Image Denoise](https://github.com/RenderKit/oidn) (Apache License 2.0)
