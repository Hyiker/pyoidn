import unittest
import utils
import numpy as np
from PIL import Image


class PyOidnFilterTest(unittest.TestCase):
    def _make_device(self):
        import pyoidn

        device = pyoidn.Device(pyoidn.OIDN_DEVICE_TYPE_CPU)
        device.commit()
        self.assertIsNone(device.get_error())
        return device

    def _write_image(self, filename: str, image: np.ndarray):
        import pyoidn

        image_8bit = np.clip(image * 255.0, 0, 255).astype(np.uint8)
        img = Image.fromarray(image_8bit, "RGB")
        img.save(filename)

    def _get_denoised_reference(self):
        return utils.read_image("denoised_example.png")

    def _assert_images_similar(self, img1: np.ndarray, img2: np.ndarray, error_mean=0.01):
        self.assertEqual(img1.shape, img2.shape)
        mean_error = np.mean(np.abs(img1 - img2))
        self.assertLessEqual(mean_error, error_mean)

    def test_denoise(self):
        import pyoidn

        with self._make_device() as device:
            filter = pyoidn.Filter(device, "RT")
            try:
                color = utils.read_image("noisy.jpeg")
                normal = utils.read_image("normal.jpeg")
                albedo = utils.read_image("albedo.jpeg")

                result = np.zeros_like(color, dtype=np.float32)

                filter.set_image(
                    pyoidn.OIDN_IMAGE_COLOR, color, pyoidn.OIDN_FORMAT_FLOAT3
                )
                filter.set_image(
                    pyoidn.OIDN_IMAGE_NORMAL, normal, pyoidn.OIDN_FORMAT_FLOAT3
                )
                filter.set_image(
                    pyoidn.OIDN_IMAGE_ALBEDO, albedo, pyoidn.OIDN_FORMAT_FLOAT3
                )
                filter.set_image(
                    pyoidn.OIDN_IMAGE_OUTPUT, result, pyoidn.OIDN_FORMAT_FLOAT3
                )
                filter.commit()
                filter.execute()

                self.assertIsNone(device.get_error())
                self._assert_images_similar(result, self._get_denoised_reference())
            finally:
                filter.release()

    def test_denoise_async(self):
        import pyoidn

        with self._make_device() as device:
            filter = pyoidn.Filter(device, "RT")
            try:
                color = utils.read_image("noisy.jpeg")
                normal = utils.read_image("normal.jpeg")
                albedo = utils.read_image("albedo.jpeg")

                result = np.zeros_like(color, dtype=np.float32)

                filter.set_image(
                    pyoidn.OIDN_IMAGE_COLOR, color, pyoidn.OIDN_FORMAT_FLOAT3
                )
                filter.set_image(
                    pyoidn.OIDN_IMAGE_NORMAL, normal, pyoidn.OIDN_FORMAT_FLOAT3
                )
                filter.set_image(
                    pyoidn.OIDN_IMAGE_ALBEDO, albedo, pyoidn.OIDN_FORMAT_FLOAT3
                )
                filter.set_image(
                    pyoidn.OIDN_IMAGE_OUTPUT, result, pyoidn.OIDN_FORMAT_FLOAT3
                )
                filter.commit()
                filter.execute_async()

                self.assertIsNone(device.get_error())

                device.wait()

                self._assert_images_similar(result, self._get_denoised_reference())
            finally:
                filter.release()

    def test_denoise_using_buffer(self):
        import pyoidn

        with self._make_device() as device:
            filter = pyoidn.Filter(device, "RT")
            try:
                color = np.ascontiguousarray(
                    utils.read_image("noisy.jpeg"), dtype=np.float32
                )
                normal = np.ascontiguousarray(
                    utils.read_image("normal.jpeg"), dtype=np.float32
                )
                albedo = np.ascontiguousarray(
                    utils.read_image("albedo.jpeg"), dtype=np.float32
                )

                height, width = int(color.shape[0]), int(color.shape[1])
                self.assertEqual(color.shape, (height, width, 3))
                self.assertEqual(normal.shape, (height, width, 3))
                self.assertEqual(albedo.shape, (height, width, 3))

                pixel_stride = 3 * 4
                row_stride = width * pixel_stride

                color_buf = pyoidn.Buffer(
                    device, color.nbytes, storage=pyoidn.OIDN_STORAGE_HOST
                )
                normal_buf = pyoidn.Buffer(
                    device, normal.nbytes, storage=pyoidn.OIDN_STORAGE_HOST
                )
                albedo_buf = pyoidn.Buffer(
                    device, albedo.nbytes, storage=pyoidn.OIDN_STORAGE_HOST
                )
                out_buf = pyoidn.Buffer(
                    device, color.nbytes, storage=pyoidn.OIDN_STORAGE_HOST
                )

                try:
                    color_buf.write(0, color.nbytes, color)
                    normal_buf.write(0, normal.nbytes, normal)
                    albedo_buf.write(0, albedo.nbytes, albedo)

                    filter.set_image(
                        pyoidn.OIDN_IMAGE_COLOR,
                        color_buf,
                        pyoidn.OIDN_FORMAT_FLOAT3,
                        width=width,
                        height=height,
                        pixel_byte_stride=pixel_stride,
                        row_byte_stride=row_stride,
                    )
                    filter.set_image(
                        pyoidn.OIDN_IMAGE_NORMAL,
                        normal_buf,
                        pyoidn.OIDN_FORMAT_FLOAT3,
                        width=width,
                        height=height,
                        pixel_byte_stride=pixel_stride,
                        row_byte_stride=row_stride,
                    )
                    filter.set_image(
                        pyoidn.OIDN_IMAGE_ALBEDO,
                        albedo_buf,
                        pyoidn.OIDN_FORMAT_FLOAT3,
                        width=width,
                        height=height,
                        pixel_byte_stride=pixel_stride,
                        row_byte_stride=row_stride,
                    )
                    filter.set_image(
                        pyoidn.OIDN_IMAGE_OUTPUT,
                        out_buf,
                        pyoidn.OIDN_FORMAT_FLOAT3,
                        width=width,
                        height=height,
                        pixel_byte_stride=pixel_stride,
                        row_byte_stride=row_stride,
                    )

                    filter.commit()
                    filter.execute()

                    self.assertIsNone(device.get_error())

                    result = np.zeros_like(color, dtype=np.float32)
                    out_buf.read(0, result.nbytes, result)
                    self._assert_images_similar(result, self._get_denoised_reference())
                finally:
                    color_buf.release()
                    normal_buf.release()
                    albedo_buf.release()
                    out_buf.release()
            finally:
                filter.release()

    def test_denoise_async_using_buffer(self):
        import pyoidn

        with self._make_device() as device:
            filter = pyoidn.Filter(device, "RT")
            try:
                color = np.ascontiguousarray(
                    utils.read_image("noisy.jpeg"), dtype=np.float32
                )
                normal = np.ascontiguousarray(
                    utils.read_image("normal.jpeg"), dtype=np.float32
                )
                albedo = np.ascontiguousarray(
                    utils.read_image("albedo.jpeg"), dtype=np.float32
                )

                height, width = int(color.shape[0]), int(color.shape[1])
                pixel_stride = 3 * 4
                row_stride = width * pixel_stride

                color_buf = pyoidn.Buffer(
                    device, color.nbytes, storage=pyoidn.OIDN_STORAGE_HOST
                )
                normal_buf = pyoidn.Buffer(
                    device, normal.nbytes, storage=pyoidn.OIDN_STORAGE_HOST
                )
                albedo_buf = pyoidn.Buffer(
                    device, albedo.nbytes, storage=pyoidn.OIDN_STORAGE_HOST
                )
                out_buf = pyoidn.Buffer(
                    device, color.nbytes, storage=pyoidn.OIDN_STORAGE_HOST
                )

                try:
                    color_buf.write(0, color.nbytes, color)
                    normal_buf.write(0, normal.nbytes, normal)
                    albedo_buf.write(0, albedo.nbytes, albedo)

                    filter.set_image(
                        pyoidn.OIDN_IMAGE_COLOR,
                        color_buf,
                        pyoidn.OIDN_FORMAT_FLOAT3,
                        width=width,
                        height=height,
                        pixel_byte_stride=pixel_stride,
                        row_byte_stride=row_stride,
                    )
                    filter.set_image(
                        pyoidn.OIDN_IMAGE_NORMAL,
                        normal_buf,
                        pyoidn.OIDN_FORMAT_FLOAT3,
                        width=width,
                        height=height,
                        pixel_byte_stride=pixel_stride,
                        row_byte_stride=row_stride,
                    )
                    filter.set_image(
                        pyoidn.OIDN_IMAGE_ALBEDO,
                        albedo_buf,
                        pyoidn.OIDN_FORMAT_FLOAT3,
                        width=width,
                        height=height,
                        pixel_byte_stride=pixel_stride,
                        row_byte_stride=row_stride,
                    )
                    filter.set_image(
                        pyoidn.OIDN_IMAGE_OUTPUT,
                        out_buf,
                        pyoidn.OIDN_FORMAT_FLOAT3,
                        width=width,
                        height=height,
                        pixel_byte_stride=pixel_stride,
                        row_byte_stride=row_stride,
                    )

                    filter.commit()
                    filter.execute_async()
                    self.assertIsNone(device.get_error())

                    device.wait()

                    result = np.zeros_like(color, dtype=np.float32)
                    out_buf.read(0, result.nbytes, result)
                    self._assert_images_similar(result, self._get_denoised_reference())
                finally:
                    color_buf.release()
                    normal_buf.release()
                    albedo_buf.release()
                    out_buf.release()
            finally:
                filter.release()


if __name__ == "__main__":
    unittest.main()
