# pyoidn

Unofficial Intel [Open Image Denoise (OIDN)](https://www.openimagedenoise.org/) Python binding.

## Quickstart

```python
import numpy as np
import pyoidn

# color/normal/albedo: HxWx3 float32 in [0, 1]
result = np.zeros_like(color, dtype=np.float32)

with pyoidn.Device() as device:
    device.commit()

    with pyoidn.Filter(device, "RT") as flt:
        flt.set_image(pyoidn.OIDN_IMAGE_COLOR,  color,  pyoidn.OIDN_FORMAT_FLOAT3)
        flt.set_image(pyoidn.OIDN_IMAGE_NORMAL, normal, pyoidn.OIDN_FORMAT_FLOAT3)
        flt.set_image(pyoidn.OIDN_IMAGE_ALBEDO, albedo, pyoidn.OIDN_FORMAT_FLOAT3)
        flt.set_image(pyoidn.OIDN_IMAGE_OUTPUT, result, pyoidn.OIDN_FORMAT_FLOAT3)

        flt.commit()
        flt.execute()

    assert device.get_error() is None
```
