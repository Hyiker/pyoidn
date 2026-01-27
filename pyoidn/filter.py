from .capi import oidn_Capi
from .device import Device
from .buffer import Buffer
from .utils import c_str, np2c_ptr
import numpy as np
from typing import Union

OIDN_FORMAT_UNDEFINED = 0

OIDN_FORMAT_FLOAT = 1
OIDN_FORMAT_FLOAT2 = OIDN_FORMAT_FLOAT + 1
OIDN_FORMAT_FLOAT3 = OIDN_FORMAT_FLOAT + 2
OIDN_FORMAT_FLOAT4 = OIDN_FORMAT_FLOAT + 3

OIDN_FORMAT_HALF = 257
OIDN_FORMAT_HALF2 = OIDN_FORMAT_HALF + 1
OIDN_FORMAT_HALF3 = OIDN_FORMAT_HALF + 2
OIDN_FORMAT_HALF4 = OIDN_FORMAT_HALF + 3

OIDN_QUALITY_DEFAULT = 0
OIDN_QUALITY_FAST = 4
OIDN_QUALITY_BALANCED = 5
OIDN_QUALITY_HIGH = 6

OIDN_IMAGE_COLOR = "color"
OIDN_IMAGE_ALBEDO = "albedo"
OIDN_IMAGE_NORMAL = "normal"
OIDN_IMAGE_OUTPUT = "output"

OIDN_FILTER_TYPE_RT = "RT"
OIDN_FILTER_TYPE_RT_LIGHTMAP = "RTLightmap"


class Filter:
    def __init__(self, device: Device, filter_type: str = OIDN_FILTER_TYPE_RT) -> None:
        """Create a filter

        :param device: pyoidn device
        :param filter_type: filter type, see OIDN_FILTER_TYPE_*
        """
        self._device = device
        self._filter = oidn_Capi.oidnNewFilter(device._device, c_str(filter_type))

    def set_image(
        self,
        name: str,
        data: Union[np.ndarray, Buffer],
        data_format: int,
        width: int = -1,
        height: int = -1,
        byte_offset: int = 0,
        pixel_byte_stride: int = 0,
        row_byte_stride: int = 0,
    ):
        """Set the input or output image for the filter

        :param name: The name of the image to set, see OIDN_IMAGE_*; typically "color", "albedo", "normal", etc.
        :param data: The numpy array or Buffer containing image data to be used by the filter, the numpy array should be contiguous.
        :param data_format: The format of the data, e.g., OIDN_FORMAT_FLOAT, OIDN_FORMAT_FLOAT2, etc.
        """
        if isinstance(data, Buffer):
            oidn_Capi.oidnSetFilterImage(
                self._filter,
                c_str(name),
                data._buffer,
                data_format,
                width,
                height,
                byte_offset,
                pixel_byte_stride,
                row_byte_stride,
            )
        elif isinstance(data, np.ndarray):
            oidn_Capi.oidnSetSharedFilterImage(
                self._filter,
                c_str(name),
                np2c_ptr(data),
                data_format,
                data.shape[1] if width < 0 else width,
                data.shape[0] if height < 0 else height,
                byte_offset,
                pixel_byte_stride,
                row_byte_stride,
            )

    def unset_image(self, name: str):
        """Unset the input or output image for the filter

        :param name: The name of the image to unset, see OIDN_IMAGE_*; typically "color", "albedo", "normal", etc.
        """
        oidn_Capi.oidnUnsetFilterImage(self._filter, c_str(name))

    def get_bool(self, name: str) -> bool:
        return bool(oidn_Capi.oidnGetFilterBool(self._filter, c_str(name)))

    def set_bool(self, name: str, value: bool):
        oidn_Capi.oidnSetFilterBool(self._filter, c_str(name), value)

    def get_int(self, name: str) -> int:
        return oidn_Capi.oidnGetFilterInt(self._filter, c_str(name))

    def set_int(self, name: str, value: int):
        oidn_Capi.oidnSetFilterInt(self._filter, c_str(name), value)

    def get_float(self, name: str) -> float:
        return oidn_Capi.oidnGetFilterFloat(self._filter, c_str(name))

    def set_float(self, name: str, value: float):
        oidn_Capi.oidnSetFilterFloat(self._filter, c_str(name), value)

    def set_value(self, k: str, value):
        if isinstance(value, int):
            self.set_int(k, value)
        elif isinstance(value, bool):
            self.set_bool(k, value)
        elif isinstance(value, float):
            self.set_float(k, value)
        else:
            raise TypeError("Unsupported value type: {}".format(type(value)))

    def set_quality(self, quality: int):
        """
        :param quality: see OIDN_QUALITY_*
        """
        self.set_int("quality", quality)

    def commit(self):
        oidn_Capi.oidnCommitFilter(self._filter)

    def execute(self):
        oidn_Capi.oidnExecuteFilter(self._filter)

    def execute_async(self):
        oidn_Capi.oidnExecuteFilterAsync(self._filter)

    def release(self):
        oidn_Capi.oidnReleaseFilter(self._filter)

    def __enter__(self) -> "Filter":
        return self

    def __exit__(self, exc_type, exc, tb):
        self.release()
        return self
