from __future__ import annotations

from typing import Optional, Union

from .capi import oidn_Capi, oidn_ffi
from .device import Device

OIDN_STORAGE_UNDEFINED = 0
OIDN_STORAGE_HOST = 1
OIDN_STORAGE_DEVICE = 2
OIDN_STORAGE_MANAGED = 3


def _from_buffer(obj, require_writable: bool):
    try:
        return oidn_ffi.from_buffer(obj, require_writable=require_writable)
    except TypeError:
        return oidn_ffi.from_buffer(obj, require_writable)


class Buffer:
    """OIDN buffer wrapper.

    Mirrors the functions in `OIDN_FUNCTION_BUFFER`.

    Notes:
    - This is a thin wrapper; call `release()` when done.
    - `read*`/`write*` operate on host memory pointers.
    """

    def __init__(
        self,
        device: Device,
        byte_size: int,
        storage: Optional[int] = None,
    ) -> None:
        if byte_size < 0:
            raise ValueError("byte_size must be >= 0")

        self._device = device
        if storage is None:
            self._buffer = oidn_Capi.oidnNewBuffer(device._device, int(byte_size))
        else:
            self._buffer = oidn_Capi.oidnNewBufferWithStorage(device._device, int(byte_size), int(storage))

    @classmethod
    def shared(cls, device: Device, dev_ptr, byte_size: int) -> "Buffer":
        """Create a shared buffer from an existing pointer."""
        if byte_size < 0:
            raise ValueError("byte_size must be >= 0")

        self = cls.__new__(cls)
        self._device = device

        if isinstance(dev_ptr, int):
            dev_ptr = oidn_ffi.cast("void*", dev_ptr)
        self._buffer = oidn_Capi.oidnNewSharedBuffer(device._device, dev_ptr, int(byte_size))
        return self

    def release(self):
        if getattr(self, "_buffer", None) is None:
            return
        oidn_Capi.oidnReleaseBuffer(self._buffer)
        self._buffer = None

    @property
    def size(self) -> int:
        return int(oidn_Capi.oidnGetBufferSize(self._buffer))

    @property
    def storage(self) -> int:
        return int(oidn_Capi.oidnGetBufferStorage(self._buffer))

    def get_data(self):
        """Return the raw pointer returned by `oidnGetBufferData` (cffi pointer)."""
        return oidn_Capi.oidnGetBufferData(self._buffer)

    def read(self, byte_offset: int, byte_size: int, dst) -> None:
        """Read from buffer into a writable host buffer (e.g., numpy array, bytearray, memoryview)."""
        if byte_offset < 0 or byte_size < 0:
            raise ValueError("byte_offset/byte_size must be >= 0")

        dst_mv = dst if isinstance(dst, memoryview) else memoryview(dst)
        dst_ptr = oidn_ffi.cast("void*", _from_buffer(dst_mv, require_writable=True))
        oidn_Capi.oidnReadBuffer(self._buffer, int(byte_offset), int(byte_size), dst_ptr)

    def read_async(self, byte_offset: int, byte_size: int, dst) -> None:
        """Async version of `read` (synchronize via `Device.wait()`)."""
        if byte_offset < 0 or byte_size < 0:
            raise ValueError("byte_offset/byte_size must be >= 0")

        dst_mv = dst if isinstance(dst, memoryview) else memoryview(dst)
        dst_ptr = oidn_ffi.cast("void*", _from_buffer(dst_mv, require_writable=True))
        oidn_Capi.oidnReadBufferAsync(self._buffer, int(byte_offset), int(byte_size), dst_ptr)

    def write(self, byte_offset: int, byte_size: int, src) -> None:
        """Write into buffer from a host buffer (e.g., numpy array, bytes, memoryview)."""
        if byte_offset < 0 or byte_size < 0:
            raise ValueError("byte_offset/byte_size must be >= 0")

        src_mv = src if isinstance(src, memoryview) else memoryview(src)
        src_ptr = oidn_ffi.cast("const void*", _from_buffer(src_mv, require_writable=False))
        oidn_Capi.oidnWriteBuffer(self._buffer, int(byte_offset), int(byte_size), src_ptr)

    def write_async(self, byte_offset: int, byte_size: int, src) -> None:
        """Async version of `write` (synchronize via `Device.wait()`)."""
        if byte_offset < 0 or byte_size < 0:
            raise ValueError("byte_offset/byte_size must be >= 0")

        src_mv = src if isinstance(src, memoryview) else memoryview(src)
        src_ptr = oidn_ffi.cast("const void*", _from_buffer(src_mv, require_writable=False))
        oidn_Capi.oidnWriteBufferAsync(self._buffer, int(byte_offset), int(byte_size), src_ptr)

    def __enter__(self) -> "Buffer":
        return self

    def __exit__(self, exc_type, exc, tb):
        self.release()
        return False
