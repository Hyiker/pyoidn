# SPDX-FileCopyrightText: Copyright (c) 2026
# SPDX-License-Identifier: MIT
"""Convenience API for denoising an image in a single call."""

import atexit
from dataclasses import dataclass, field
from threading import RLock
from typing import Any, Dict, Optional, Tuple, Union

import numpy as np

from .capi import oidn_Capi, oidn_ffi
from .device import Device
from .filter import (
    Filter,
    OIDN_FILTER_TYPE_RT,
    OIDN_FILTER_TYPE_RT_LIGHTMAP,
    OIDN_FORMAT_FLOAT3,
    OIDN_FORMAT_HALF3,
    OIDN_QUALITY_BALANCED,
    OIDN_QUALITY_DEFAULT,
    OIDN_QUALITY_FAST,
    OIDN_QUALITY_HIGH,
)
from .utils import TORCH_AVAILABLE

__all__ = ["denoise"]

_QUALITIES = {
    "default": OIDN_QUALITY_DEFAULT,
    "fast": OIDN_QUALITY_FAST,
    "balanced": OIDN_QUALITY_BALANCED,
    "high": OIDN_QUALITY_HIGH,
}


def _prepare_image(image: Any, name: str, color: Any) -> Tuple[Any, int]:
    """Validate an RGB image and return contiguous storage and its OIDN format."""
    if isinstance(color, np.ndarray):
        if not isinstance(image, np.ndarray):
            raise TypeError(f"{name} must be a NumPy array, like color")
        if image.dtype not in (np.float16, np.float32):
            raise TypeError(f"{name} must have dtype float16 or float32")
        is_half = image.dtype == np.float16
    else:
        import torch

        if not isinstance(image, torch.Tensor):
            raise TypeError(f"{name} must be a PyTorch tensor, like color")
        if image.dtype not in (torch.float16, torch.float32):
            raise TypeError(f"{name} must have dtype float16 or float32")
        if image.device.type not in ("cpu", "cuda") or image.device != color.device:
            raise ValueError(f"{name} must be on the same CPU or CUDA device as color")
        if image.layout != torch.strided:
            raise ValueError(f"{name} must have a strided tensor layout")
        is_half = image.dtype == torch.float16

    if image.ndim != 3 or image.shape[2] != 3 or min(image.shape[:2]) == 0:
        raise ValueError(f"{name} must have shape (height, width, 3) with nonzero dimensions")
    if image.shape != color.shape:
        raise ValueError(f"{name} must have the same shape as color")

    prepared = (
        np.ascontiguousarray(image)
        if isinstance(image, np.ndarray)
        else image.detach().contiguous()
    )
    return prepared, OIDN_FORMAT_HALF3 if is_half else OIDN_FORMAT_FLOAT3


def _check_error(device: Device, operation: str) -> None:
    """Raise a runtime error for a failed convenience API operation."""
    message_ptr = oidn_ffi.new("const char**")
    code = int(oidn_Capi.oidnGetDeviceError(device._device, message_ptr))
    if code != 0:
        message = (
            oidn_ffi.string(message_ptr[0]).decode("utf-8", errors="replace")
            if message_ptr[0] != oidn_ffi.NULL
            else "no error message was provided"
        )
        raise RuntimeError(f"OIDN {operation} failed (error {code}): {message}")


@dataclass
class _DeviceResources:
    """Native resources reused on one CPU device or CUDA stream."""

    device: Device  # Committed OIDN device.
    stream: Any  # Retains the associated Torch CUDA stream, or None for CPU.
    filters: Dict[str, Filter] = field(default_factory=dict)  # One per filter type.
    # Shared allocations retained until their bindings are replaced or released.
    images: Dict[str, Dict[str, Tuple[Any, int]]] = field(default_factory=dict)


class _Denoiser:
    """Process-wide owner of lazily initialized, reusable denoising resources."""

    def __init__(self) -> None:
        self._resources: Dict[Tuple[str, int, int], _DeviceResources] = {}
        self._lock = RLock()

    def _get_resources(self, color: Any) -> _DeviceResources:
        """Return the committed device associated with the input's current stream."""
        stream = None
        key = ("cpu", 0, 0)
        if not isinstance(color, np.ndarray) and color.device.type == "cuda":
            import torch

            stream = torch.cuda.current_stream(color.device)
            key = ("cuda", int(color.device.index), int(stream.cuda_stream))
        if key not in self._resources:
            device = Device() if stream is None else Device.from_torch(color.device, stream)
            try:
                _check_error(device, "device creation")
                if device._device == oidn_ffi.NULL:
                    raise RuntimeError("OIDN device creation returned a null handle")
                device.commit()
                _check_error(device, "device commit")
            except BaseException:
                if device._device != oidn_ffi.NULL:
                    device.release()
                raise
            self._resources[key] = _DeviceResources(device, stream)
        return self._resources[key]

    def run(
        self,
        images: Dict[str, Tuple[Any, int]],
        color: Any,
        hdr: bool,
        clean_aux: bool,
        quality: int,
        filter_type: str,
    ) -> None:
        """Bind this call's images and execute with exclusive access to cached filters."""
        with self._lock:
            resources = self._get_resources(color)
            device = resources.device
            flt = resources.filters.get(filter_type)
            try:
                if flt is None:
                    flt = Filter(device, filter_type)
                    _check_error(device, "filter creation")
                    if flt._filter == oidn_ffi.NULL:
                        raise RuntimeError("OIDN filter creation returned a null handle")
                    resources.filters[filter_type] = flt
                for name in resources.images.get(filter_type, {}):
                    if name not in images:
                        flt.unset_image(name)
                        _check_error(device, f"unsetting {name} image")
                for name, (image, data_format) in images.items():
                    flt.set_image(name, image, data_format)
                    _check_error(device, f"setting {name} image")
                if filter_type == OIDN_FILTER_TYPE_RT:
                    flt.set_bool("hdr", hdr)
                    flt.set_bool("cleanAux", clean_aux)
                flt.set_quality(quality)
                _check_error(device, "filter configuration")
                flt.commit()
                _check_error(device, "filter commit")
                flt.execute()
                _check_error(device, "filter execution")
            except BaseException:
                # Release before dropping either the old or partially rebound allocations.
                if flt is not None and flt._filter != oidn_ffi.NULL:
                    flt.release()
                resources.filters.pop(filter_type, None)
                resources.images.pop(filter_type, None)
                raise
            resources.images[filter_type] = images

    def close(self) -> None:
        """Release cached filters before their devices and backing allocations."""
        with self._lock:
            for resources in self._resources.values():
                for flt in resources.filters.values():
                    flt.release()
                resources.device.release()
            self._resources.clear()


_denoiser = _Denoiser()
atexit.register(_denoiser.close)


def denoise(
    color: Any,
    albedo: Optional[Any] = None,
    normal: Optional[Any] = None,
    *,
    hdr: bool = False,
    clean_aux: bool = False,
    quality: Union[str, int] = "high",
    filter_type: str = OIDN_FILTER_TYPE_RT,
) -> Any:
    """Denoise an RGB image and return a new image, ready to use.

    Reuses an internal device and filter across calls. NumPy and CPU Torch inputs
    share a CPU device; CUDA resources are cached per device and current stream.
    Resources are initialized lazily and released when the process exits. Calls
    are serialized to protect the shared filter configuration.
    Noncontiguous inputs are copied to contiguous storage on the same device.
    Inputs are never modified. This operation is synchronous and not differentiable.

    :param color: NumPy array or Torch tensor of shape ``(H, W, 3)``, with
        nonzero dimensions and dtype float16 or float32. Use linear color values;
        LDR colors are in [0, 1], HDR colors are nonnegative.
    :param albedo: Optional albedo in [0, 1], with the same shape, container type,
        and device as color. Its dtype may independently be float16 or float32.
    :param normal: Optional world- or view-space normals in [-1, 1], with the
        same requirements as albedo.
    :param hdr: Whether RT color input is HDR. RTLightmap always processes HDR.
    :param clean_aux: Whether auxiliary images are already noise-free. Does not
        prefilter them. Supported only by RT.
    :param quality: ``"high"``, ``"balanced"``, ``"fast"``, ``"default"``, or
        the corresponding ``OIDN_QUALITY_*`` constant.
    :param filter_type: ``"RT"`` for rendered images or ``"RTLightmap"`` for
        HDR lightmaps. RTLightmap does not accept albedo or normal inputs.
    :return: A contiguous image with color's shape, dtype, container type, and
        device. Torch output does not require gradients.
    :raises TypeError: If an input type or dtype is unsupported.
    :raises ValueError: If image shapes, devices, or options are incompatible.
    :raises RuntimeError: If OIDN reports a failure.
    """
    is_numpy = isinstance(color, np.ndarray)
    if not is_numpy:
        if not TORCH_AVAILABLE:
            raise TypeError("color must be a NumPy array or an available PyTorch tensor")
        import torch

        if not isinstance(color, torch.Tensor):
            raise TypeError("color must be a NumPy array or a PyTorch tensor")

    if filter_type not in (OIDN_FILTER_TYPE_RT, OIDN_FILTER_TYPE_RT_LIGHTMAP):
        raise ValueError("filter_type must be 'RT' or 'RTLightmap'")
    if not isinstance(hdr, bool) or not isinstance(clean_aux, bool):
        raise TypeError("hdr and clean_aux must be bool values")
    if filter_type == OIDN_FILTER_TYPE_RT_LIGHTMAP:
        if albedo is not None or normal is not None or clean_aux:
            raise ValueError("RTLightmap does not support albedo, normal, or clean_aux")
    if isinstance(quality, str):
        if quality not in _QUALITIES:
            raise ValueError("quality must be 'high', 'balanced', 'fast', or 'default'")
        quality = _QUALITIES[quality]
    elif isinstance(quality, bool) or not isinstance(quality, int):
        raise TypeError("quality must be a quality name or an OIDN_QUALITY_* constant")
    elif quality not in _QUALITIES.values():
        raise ValueError("quality must be an OIDN_QUALITY_* constant")

    images = {"color": _prepare_image(color, "color", color)}
    for name, image in (("albedo", albedo), ("normal", normal)):
        if image is not None:
            images[name] = _prepare_image(image, name, color)
    output = (
        np.empty_like(images["color"][0])
        if is_numpy
        else torch.empty_like(images["color"][0])
    )
    images["output"] = (output, images["color"][1])
    _denoiser.run(images, color, hdr, clean_aux, quality, filter_type)
    return output
