import threading
from typing import Optional
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStatusBar
from PySide6.QtCore import QTimer
from config.logger_core import log_msg
from ui.components.game_display import GameDisplay
from ui.components.menu_bar import GameMenuBar
from ui.components.noise_panel import NoisePanel
from backend.emulator import run_pyboy_threaded

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.pyboy: Optional[object] = None
        self.emulator_thread: Optional[threading.Thread] = None
        self.running = False
        self._init_ui()
        self._init_connections()
        self._init_timer()

    def _init_ui(self):
        self.setWindowTitle("AgentMon")
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        self.menu = GameMenuBar(self)
        self.setMenuBar(self.menu)

        row = QHBoxLayout()
        self.display = GameDisplay()
        row.addWidget(self.display)

        # Panel 300x300 a la derecha (sin backend aún)
        self.noise_panel = NoisePanel(self)
        row.addWidget(self.noise_panel)

        row.addStretch()
        layout.addLayout(row)
        layout.addStretch()

        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.showMessage("Listo - Presiona Iniciar")

    def _init_connections(self):
        self.menu.start_requested.connect(self.start_emulator)
        self.menu.restart_requested.connect(self.restart_emulator)
        self.menu.pause_requested.connect(self.pause_emulator)

    def _init_timer(self):
        timer = QTimer(self)
        timer.timeout.connect(self._update_status)
        timer.start(2000)

    def start_emulator(self):
        log_msg("info", "ui.start_emulator")
        self.pyboy, self.emulator_thread = run_pyboy_threaded()
        if self.pyboy and self.emulator_thread:
            self.display.connect_emulator(self.pyboy)
            self.running = True
            self.status.showMessage("Simulación iniciada")
        else:
            self.status.showMessage("Error iniciando simulación")

    def restart_emulator(self):
        log_msg("info", "ui.restart_emulator")
        self.stop_emulator()
        self.start_emulator()

    def pause_emulator(self):
        log_msg("info", "ui.pause_emulator")
        self.status.showMessage("Simulación pausada")

    def stop_emulator(self):
        if getattr(self.display, "capture_thread", None):
            self.display.disconnect_emulator()
        if self.emulator_thread and self.emulator_thread.is_alive():
            self.emulator_thread.join(2)
        self.running = False
        self.pyboy = None
        self.emulator_thread = None
        # Usar el método existente del menú
        if hasattr(self.menu, "_set_state"):
            self.menu._set_state(False, False)
        self.status.showMessage("Simulación detenida")
        log_msg("info", "ui.emulator_stopped")

    def _update_status(self):
        if self.running:
            stats = self.display.get_display_stats()
            fps = stats.get("current_fps", 0.0)
            buf = stats.get("buffer_size", 0)
            self.status.showMessage(f"FPS: {fps:.1f} | Buffer: {buf}")

    def closeEvent(self, event):
        log_msg("info", "ui.closing_application")
        self.stop_emulator()
        event.accept()