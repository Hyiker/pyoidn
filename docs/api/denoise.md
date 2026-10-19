# Denoise

```python
import pyoidn

result = pyoidn.denoise(color)
result = pyoidn.denoise(color, albedo=albedo, normal=normal, hdr=True)
lightmap = pyoidn.denoise(color, filter_type="RTLightmap")
```

The convenience interface manages commits and reuses native devices and filters.
Each call returns a new output, so later calls do not overwrite earlier results.
The most recent image allocations remain referenced while bound to a cached filter.
OIDN failures within this interface raise `RuntimeError`; the low-level API keeps
its existing manual error-handling behavior.

Auxiliary images must use the same container type, shape, and device as `color`.
Use linear RGB color, albedos in [0, 1], and world- or view-space normals in [-1, 1].
Set `clean_aux=True` only when auxiliary images are already noise-free; this option
does not denoise them separately. RTLightmap always processes HDR lightmaps and
does not accept auxiliary images.

::: pyoidn.denoise
