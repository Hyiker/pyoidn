# Intel Open Image Denoise python binding

<img alt="GitHub Tag" src="https://img.shields.io/github/v/tag/Hyiker/pyoidn">
<img alt="GitHub Actions Workflow Status" src="https://img.shields.io/github/actions/workflow/status/Hyiker/pyoidn/build_publish.yml">


Unofficial Intel [OIDN](https://www.openimagedenoise.org/) python binding. I pick some of my mostly used functionalities of OIDN, feature request with issues/PRs are welcomed.

Current implementation only supports numpy as input/output buffer. PyTorch version will be developed soon.

## Install and Usage

Install pyoidn with:

```bash
pip install pyoidn
```

A simple for ray traced image denoising:

```python
def load_image(path: str) -> np.ndarray:
    return np.array(Image.open(path), dtype=np.float32) / 255.0

color = load_image(color_path)
normal = load_image(normal_path)
albedo = load_image(albedo_path)
result = np.zeros_like(color, dtype=np.float32)

device = pyoidn.Device()
device.commit()

filter = pyoidn.Filter(device, "RT")
filter.set_image(pyoidn.OIDN_IMAGE_COLOR, color, pyoidn.OIDN_FORMAT_FLOAT3)
filter.set_image(pyoidn.OIDN_IMAGE_NORMAL, normal, pyoidn.OIDN_FORMAT_FLOAT3)
filter.set_image(pyoidn.OIDN_IMAGE_ALBEDO, albedo, pyoidn.OIDN_FORMAT_FLOAT3)
filter.set_image(pyoidn.OIDN_IMAGE_OUTPUT, result, pyoidn.OIDN_FORMAT_FLOAT3)

filter.commit()
filter.execute()

result = np.array(np.clip(result * 255, 0, 255), dtype=np.uint8)
Image.fromarray(result).save(output_path)

filter.release()

device.release()
```

Async version example can be found in `tests/test.py`

Please use `device.get_error` for error check.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

This project includes:
- [Intel Open Image Denoise](https://github.com/RenderKit/oidn) - Licensed under Apache License 2.0
