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
    """
    Logical device, use CPU device by default.
    """

    def __init__(self, device_type=OIDN_DEVICE_TYPE_CPU):
        # FIXME: fail when use OIDN_DEVICE_TYPE_DEFAULT, figure out why
        self._device = oidn_Capi.oidnNewDevice(device_type)

    def commit(self):
        oidn_Capi.oidnCommitDevice(self._device)

    def release(self):
        oidn_Capi.oidnReleaseDevice(self._device)

    def wait(self):
        """
        Wait for all async tasks to be done.
        """
        oidn_Capi.oidnSyncDevice(self._device)

    def get_bool(self, name: str) -> bool:
        return bool(oidn_Capi.oidnGetDeviceBool(self._device, name()))

    def set_bool(self, name: str, value: bool):
        oidn_Capi.oidnSetDeviceBool(self._device, c_str(name), value)

    def get_int(self, name: str) -> int:
        return oidn_Capi.oidnGetDeviceInt(self._device, c_str(name))

    def set_int(self, name: str, value: int):
        oidn_Capi.oidnSetDeviceInt(self._device, c_str(name), value)

    def get_uint(self, name: str) -> int:
        return oidn_Capi.oidnGetDeviceUInt(self._device, c_str(name))

    def set_uint(self, name: str, value: int):
        if value < 0:
            raise ValueError("Unsigned integer value cannot be negative")
        oidn_Capi.oidnSetDeviceUInt(self._device, c_str(name), value)

    def get_error(self) -> Optional[str]:
        out_message = oidn_ffi.new("const char**")
        oidn_Capi.oidnGetDeviceError(self._device, out_message)
        if oidn_ffi.NULL == out_message[0]:
            return None
        message = oidn_ffi.string(out_message[0])
        return message.decode()


def is_cpu_available():
    return oidn_Capi.oidnIsCPUDeviceSupported()


def is_cuda_available(device_id: int = 0):
    return oidn_Capi.oidnIsCUDADeviceSupported(device_id)
