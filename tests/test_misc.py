import unittest


class PyOidnMiscTest(unittest.TestCase):

    def test_import(self):
        import pyoidn

    def test_version_string(self):
        import pyoidn

        self.assertEqual(pyoidn.version.oidn_version, "2.4.0")

    def test_new_filter(self):
        import pyoidn

        device = pyoidn.Device()
        device.commit()

        filter = pyoidn.Filter(device, "RT")
        self.assertIsNone(device.get_error())

        filter.release()
        device.release()


if __name__ == "__main__":
    unittest.main()
