import unittest

import numpy as np


class PyOidnBufferTest(unittest.TestCase):
    def _make_device(self):
        import pyoidn

        device = pyoidn.Device(pyoidn.OIDN_DEVICE_TYPE_CPU)
        device.commit()
        self.assertIsNone(device.get_error())
        return device

    def test_create_buffer_default_and_properties(self):
        import pyoidn

        device = self._make_device()
        try:
            buf = pyoidn.Buffer(device, 64)
            try:
                self.assertEqual(buf.size, 64)
                # Different backends may report different default storage; assert it's a known value.
                self.assertIn(
                    buf.storage,
                    {
                        pyoidn.OIDN_STORAGE_UNDEFINED,
                        pyoidn.OIDN_STORAGE_HOST,
                        pyoidn.OIDN_STORAGE_DEVICE,
                        pyoidn.OIDN_STORAGE_MANAGED,
                    },
                )
            finally:
                buf.release()
        finally:
            self.assertIsNone(device.get_error())
            device.release()

    def test_create_buffer_with_storage_host(self):
        import pyoidn

        device = self._make_device()
        try:
            buf = pyoidn.Buffer(device, 32, storage=pyoidn.OIDN_STORAGE_HOST)
            try:
                self.assertEqual(buf.size, 32)
                self.assertEqual(buf.storage, pyoidn.OIDN_STORAGE_HOST)
            finally:
                buf.release()
        finally:
            self.assertIsNone(device.get_error())
            device.release()

    def test_get_data_not_null(self):
        import pyoidn
        from pyoidn.capi import oidn_ffi

        device = self._make_device()
        try:
            with pyoidn.Buffer(device, 8) as buf:
                ptr = buf.get_data()
                self.assertNotEqual(ptr, oidn_ffi.NULL)
        finally:
            self.assertIsNone(device.get_error())
            device.release()

    def test_buffer_read_write_roundtrip(self):
        import pyoidn

        device = self._make_device()
        try:
            with pyoidn.Buffer(device, 16) as buf:
                src = bytes(range(16))
                dst = bytearray(16)

                buf.write(0, 16, src)
                buf.read(0, 16, dst)

                self.assertEqual(bytes(dst), src)
        finally:
            self.assertIsNone(device.get_error())
            device.release()

    def test_buffer_read_write_with_offset(self):
        import pyoidn

        device = self._make_device()
        try:
            with pyoidn.Buffer(device, 32) as buf:
                payload = bytes([9] * 8)
                dst = bytearray(32)

                buf.write(0, 32, dst)
                buf.write(8, 8, payload)
                buf.read(0, 32, dst)

                self.assertEqual(bytes(dst[:8]), bytes([0] * 8))
                self.assertEqual(bytes(dst[8:16]), payload)
        finally:
            self.assertIsNone(device.get_error())
            device.release()

    def test_async_read_write_roundtrip(self):
        import pyoidn

        device = self._make_device()
        try:
            with pyoidn.Buffer(device, 16) as buf:
                src = bytes((255 - i) for i in range(16))
                dst = bytearray(16)

                buf.write_async(0, 16, src)
                device.wait()

                buf.read_async(0, 16, dst)
                device.wait()

                self.assertEqual(bytes(dst), src)
        finally:
            self.assertIsNone(device.get_error())
            device.release()

    def test_shared_buffer_numpy(self):
        import pyoidn

        device = self._make_device()
        try:
            arr = np.arange(32, dtype=np.uint8)
            ptr = pyoidn.utils.np2c_ptr(arr)

            buf = pyoidn.Buffer.shared(device, ptr, arr.nbytes)
            try:
                dst = bytearray(arr.nbytes)
                buf.read(0, arr.nbytes, dst)
                self.assertEqual(bytes(dst), arr.tobytes())

                new_src = bytes((i * 3) % 256 for i in range(arr.nbytes))
                buf.write(0, arr.nbytes, new_src)
                self.assertEqual(arr.tobytes(), new_src)
            finally:
                buf.release()
        finally:
            self.assertIsNone(device.get_error())
            device.release()

    def test_release_idempotent(self):
        import pyoidn

        device = self._make_device()
        try:
            buf = pyoidn.Buffer(device, 8)
            buf.release()
            buf.release()
        finally:
            self.assertIsNone(device.get_error())
            device.release()

    def test_invalid_arguments_raise(self):
        import pyoidn

        device = self._make_device()
        try:
            with self.assertRaises(ValueError):
                pyoidn.Buffer(device, -1)

            with pyoidn.Buffer(device, 8) as buf:
                with self.assertRaises(ValueError):
                    buf.read(-1, 1, bytearray(1))
                with self.assertRaises(ValueError):
                    buf.read(0, -1, bytearray(1))
                with self.assertRaises(ValueError):
                    buf.write(-1, 1, b"\x00")
                with self.assertRaises(ValueError):
                    buf.write(0, -1, b"\x00")

            with self.assertRaises(ValueError):
                pyoidn.Buffer.shared(device, 0, -1)
        finally:
            self.assertIsNone(device.get_error())
            device.release()


if __name__ == "__main__":
    unittest.main()
