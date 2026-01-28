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

    def _get_input_images(self):
        color = utils.read_image("noisy.jpeg")
        normal = utils.read_image("normal.jpeg")
        albedo = utils.read_image("albedo.jpeg")
        return color, normal, albedo

    def _assert_images_similar(self, img1: np.ndarray, img2: np.ndarray, error_mean=0.01):
        self.assertEqual(img1.shape, img2.shape)
        mean_error = np.mean(np.abs(img1 - img2))
        self.assertLessEqual(mean_error, error_mean)

    def test_denoise(self):
        import pyoidn

        with self._make_device() as device:
            filter = pyoidn.Filter(device, "RT")
            try:
                color, normal, albedo = self._get_input_images()

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
                color, normal, albedo = self._get_input_images()

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
                color, normal, albedo = self._get_input_images()
                color = np.ascontiguousarray(color, dtype=np.float32)
                normal = np.ascontiguousarray(normal, dtype=np.float32)
                albedo = np.ascontiguousarray(albedo, dtype=np.float32)
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
                color, normal, albedo = self._get_input_images()
                color = np.ascontiguousarray(
                    color, dtype=np.float32
                )
                normal = np.ascontiguousarray(
                    normal, dtype=np.float32
                )
                albedo = np.ascontiguousarray(
                    albedo, dtype=np.float32
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
    def test_denoise_using_torch_tensors(self):
        try:
            import torch
        except ImportError:
            self.skipTest("torch not installed")

        import pyoidn

        torch_device = torch.device("cpu")

        with pyoidn.Device.from_torch(torch_device) as device:
            device.commit()
            filter = pyoidn.Filter(device, "RT")
            try:
                color, normal, albedo = self._get_input_images()

                color_t = torch.from_numpy(color).to(dtype=torch.float32).contiguous()
                normal_t = torch.from_numpy(normal).to(dtype=torch.float32).contiguous()
                albedo_t = torch.from_numpy(albedo).to(dtype=torch.float32).contiguous()
                out_t = torch.empty_like(color_t)

                filter.set_image(pyoidn.OIDN_IMAGE_COLOR, color_t, pyoidn.OIDN_FORMAT_FLOAT3)
                filter.set_image(pyoidn.OIDN_IMAGE_NORMAL, normal_t, pyoidn.OIDN_FORMAT_FLOAT3)
                filter.set_image(pyoidn.OIDN_IMAGE_ALBEDO, albedo_t, pyoidn.OIDN_FORMAT_FLOAT3)
                filter.set_image(pyoidn.OIDN_IMAGE_OUTPUT, out_t, pyoidn.OIDN_FORMAT_FLOAT3)
                filter.commit()
                filter.execute()

                self.assertIsNone(device.get_error())

                result = out_t.numpy()
                self._assert_images_similar(result, self._get_denoised_reference())
            finally:
                filter.release()

    def test_denoise_cuda_using_torch_tensors(self):
        try:
            import torch
        except ImportError:
            self.skipTest("torch not installed")

        if not torch.cuda.is_available():
            self.skipTest("CUDA not available")

        import pyoidn

        device_id = torch.cuda.current_device()
        if not pyoidn.Device.is_cuda_available(device_id):
            self.skipTest("OIDN CUDA backend not available")
        torch_device = torch.device("cuda", device_id)

        with pyoidn.Device.from_torch(torch_device) as device:
            device.commit()
            self.assertIsNone(device.get_error())

            flt = pyoidn.Filter(device, "RT")
            try:
                color, normal, albedo = self._get_input_images()

                color_t = torch.from_numpy(color).to(device=torch_device, dtype=torch.float32).contiguous()
                normal_t = torch.from_numpy(normal).to(device=torch_device, dtype=torch.float32).contiguous()
                albedo_t = torch.from_numpy(albedo).to(device=torch_device, dtype=torch.float32).contiguous()
                out_t = torch.empty_like(color_t)

                flt.set_image(pyoidn.OIDN_IMAGE_COLOR, color_t, pyoidn.OIDN_FORMAT_FLOAT3)
                flt.set_image(pyoidn.OIDN_IMAGE_NORMAL, normal_t, pyoidn.OIDN_FORMAT_FLOAT3)
                flt.set_image(pyoidn.OIDN_IMAGE_ALBEDO, albedo_t, pyoidn.OIDN_FORMAT_FLOAT3)
                flt.set_image(pyoidn.OIDN_IMAGE_OUTPUT, out_t, pyoidn.OIDN_FORMAT_FLOAT3)
                flt.commit()
                flt.execute()

                self.assertIsNone(device.get_error())

                result = out_t.detach().cpu().numpy()
                self._assert_images_similar(result, self._get_denoised_reference())
            finally:
                flt.release()


if __name__ == "__main__":
    unittest.main()
