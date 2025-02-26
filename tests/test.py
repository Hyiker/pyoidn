import unittest
import sys
import os
import numpy as np
from PIL import Image
from pathlib import Path

# here = Path(__file__).parent.absolute()
# sys.path.append(here.parent.absolute().as_posix())

TEST_DIR = os.path.abspath(os.path.dirname(__file__))


def open_data_image(name: str):
    return (
        np.array(
            Image.open(
                os.path.join(TEST_DIR, "data", name),
            ),
            dtype=np.float32,
        )
        / 255.0
    )


class PyOidnTest(unittest.TestCase):
    def test_import(self):
        import pyoidn

    def test_new_device(self):
        import pyoidn

        device = pyoidn.Device()
        device.commit()
        device.release()

    def test_new_filter(self):
        import pyoidn

        device = pyoidn.Device()
        device.commit()

        filter = pyoidn.Filter(device, "RT")

        filter.release()
        device.release()

    def test_denoise(self):
        import pyoidn

        device = pyoidn.Device()
        device.commit()

        filter = pyoidn.Filter(device, "RT")

        color = open_data_image("noisy.jpeg")
        normal = open_data_image("normal.jpeg")
        albedo = open_data_image("albedo.jpeg")

        result = np.zeros_like(color, dtype=np.float32)

        filter.set_image(pyoidn.OIDN_IMAGE_COLOR, color, pyoidn.OIDN_FORMAT_FLOAT3)
        filter.set_image(pyoidn.OIDN_IMAGE_NORMAL, normal, pyoidn.OIDN_FORMAT_FLOAT3)
        filter.set_image(pyoidn.OIDN_IMAGE_ALBEDO, albedo, pyoidn.OIDN_FORMAT_FLOAT3)
        filter.set_image(pyoidn.OIDN_IMAGE_OUTPUT, result, pyoidn.OIDN_FORMAT_FLOAT3)
        filter.commit()
        filter.execute()

        result = np.array(np.clip(result * 255, 0, 255), dtype=np.uint8)
        res_img = Image.fromarray(result)
        res_img.save(os.path.join(TEST_DIR, "data", "denoised_example.png"))

        filter.release()
        device.release()

    def test_denoise_async(self):
        import pyoidn

        device = pyoidn.Device()
        device.commit()

        filter = pyoidn.Filter(device, "RT")

        color = open_data_image("noisy.jpeg")
        normal = open_data_image("normal.jpeg")
        albedo = open_data_image("albedo.jpeg")

        result = np.zeros_like(color, dtype=np.float32)

        filter.set_image(pyoidn.OIDN_IMAGE_COLOR, color, pyoidn.OIDN_FORMAT_FLOAT3)
        filter.set_image(pyoidn.OIDN_IMAGE_NORMAL, normal, pyoidn.OIDN_FORMAT_FLOAT3)
        filter.set_image(pyoidn.OIDN_IMAGE_ALBEDO, albedo, pyoidn.OIDN_FORMAT_FLOAT3)
        filter.set_image(pyoidn.OIDN_IMAGE_OUTPUT, result, pyoidn.OIDN_FORMAT_FLOAT3)
        filter.commit()
        filter.execute_async()

        device.wait()

        result = np.array(np.clip(result * 255, 0, 255), dtype=np.uint8)
        res_img = Image.fromarray(result)
        res_img.save(os.path.join(TEST_DIR, "data", "denoised_example_async.png"))

        filter.release()
        device.release()


if __name__ == "__main__":
    unittest.main()
