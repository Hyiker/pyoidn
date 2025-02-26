from .capi import oidn_ffi
import numpy as np


def c_str(py_str):
    return bytes(py_str, "ascii")


def np2c_ptr(np_array: np.array, ptr_type="void *"):
    return oidn_ffi.cast(ptr_type, oidn_ffi.from_buffer(np_array))
