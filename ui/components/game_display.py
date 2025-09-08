from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget
from PySide6.QtCore import QTimer, QThread, Signal, Qt, QSize
from PySide6.QtGui import QImage, QPixmap
from typing import Optional
import numpy as np
from pyboy import PyBoy
from ui.utils.frame_buffer import FrameBuffer
from config.logger_core import log_msg


class GameDisplayThread(QThread):    
    frame_ready = Signal(np.ndarray)
    
    def __init__(self, pyboy: PyBoy):
        super().__init__()
        self.pyboy = pyboy
        self._running = False
        
    def run(self):
        self._running = True
        log_msg("info", "display.thread_started")
        
        while self._running:
            if self.pyboy and self.pyboy.tick():
                screen_array = self.pyboy.screen.ndarray.copy()
                self.frame_ready.emit(screen_array)
            else:
                break
                
        log_msg("info", "display.thread_stopped")
    
    def stop(self):
        self._running = False
        self.quit()
        self.wait()


class GameDisplay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.pyboy: Optional[PyBoy] = None
        self.frame_buffer = FrameBuffer(target_fps=30)
        
        self.setup_ui()
        self.setup_timer()
        
        self.capture_thread = None
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        self.game_label = QLabel()
        self.game_label.setFixedSize(300, 288)
        self.game_label.setStyleSheet("""
            QLabel {
                background-color: black;
                border: 2px solid #333333;
                border-radius: 4px;
            }
        """)
        self.game_label.setText("Esperando conexión con emulador...")
        
        layout.addWidget(self.game_label)
        
    def setup_timer(self):
        self.display_timer = QTimer()
        self.display_timer.timeout.connect(self.update_display)
        self.display_timer.start(33)
        
    def connect_emulator(self, pyboy: PyBoy):
        self.pyboy = pyboy
        
        self.capture_thread = GameDisplayThread(pyboy)
        self.capture_thread.frame_ready.connect(self.on_frame_received)
        self.capture_thread.start()
        
        log_msg("info", "display.emulator_connected")
        
    def on_frame_received(self, frame: np.ndarray):
        self.frame_buffer.add_frame(frame)
        
    def update_display(self):
        current_frame = self.frame_buffer.get_current_frame()
        
        if current_frame is not None:
            height, width, channels = current_frame.shape
            bytes_per_line = channels * width
            
            q_image = QImage(
                current_frame.data,
                width,
                height, 
                bytes_per_line,
                QImage.Format.Format_RGBA8888
            )
            
            pixmap = QPixmap.fromImage(q_image)
            scaled_pixmap = pixmap.scaled(
                QSize(300, 288),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            
            self.game_label.setPixmap(scaled_pixmap)
    
    def disconnect_emulator(self):
        if self.capture_thread:
            self.capture_thread.stop()
            self.capture_thread = None
            
        self.frame_buffer.clear()
        self.pyboy = None
        self.game_label.clear()
        self.game_label.setText("Emulador desconectado")
        
        log_msg("info", "display.emulator_disconnected")
    
    def get_display_stats(self) -> dict:
        return self.frame_buffer.get_fps_stats()