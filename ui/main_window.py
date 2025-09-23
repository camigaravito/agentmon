import threading
from typing import Optional
import numpy as np
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStatusBar
from PySide6.QtCore import QTimer
from config.logger_core import log_msg
from ui.components.game_display import GameDisplay
from ui.components.menu_bar import GameMenuBar
from ui.components.noise_panel import NoisePanel
from backend.emulator import run_pyboy_threaded, last_explorer

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
        # Timer de estado cada 2 segundos
        self.status_timer = QTimer(self)
        self.status_timer.timeout.connect(self._update_status)
        self.status_timer.start(2000)

        # Timer del mapa de visitas cada 200ms (~5 FPS)
        self.noise_timer = QTimer(self)
        self.noise_timer.timeout.connect(self._update_noise_panel)
        self.noise_timer.start(200)

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
        if hasattr(self.menu, "_set_state"):
            self.menu._set_state(False, False)
        self.status.showMessage("Simulación detenida")
        log_msg("info", "ui.emulator_stopped")

    def _update_status(self):
        if self.running:
            stats = self.display.get_display_stats()
            fps = stats.get("current_fps", 0.0)
            buf = stats.get("buffer_size", 0)

            explorer = last_explorer
            if explorer and hasattr(explorer, "get_stats"):
                explorer_stats = explorer.get_stats()
                visited = explorer_stats.get("visited_positions", 0)
                self.status.showMessage(f"FPS: {fps:.1f} | Buffer: {buf} | Visitadas: {visited}")
            else:
                self.status.showMessage(f"FPS: {fps:.1f} | Buffer: {buf}")

    def _update_noise_panel(self):
        if not self.running:
            return

        explorer = last_explorer
        if explorer and hasattr(explorer, "get_noise_grayscale"):
            try:
                gray = explorer.get_noise_grayscale()
                if gray is not None and gray.size > 0:
                    self.noise_panel.set_gray(gray)
            except Exception as e:
                if hasattr(self, '_noise_error_count'):
                    self._noise_error_count += 1
                else:
                    self._noise_error_count = 1
                if self._noise_error_count % 100 == 0:
                    log_msg("warning", "ui.noise_panel_update_error",
                           error=str(e), count=self._noise_error_count)

    def closeEvent(self, event):
        log_msg("info", "ui.closing_application")
        self.stop_emulator()
        event.accept()