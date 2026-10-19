# SPDX-FileCopyrightText: Copyright (c) 2026
# SPDX-License-Identifier: MIT
"""Tests for the convenience denoiser and its reusable native resources."""

import importlib
import unittest
from concurrent.futures import ThreadPoolExecutor
from typing import Any
from unittest import mock

import numpy as np

import pyoidn
import utils

denoise_module = importlib.import_module("pyoidn.denoise")


class PyOidnDenoiseTest(unittest.TestCase):
    def setUp(self) -> None:
        denoise_module._denoiser.close()
        self.addCleanup(denoise_module._denoiser.close)

    def _torch(self) -> Any:
        try:
            import torch
        except ImportError:
            self.skipTest("torch not installed")
        return torch

    def _reference(self, color: Any) -> Any:
        """Run the low-level API on the same backend without auxiliary images."""
        if isinstance(color, np.ndarray):
            output = np.empty_like(color)
            device = pyoidn.Device()
        else:
            output = self._torch().empty_like(color)
            device = pyoidn.Device.from_torch(color.device)
        with device:
            device.commit()
            flt = pyoidn.Filter(device)
            try:
                flt.set_image("color", color, pyoidn.OIDN_FORMAT_FLOAT3)
                flt.set_image("output", output, pyoidn.OIDN_FORMAT_FLOAT3)
                flt.commit()
                flt.execute()
                self.assertIsNone(device.get_error())
            finally:
                flt.release()
        return output

    def test_numpy_denoise_matches_image_reference(self) -> None:
        color = utils.read_image("noisy.jpeg")
        original = color.copy()
        result = pyoidn.denoise(
            color,
            albedo=utils.read_image("albedo.jpeg"),
            normal=utils.read_image("normal.jpeg"),
        )
        reference = utils.read_image("denoised_example.png")
        self.assertLessEqual(float(np.mean(np.abs(result - reference))), 0.01)
        self.assertEqual(result.dtype, color.dtype)
        self.assertTrue(result.flags.c_contiguous)
        self.assertFalse(np.shares_memory(result, color))
        np.testing.assert_array_equal(color, original)

    def test_resources_are_reused_and_results_remain_independent(self) -> None:
        color = np.full((32, 32, 3), 0.25, dtype=np.float32)
        with mock.patch.object(denoise_module, "Device", wraps=pyoidn.Device) as device:
            with mock.patch.object(denoise_module, "Filter", wraps=pyoidn.Filter) as flt:
                first = pyoidn.denoise(color)
                snapshot = first.copy()
                second = pyoidn.denoise(color + np.float32(0.5), hdr=True)
                restored = pyoidn.denoise(color)
                self.assertEqual(device.call_count, 1)
                self.assertEqual(flt.call_count, 1)
        np.testing.assert_array_equal(first, snapshot)
        np.testing.assert_array_equal(restored, snapshot)
        self.assertFalse(np.shares_memory(first, second))
        self.assertGreater(float(np.mean(second - first)), 0.1)

    def test_removed_auxiliary_images_do_not_leak_into_next_call(self) -> None:
        color = utils.read_image("noisy.jpeg")
        pyoidn.denoise(color, utils.read_image("albedo.jpeg"), utils.read_image("normal.jpeg"))
        result = pyoidn.denoise(color)
        np.testing.assert_allclose(result, self._reference(color), rtol=1e-5, atol=1e-5)

    def test_concurrent_calls_return_the_correct_independent_results(self) -> None:
        inputs = [np.full((24, 32, 3), value, dtype=np.float32) for value in (0.2, 0.8)]
        with ThreadPoolExecutor(max_workers=2) as pool:
            outputs = list(pool.map(pyoidn.denoise, inputs))
        for color, output in zip(inputs, outputs):
            np.testing.assert_allclose(output, self._reference(color), rtol=1e-5, atol=1e-5)

    def test_noncontiguous_input_and_changed_resolution(self) -> None:
        color = utils.read_image("noisy.jpeg")[::2, ::-2]
        self.assertFalse(color.flags.c_contiguous)
        result = pyoidn.denoise(color)
        reference = self._reference(np.ascontiguousarray(color))
        np.testing.assert_allclose(result, reference, rtol=1e-5, atol=1e-5)
        smaller = np.full((16, 24, 3), 0.5, dtype=np.float32)
        resized = pyoidn.denoise(smaller)
        self.assertEqual(resized.shape, smaller.shape)
        self.assertTrue(np.isfinite(resized).all())

    def test_half_input_and_lightmap_use_separate_filter_configurations(self) -> None:
        color = np.full((32, 32, 3), 0.5, dtype=np.float16)
        with mock.patch.object(denoise_module, "Filter", wraps=pyoidn.Filter) as flt:
            result = pyoidn.denoise(color, quality=pyoidn.OIDN_QUALITY_HIGH)
            lightmap = pyoidn.denoise(color, filter_type="RTLightmap")
            again = pyoidn.denoise(color)
            self.assertEqual(flt.call_count, 2)
        self.assertEqual(result.dtype, np.float16)
        self.assertEqual(lightmap.dtype, np.float16)
        self.assertTrue(np.isfinite(lightmap).all())
        np.testing.assert_array_equal(result, again)

    def test_invalid_inputs_fail_before_native_resource_creation(self) -> None:
        color = np.zeros((16, 16, 3), dtype=np.float32)
        cases = [
            (TypeError, {"color": [0.0]}),
            (TypeError, {"color": color.astype(np.uint8)}),
            (ValueError, {"color": color[:, :, 0]}),
            (ValueError, {"color": np.zeros((0, 16, 3), dtype=np.float32)}),
            (ValueError, {"color": color, "albedo": color[:8]}),
            (TypeError, {"color": color, "albedo": [0.0]}),
            (ValueError, {"color": color, "quality": "unknown"}),
            (ValueError, {"color": color, "quality": 123}),
            (TypeError, {"color": color, "quality": True}),
            (TypeError, {"color": color, "hdr": "yes"}),
            (ValueError, {"color": color, "filter_type": "unknown"}),
            (ValueError, {"color": color, "filter_type": "RTLightmap", "albedo": color}),
        ]
        with mock.patch.object(denoise_module, "Device") as device:
            for exception, kwargs in cases:
                with self.subTest(kwargs=tuple(kwargs), exception=exception):
                    with self.assertRaises(exception):
                        pyoidn.denoise(**kwargs)
            device.assert_not_called()

    def test_failed_filter_is_replaced_and_exception_propagates(self) -> None:
        color = np.full((16, 16, 3), 0.5, dtype=np.float32)
        with mock.patch.object(denoise_module, "Filter", wraps=pyoidn.Filter) as flt:
            with mock.patch.object(pyoidn.Filter, "execute", side_effect=RuntimeError("failed")):
                with self.assertRaisesRegex(RuntimeError, "failed"):
                    pyoidn.denoise(color)
            result = pyoidn.denoise(color)
            self.assertEqual(flt.call_count, 2)
        self.assertTrue(np.isfinite(result).all())

    def test_native_error_without_message_is_reported(self) -> None:
        color = np.zeros((16, 16, 3), dtype=np.float32)
        with mock.patch.object(denoise_module.oidn_Capi, "oidnGetDeviceError", return_value=4):
            with self.assertRaisesRegex(RuntimeError, "error 4.*no error message"):
                pyoidn.denoise(color)

    def test_torch_cpu_shares_resources_and_preserves_tensor_properties(self) -> None:
        torch = self._torch()
        color = np.full((16, 24, 3), 0.5, dtype=np.float32)
        tensor = torch.from_numpy(color).transpose(0, 1).requires_grad_(True)
        with mock.patch.object(denoise_module, "Device", wraps=pyoidn.Device) as device:
            pyoidn.denoise(color)
            result = pyoidn.denoise(tensor)
            self.assertEqual(device.call_count, 1)
        self.assertEqual(result.shape, tensor.shape)
        self.assertEqual(result.device, tensor.device)
        self.assertEqual(result.dtype, tensor.dtype)
        self.assertTrue(result.is_contiguous())
        self.assertFalse(result.requires_grad)
        self.assertIsNone(tensor.grad)
        half = pyoidn.denoise(tensor.detach().to(dtype=torch.float16))
        self.assertEqual(half.dtype, torch.float16)
        self.assertTrue(torch.isfinite(half).all())

    def test_torch_rejects_mixed_inputs_and_unsupported_devices(self) -> None:
        torch = self._torch()
        color = torch.zeros((16, 16, 3), dtype=torch.float32)
        with self.assertRaises(TypeError):
            pyoidn.denoise(color, albedo=color.numpy())
        with self.assertRaises(ValueError):
            pyoidn.denoise(torch.empty((16, 16, 3), device="meta", dtype=torch.float32))

    def test_cuda_resources_follow_the_current_stream(self) -> None:
        torch = self._torch()
        if not torch.cuda.is_available():
            self.skipTest("CUDA not available")
        device_id = torch.cuda.current_device()
        if not pyoidn.Device.is_cuda_available(device_id):
            self.skipTest("OIDN CUDA backend not available")
        color = utils.read_image("noisy.jpeg")
        stream = torch.cuda.Stream(device=device_id)
        with mock.patch.object(
            pyoidn.Device, "from_torch", wraps=pyoidn.Device.from_torch
        ) as create_device:
            with torch.cuda.stream(stream):
                tensor = torch.from_numpy(color).to(device="cuda")
                first = pyoidn.denoise(tensor)
                second = pyoidn.denoise(tensor)
            third = pyoidn.denoise(tensor)
            self.assertEqual(create_device.call_count, 2)
        self.assertEqual(first.device, tensor.device)
        torch.testing.assert_close(first, second)
        torch.testing.assert_close(first, third)
        torch.testing.assert_close(first, self._reference(tensor))


if __name__ == "__main__":
    unittest.main()
