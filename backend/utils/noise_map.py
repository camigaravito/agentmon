from __future__ import annotations
from dataclasses import dataclass, field
from typing import Tuple
import numpy as np

@dataclass
class InterestWeights:
    visit_inc: float = 1.0
    interact_inc: float = 4.0
    item_inc: float = 8.0
    shop_inc: float = 10.0
    heal_inc: float = 6.0

@dataclass
class NoiseConfig:
    rows: int = 15
    cols: int = 20
    decay: float = 0.997
    max_val: float = 255.0
    weights: InterestWeights = field(default_factory=InterestWeights)

class NoiseVisitMap:
    def __init__(self, cfg: NoiseConfig = NoiseConfig()):
        self.cfg = cfg
        self.grid = np.zeros((cfg.rows, cfg.cols), dtype=np.float32)
        self.blocked = np.zeros((cfg.rows, cfg.cols), dtype=bool)
        self.interest_layer = np.zeros((cfg.rows, cfg.cols), dtype=np.uint8)

    def reset(self):
        self.grid.fill(0.0)
        self.blocked.fill(False)
        self.interest_layer.fill(0)

    @property
    def shape(self) -> Tuple[int,int]:
        return self.grid.shape

    def in_bounds(self, r: int, c: int) -> bool:
        return 0 <= r < self.cfg.rows and 0 <= c < self.cfg.cols

    def decay_all(self):
        self.grid *= self.cfg.decay
        self.grid[self.blocked] = 0.0

    def mark_blocked(self, r: int, c: int, flag: bool = True):
        if self.in_bounds(r, c):
            self.blocked[r, c] = flag
            if flag:
                self.grid[r, c] = 0.0

    def add_visit(self, r: int, c: int):
        if self.in_bounds(r, c) and not self.blocked[r, c]:
            self.grid[r, c] = min(self.cfg.max_val, self.grid[r, c] + self.cfg.weights.visit_inc)

    def add_interact(self, r: int, c: int):
        if self.in_bounds(r, c) and not self.blocked[r, c]:
            self.grid[r, c] = min(self.cfg.max_val, self.grid[r, c] + self.cfg.weights.interact_inc)

    def set_interest(self, r: int, c: int, kind: str):
        if not self.in_bounds(r, c) or self.blocked[r, c]:
            return
        if kind == "item":
            inc, code = self.cfg.weights.item_inc, 1
        elif kind == "shop":
            inc, code = self.cfg.weights.shop_inc, 2
        elif kind == "heal":
            inc, code = self.cfg.weights.heal_inc, 3
        else:
            inc, code = 0.0, 0
        if inc > 0.0:
            self.grid[r, c] = min(self.cfg.max_val, self.grid[r, c] + inc)
            self.interest_layer[r, c] = code

    def to_grayscale_u8(self) -> np.ndarray:
        norm = np.clip(self.grid, 0.0, self.cfg.max_val) / (self.cfg.max_val if self.cfg.max_val > 0 else 1.0)
        gray = (255.0 - (norm * 255.0)).astype(np.uint8)
        gray[self.blocked] = 255
        return gray

    def get_interest_mask(self) -> np.ndarray:
        return self.interest_layer.copy()