import unittest


class PyOidnMiscTest(unittest.TestCase):

    def test_import(self):
        import pyoidn

    def test_version_string(self):
        import pyoidn

        self.assertEqual(pyoidn.version.oidn_version, "2.5.0")


if __name__ == "__main__":
    unittest.main()
