import os
import threading
from typing import Optional
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStatusBar
from PySide6.QtCore import QTimer
from config.logger_core import log_msg
from ui.components.game_display import GameDisplay
from ui.components.menu_bar import GameMenuBar
from backend.emulator import run_pyboy_threaded


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.pyboy = None
        self.emulator_thread: Optional[threading.Thread] = None
        self.running = False
        self.setup_ui()
        self.setup_conns()
        self.setup_timer()

    def setup_ui(self):
        self.setWindowTitle("AgentMon")
        central = QWidget()
        self.setCentralWidget(central)
        v = QVBoxLayout(central)
        self.menu = GameMenuBar(self)
        self.setMenuBar(self.menu)
        h = QHBoxLayout()
        self.display = GameDisplay()
        h.addWidget(self.display)
        h.addStretch()
        v.addLayout(h)
        v.addStretch()
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.showMessage("Listo - Presiona Iniciar")

    def setup_conns(self):
        self.menu.start_requested.connect(self.start_emulator)
        self.menu.restart_requested.connect(self.restart_emulator)
        self.menu.pause_requested.connect(self.pause_emulator)

    def setup_timer(self):
        t = QTimer(self)
        t.timeout.connect(self.update_status)
        t.start(2000)

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
        if self.display:
            self.display.disconnect_emulator()
        if self.emulator_thread and self.emulator_thread.is_alive():
            self.emulator_thread.join(2)
        self.running = False
        self.pyboy = None
        self.emulator_thread = None
        self.menu._set_state(False, False)
        log_msg("info", "ui.emulator_stopped")

    def update_status(self):
        if self.running:
            s = self.display.get_display_stats()
            self.status.showMessage(f"FPS: {s.get('current_fps',0):.1f} | Buffer: {s.get('buffer_size',0)}")

    def closeEvent(self, e):
        log_msg("info", "ui.closing_application")
        self.stop_emulator()
        e.accept()