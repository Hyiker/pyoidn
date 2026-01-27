"""Device wrapper.

This module provides a thin Python wrapper around OIDN's device API.

Typical usage:

.. code-block:: python

    import pyoidn

    with pyoidn.Device() as device:
        device.commit()
        # create filters / buffers
        assert device.get_error() is None

Notes
-----
- The wrapper is intentionally minimal and mirrors OIDN's lifecycle.
- Error handling: call :meth:`Device.get_error` after creating/committing/executing.
- Refer to https://github.com/RenderKit/oidn?tab=readme-ov-file#devices for the OIDN property settings.
"""

from .capi import oidn_Capi, oidn_ffi
from typing import Optional
from .utils import c_str

OIDN_DEVICE_TYPE_DEFAULT = 0
OIDN_DEVICE_TYPE_CPU = 1
OIDN_DEVICE_TYPE_SYCL = 2
OIDN_DEVICE_TYPE_CUDA = 3
OIDN_DEVICE_TYPE_HIP = 4
OIDN_DEVICE_TYPE_METAL = 5


class Device:
    """Logical OIDN device.

    A device owns OIDN resources (filters, buffers) and provides synchronization.

    :param device_type:
        One of ``OIDN_DEVICE_TYPE_*``. The default is CPU.

    .. important::

        This class does not automatically call :meth:`commit`. You should call
        :meth:`commit` before executing filters.
    """

    def __init__(self, device_type=OIDN_DEVICE_TYPE_CPU):
        """Create a new device.

        :param device_type: One of ``OIDN_DEVICE_TYPE_*``.
        """
        # FIXME: fail when use OIDN_DEVICE_TYPE_DEFAULT, figure out why
        self._device = oidn_Capi.oidnNewDevice(device_type)

    def commit(self) -> None:
        """Commit device parameters.

        After setting device parameters (e.g., thread count), call this to apply them.
        """
        oidn_Capi.oidnCommitDevice(self._device)

    def release(self) -> None:
        """Release the underlying OIDN device handle."""
        oidn_Capi.oidnReleaseDevice(self._device)

    def wait(self) -> None:
        """Wait for all async tasks to finish."""
        oidn_Capi.oidnSyncDevice(self._device)

    def get_bool(self, name: str) -> bool:
        """Get a boolean device parameter.

        :param name: Parameter name (OIDN string).
        :return: The boolean value.
        """
        return bool(oidn_Capi.oidnGetDeviceBool(self._device, c_str(name)))

    def set_bool(self, name: str, value: bool) -> None:
        """Set a boolean device parameter.

        :param name: Parameter name (OIDN string).
        :param value: Boolean value.
        """
        oidn_Capi.oidnSetDeviceBool(self._device, c_str(name), value)

    def get_int(self, name: str) -> int:
        """Get an integer device parameter.

        :param name: Parameter name (OIDN string).
        :return: The integer value.
        """
        return oidn_Capi.oidnGetDeviceInt(self._device, c_str(name))

    def set_int(self, name: str, value: int) -> None:
        """Set an integer device parameter.

        :param name: Parameter name (OIDN string).
        :param value: Integer value.
        """
        oidn_Capi.oidnSetDeviceInt(self._device, c_str(name), value)

    def get_uint(self, name: str) -> int:
        """Get an unsigned integer device parameter.

        :param name: Parameter name (OIDN string).
        :return: The value as a Python int.
        """
        return oidn_Capi.oidnGetDeviceUInt(self._device, c_str(name))

    def set_uint(self, name: str, value: int) -> None:
        """Set an unsigned integer device parameter.

        :param name: Parameter name (OIDN string).
        :param value: Unsigned integer value.
        :raises ValueError: If ``value`` is negative.
        """
        if value < 0:
            raise ValueError("Unsigned integer value cannot be negative")
        oidn_Capi.oidnSetDeviceUInt(self._device, c_str(name), value)

    def get_error(self) -> Optional[str]:
        """Get the last device error message.

        :return:
            ``None`` if there is no error; otherwise a human-readable error message.

        .. note::

            OIDN reports errors asynchronously in some cases, so you may want to call
            :meth:`wait` before checking.
        """
        out_message = oidn_ffi.new("const char**")
        oidn_Capi.oidnGetDeviceError(self._device, out_message)
        if oidn_ffi.NULL == out_message[0]:
            return None
        message = oidn_ffi.string(out_message[0])
        if isinstance(message, str):
            return message
        if isinstance(message, (bytes, bytearray, memoryview)):
            return bytes(message).decode(errors="replace")
        return str(message)

    def __enter__(self) -> "Device":
        """Enter a context manager.

        :return: This device.
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit a context manager and release the device."""
        self.release()

    @staticmethod
    def is_cpu_available():
        """Return whether the CPU device backend is supported on this machine."""
        return oidn_Capi.oidnIsCPUDeviceSupported()

    @staticmethod
    def is_cuda_available(device_id: int = 0):
        """Return whether a CUDA device backend is supported.

        :param device_id: CUDA device index.
        :return: ``True`` if supported, otherwise ``False``.
        """
        return oidn_Capi.oidnIsCUDADeviceSupported(device_id)
