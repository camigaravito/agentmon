from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget
from PySide6.QtCore import QTimer, QThread, Signal, Qt, QSize
from PySide6.QtGui import QImage, QPixmap
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
            try:
                screen = getattr(self.pyboy, "screen", None)
                arr = screen.ndarray if screen is not None else None
                if arr is not None and arr.size:
                    self.frame_ready.emit(arr.copy())
                else:
                    break
                self.msleep(33)
            except Exception as e:
                log_msg("error", "display.frame_capture_error", error=str(e))
                break
        log_msg("info", "display.thread_stopped")

    def stop(self):
        self._running = False
        self.quit()
        self.wait(3000)

class GameDisplay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.pyboy = None
        self.frame_buffer = FrameBuffer(30)
        self.capture_thread = None
        self.has_frame = False
        self._init_ui()
        self._init_timer()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        self.game_label = QLabel(alignment=Qt.AlignmentFlag.AlignCenter)
        self.game_label.setFixedSize(300, 288)
        self.game_label.setStyleSheet(
            "background-color:black;border:2px solid #333;border-radius:4px;color:#ccc;font-size:12px"
        )
        self.game_label.setText("Esperando simulación...")
        layout.addWidget(self.game_label)

    def _init_timer(self):
        timer = QTimer(self)
        timer.timeout.connect(self.update_display)
        timer.start(33)

    def connect_emulator(self, pyboy: PyBoy):
        self.pyboy = pyboy
        self.game_label.clear()
        self.has_frame = False
        self.capture_thread = GameDisplayThread(pyboy)
        self.capture_thread.frame_ready.connect(self.on_frame_received)
        self.capture_thread.start()
        log_msg("info", "display.emulator_connected")

    def on_frame_received(self, frame: np.ndarray):
        if frame.size:
            self.frame_buffer.add_frame(frame)
            if not self.has_frame:
                self.frame_buffer.add_frame(frame)
                self.has_frame = True
                self.game_label.clear()

    def update_display(self):
        frame = self.frame_buffer.get_current_frame()
        if frame is None:
            return
        try:
            img = np.ascontiguousarray(frame)
            if img.ndim != 3:
                return
            h, w, c = img.shape
            if c == 4:
                img = img[:, :, :3]
            bpl = 3 * w
            qimg = QImage(img.data.tobytes(), w, h, bpl, QImage.Format.Format_RGB888)
            if qimg.isNull():
                return
            pm = QPixmap.fromImage(qimg).scaled(
                QSize(300, 288),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.game_label.setPixmap(pm)
        except Exception as e:
            cnt = getattr(self, "_errcnt", 0) + 1
            self._errcnt = cnt
            if cnt % 100 == 0:
                log_msg("error", "display.frame_processing_error", error=str(e), count=cnt)

    def disconnect_emulator(self):
        if self.capture_thread:
            self.capture_thread.stop()
            self.capture_thread = None
        self.frame_buffer.clear()
        self.pyboy = None
        self.game_label.clear()
        log_msg("info", "display.emulator_disconnected")

    def get_display_stats(self):
        return self.frame_buffer.get_fps_stats()