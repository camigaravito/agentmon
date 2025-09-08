import sys
import os
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStatusBar
from PySide6.QtCore import QTimer
from PySide6.QtGui import QIcon

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from ui.components.game_display import GameDisplay
from ui.components.menu_bar import GameMenuBar
from backend.emulator import run_pyboy_threaded
from config.logger_core import log_msg


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.pyboy_instance = None
        self.emulator_thread = None
        
        self.setup_ui()
        self.setup_connections()
        self.setup_status_timer()
        
    def setup_ui(self):
        self.setWindowTitle("AgentMon - Sistema Multi-Agente PyBoy")
        self.setMinimumSize(800, 600)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        
        self.menu_bar = GameMenuBar(self)
        self.setMenuBar(self.menu_bar)

        top_layout = QHBoxLayout()
        self.game_display = GameDisplay()
        top_layout.addWidget(self.game_display)
        top_layout.addStretch()
        main_layout.addLayout(top_layout)
        main_layout.addStretch()
        
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Listo - Presiona Emulador > Reiniciar para comenzar")
        
    def setup_connections(self):
        self.menu_bar.restart_requested.connect(self.restart_emulator)
        self.menu_bar.pause_requested.connect(self.pause_emulator)
        self.menu_bar.resume_requested.connect(self.resume_emulator)
        
    def setup_status_timer(self):
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(2000)
        
    def restart_emulator(self):
        log_msg("info", "ui.restart_emulator")
        self.stop_emulator()
        self.start_emulator()
        
    def start_emulator(self):
        try:
            self.pyboy_instance, self.emulator_thread = run_pyboy_threaded()
            if self.pyboy_instance and self.emulator_thread:
                self.game_display.connect_emulator(self.pyboy_instance)
                self.status_bar.showMessage("Emulador iniciado - Ejecutando")
                log_msg("info", "ui.emulator_started")
            else:
                self.status_bar.showMessage("Error: No se pudo iniciar el emulador")
                log_msg("error", "ui.emulator_start_failed")
        except Exception as e:
            self.status_bar.showMessage(f"Error iniciando emulador: {e}")
            log_msg("error", "ui.emulator_start_error", error=str(e))
    
    def stop_emulator(self):
        if self.pyboy_instance:
            self.game_display.disconnect_emulator()
        if self.emulator_thread and self.emulator_thread.is_alive():
            self.emulator_thread.join(timeout=2)
        self.pyboy_instance = None
        self.emulator_thread = None
        log_msg("info", "ui.emulator_stopped")
        
    def pause_emulator(self):
        if self.pyboy_instance:
            self.status_bar.showMessage("Emulador pausado")
            log_msg("info", "ui.emulator_paused")
        
    def resume_emulator(self):
        if self.pyboy_instance:
            self.status_bar.showMessage("Emulador reanudado - Ejecutando")
            log_msg("info", "ui.emulator_resumed")
    
    def update_status(self):
        stats = self.game_display.get_display_stats()
        fps_info = f"FPS: {stats.get('current_fps', 0):.1f}"
        buffer_info = f"Buffer: {stats.get('buffer_size', 0)}"
        if self.pyboy_instance:
            self.status_bar.showMessage(f"Ejecutando - {fps_info} | {buffer_info}")
    
    def closeEvent(self, event):
        log_msg("info", "ui.closing_application")
        self.stop_emulator()
        event.accept()