import time
import threading
from collections import deque
from typing import Optional
import numpy as np
from config.logger_core import log_msg


class FrameBuffer:    
    def __init__(self, target_fps: int = 30, buffer_size: int = 90):
        self.target_fps = target_fps
        self.frame_time = 1.0 / target_fps
        self.buffer_size = buffer_size
        
        self.frame_buffer = deque(maxlen=buffer_size)
        self.current_frame: Optional[np.ndarray] = None
        self.last_frame_time = time.time()
        self.frame_count = 0
        
        self._lock = threading.Lock()
        self._running = False
        self._buffer_thread = None
        
    def add_frame(self, frame: np.ndarray) -> None:
        with self._lock:
            frame_copy = frame.copy()
            self.frame_buffer.append({
                'frame': frame_copy,
                'timestamp': time.time()
            })
            
    def get_current_frame(self) -> Optional[np.ndarray]:
        current_time = time.time()
        
        if current_time - self.last_frame_time >= self.frame_time:
            with self._lock:
                if self.frame_buffer:
                    latest_frame_data = self.frame_buffer[-1]
                    self.current_frame = latest_frame_data['frame']
                    self.last_frame_time = current_time
                    self.frame_count += 1
                    
        return self.current_frame
    
    def get_fps_stats(self) -> dict:
        with self._lock:
            return {
                'buffer_size': len(self.frame_buffer),
                'target_fps': self.target_fps,
                'frame_count': self.frame_count,
                'current_fps': self.frame_count / max(time.time() - self.last_frame_time, 1)
            }
    
    def clear(self) -> None:
        with self._lock:
            self.frame_buffer.clear()
            self.current_frame = None
            self.frame_count = 0
            self.last_frame_time = time.time()