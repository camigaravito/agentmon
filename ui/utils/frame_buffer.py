import time
from collections import deque
from typing import Optional
import numpy as np

class FrameBuffer:
    def __init__(self, target_fps: int = 30, buffer_size: int = 90):
        self.frame_time = 1.0 / target_fps
        self.buffer = deque(maxlen=buffer_size)
        self.last_time = time.time()
        self.frame_count = 0
        self.current: Optional[np.ndarray] = None

    def add_frame(self, frame: np.ndarray) -> None:
        self.buffer.append(frame.copy())

    def get_current_frame(self) -> Optional[np.ndarray]:
        now = time.time()
        if now - self.last_time >= self.frame_time and self.buffer:
            self.current = self.buffer[-1]
            self.last_time = now
            self.frame_count += 1
        return self.current

    def get_fps_stats(self) -> dict:
        elapsed = time.time() - self.last_time
        return {
            'buffer_size': len(self.buffer),
            'current_fps': self.frame_count / elapsed if elapsed > 0 else 0.0
        }

    def clear(self) -> None:
        self.buffer.clear()
        self.current = None
        self.frame_count = 0
        self.last_time = time.time()
