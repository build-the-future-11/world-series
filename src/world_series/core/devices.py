"""Device selection with explicit CPU reference and optional accelerator fallback."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

DeviceName = Literal["cpu", "mps", "cuda"]


@dataclass(frozen=True)
class DeviceInfo:
    name: DeviceName
    dtype: str
    fallback: DeviceName
    available: bool
    notes: str = ""


def probe_devices() -> list[DeviceInfo]:
    infos: list[DeviceInfo] = [
        DeviceInfo(name="cpu", dtype="float64", fallback="cpu", available=True, notes="reference path"),
    ]
    try:
        import torch

        mps_ok = bool(getattr(torch.backends, "mps", None) and torch.backends.mps.is_available())
        infos.append(
            DeviceInfo(
                name="mps",
                dtype="float32",
                fallback="cpu",
                available=mps_ok,
                notes="optional; probe ops before using higher-order grads",
            )
        )
        cuda_ok = bool(torch.cuda.is_available())
        infos.append(
            DeviceInfo(
                name="cuda",
                dtype="float32",
                fallback="cpu",
                available=cuda_ok,
                notes="optional",
            )
        )
    except Exception as exc:  # noqa: BLE001
        infos.append(
            DeviceInfo(name="mps", dtype="float32", fallback="cpu", available=False, notes=str(exc))
        )
    return infos


def select_device(requested: str = "cpu") -> DeviceInfo:
    devices = {d.name: d for d in probe_devices()}
    req = requested.lower()
    if req not in devices:
        return devices["cpu"]
    info = devices[req]  # type: ignore[index]
    if not info.available:
        return devices[info.fallback]  # type: ignore[index]
    return info


def torch_device(info: DeviceInfo):
    import torch

    if info.name == "mps":
        return torch.device("mps")
    if info.name == "cuda":
        return torch.device("cuda")
    return torch.device("cpu")
