import unittest


class PyOidnDeviceTest(unittest.TestCase):
    def test_create_cpu_device(self):
        import pyoidn

        device = pyoidn.Device(pyoidn.OIDN_DEVICE_TYPE_CPU)

        self.assertIsNone(device.get_error())
        device.commit()
        self.assertIsNone(device.get_error())
        device.release()

    def test_device_parameters(self):
        import pyoidn

        device = pyoidn.Device(pyoidn.OIDN_DEVICE_TYPE_CPU)

        self.assertEqual(device.get_int("type"), pyoidn.OIDN_DEVICE_TYPE_CPU)
        self.assertGreater(device.get_int("versionMajor"), 1)

        device.set_int("numThreads", 2)
        self.assertEqual(device.get_int("numThreads"), 2)

        device.commit()
        self.assertIsNone(device.get_error())

        device.release()

    def test_create_device_from_torch_cpu(self):
        try:
            import torch
        except ImportError:
            self.skipTest("torch not installed")

        import pyoidn

        device = pyoidn.Device.from_torch(torch.device("cpu"))
        self.assertIsNone(device.get_error())
        device.commit()
        self.assertIsNone(device.get_error())
        device.release()

    def test_create_device_from_torch_cuda(self):
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

        stream = torch.cuda.current_stream(device_id)
        device = pyoidn.Device.from_torch(torch.device("cuda", device_id), stream=stream)
        self.assertIsNone(device.get_error())
        device.commit()
        self.assertIsNone(device.get_error())
        device.release()


if __name__ == "__main__":
    unittest.main()
