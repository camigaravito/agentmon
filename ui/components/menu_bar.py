from PySide6.QtWidgets import QMenuBar, QMenu, QWidget, QMessageBox
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtCore import Signal
from config.logger_core import log_msg


class GameMenuBar(QMenuBar):
    restart_requested = Signal()
    pause_requested = Signal()
    resume_requested = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_paused = False
        self.setup_menus()
        
    def setup_menus(self):
        emulator_menu = self.addMenu("&Emulador")
        
        restart_action = QAction("&Reiniciar", self)
        restart_action.setShortcut(QKeySequence("Ctrl+R"))
        restart_action.setStatusTip("Reinicia la memoria del juego")
        restart_action.triggered.connect(self.on_restart_clicked)
        emulator_menu.addAction(restart_action)
        
        emulator_menu.addSeparator()
        
        self.pause_action = QAction("&Pausar", self)
        self.pause_action.setShortcut(QKeySequence("Space"))
        self.pause_action.setStatusTip("Pausa o reanuda el emulador")
        self.pause_action.triggered.connect(self.on_pause_clicked)
        emulator_menu.addAction(self.pause_action)
        
        emulator_menu.addSeparator()
        
        exit_action = QAction("&Salir", self)
        exit_action.setShortcut(QKeySequence("Ctrl+Q"))
        exit_action.setStatusTip("Cierra la aplicación")
        exit_action.triggered.connect(self.close_application)
        emulator_menu.addAction(exit_action)
        
        help_menu = self.addMenu("&Ayuda")
        
        about_action = QAction("&Acerca de", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def on_restart_clicked(self):
        log_msg("info", "menu.restart_clicked")
        self.restart_requested.emit()
        
    def on_pause_clicked(self):
        if self.is_paused:
            log_msg("info", "menu.resume_clicked")
            self.resume_requested.emit()
            self.pause_action.setText("&Pausar")
            self.is_paused = False
        else:
            log_msg("info", "menu.pause_clicked")
            self.pause_requested.emit()
            self.pause_action.setText("&Reanudar")
            self.is_paused = True
    
    def close_application(self):
        parent = self.parent()
        if isinstance(parent, QWidget) and hasattr(parent, 'close'):
            parent.close()
            
    def show_about(self):
        parent = self.parent()
        if isinstance(parent, QWidget):
            QMessageBox.about(
                parent,
                "Acerca de AgentMon",
                "AgentMon v1.0\n\n"
                "Sistema Multi-Agente para PyBoy\n"
                "Desarrollado con PySide6 y PyBoy\n\n"
                "© 2025 - Proyecto de Grado UNAD"
            )
    
    def set_pause_state(self, paused: bool):
        self.is_paused = paused
        self.pause_action.setText("&Reanudar" if paused else "&Pausar")