"""Independent seeded RNG streams."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Optional

import numpy as np


@dataclass(frozen=True)
class SeedBundle:
    master: int
    data: int
    model: int
    eval: int

    @staticmethod
    def from_master(master: int) -> "SeedBundle":
        def derive(tag: str) -> int:
            digest = hashlib.sha256(f"{master}:{tag}".encode()).hexdigest()
            return int(digest[:8], 16)

        return SeedBundle(
            master=int(master),
            data=derive("data"),
            model=derive("model"),
            eval=derive("eval"),
        )


class SeededStreams:
    def __init__(self, bundle: SeedBundle):
        self.bundle = bundle
        self._data = np.random.default_rng(bundle.data)
        self._model = np.random.default_rng(bundle.model)
        self._eval = np.random.default_rng(bundle.eval)

    @property
    def data(self) -> np.random.Generator:
        return self._data

    @property
    def model(self) -> np.random.Generator:
        return self._model

    @property
    def eval(self) -> np.random.Generator:
        return self._eval

    def torch_manual_seed(self, which: str = "model") -> None:
        import torch

        seed = getattr(self.bundle, which)
        torch.manual_seed(int(seed) % (2**31 - 1))


def set_global_determinism(seed: int, *, warn_nondeterministic: bool = True) -> dict:
    """Best-effort determinism. Cross-device/bit-exact identity is not guaranteed."""
    import random

    random.seed(seed)
    np.random.seed(seed % (2**32 - 1))
    notes = {"numpy": True, "python": True, "torch": False, "warning": None}
    try:
        import torch

        torch.manual_seed(seed % (2**31 - 1))
        notes["torch"] = True
        if warn_nondeterministic:
            notes["warning"] = (
                "Seed control does not guarantee identical results across releases/devices."
            )
    except Exception as exc:  # noqa: BLE001
        notes["warning"] = str(exc)
    return notes
