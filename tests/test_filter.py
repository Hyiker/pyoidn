import unittest
import utils
import numpy as np


class PyOidnMiscTest(unittest.TestCase):

    def test_import(self):
        import pyoidn

    def test_version_string(self):
        import pyoidn

        self.assertEqual(pyoidn.version.oidn_version, "2.4.0")

    def test_denoise(self):
        import pyoidn

        device = pyoidn.Device()
        device.commit()

        filter = pyoidn.Filter(device, "RT")

        color = utils.read_image("noisy.jpeg")
        normal = utils.read_image("normal.jpeg")
        albedo = utils.read_image("albedo.jpeg")

        result = np.zeros_like(color, dtype=np.float32)

        filter.set_image(pyoidn.OIDN_IMAGE_COLOR, color, pyoidn.OIDN_FORMAT_FLOAT3)
        filter.set_image(pyoidn.OIDN_IMAGE_NORMAL, normal, pyoidn.OIDN_FORMAT_FLOAT3)
        filter.set_image(pyoidn.OIDN_IMAGE_ALBEDO, albedo, pyoidn.OIDN_FORMAT_FLOAT3)
        filter.set_image(pyoidn.OIDN_IMAGE_OUTPUT, result, pyoidn.OIDN_FORMAT_FLOAT3)
        filter.commit()
        filter.execute()

        self.assertIsNone(device.get_error())
        # Check not all zeros in result
        self.assertTrue(np.any(result != 0))

        filter.release()
        device.release()

    def test_denoise_async(self):
        import pyoidn

        device = pyoidn.Device()
        device.commit()

        filter = pyoidn.Filter(device, "RT")

        color = utils.read_image("noisy.jpeg")
        normal = utils.read_image("normal.jpeg")
        albedo = utils.read_image("albedo.jpeg")

        result = np.zeros_like(color, dtype=np.float32)

        filter.set_image(pyoidn.OIDN_IMAGE_COLOR, color, pyoidn.OIDN_FORMAT_FLOAT3)
        filter.set_image(pyoidn.OIDN_IMAGE_NORMAL, normal, pyoidn.OIDN_FORMAT_FLOAT3)
        filter.set_image(pyoidn.OIDN_IMAGE_ALBEDO, albedo, pyoidn.OIDN_FORMAT_FLOAT3)
        filter.set_image(pyoidn.OIDN_IMAGE_OUTPUT, result, pyoidn.OIDN_FORMAT_FLOAT3)
        filter.commit()
        filter.execute_async()

        self.assertIsNone(device.get_error())

        device.wait()

        # Check not all zeros in result
        self.assertTrue(np.any(result != 0))

        filter.release()
        device.release()


if __name__ == "__main__":
    unittest.main()
