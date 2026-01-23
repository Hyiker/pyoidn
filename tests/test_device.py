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


if __name__ == "__main__":
    unittest.main()
