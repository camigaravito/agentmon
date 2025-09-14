from PySide6.QtWidgets import QMenuBar, QWidget, QMessageBox
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtCore import Signal
from config.logger_core import log_msg


class GameMenuBar(QMenuBar):
    start_requested = Signal()
    restart_requested = Signal()
    pause_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_running = False
        self.is_paused = False
        self.setup_menus()

    def setup_menus(self):
        m = self.addMenu("&Emulador")
        self.start_action = QAction("&Iniciar", self)
        self.start_action.setShortcut(QKeySequence("Ctrl+S"))
        self.start_action.triggered.connect(self.on_start_clicked)
        m.addAction(self.start_action)

        r = QAction("&Reiniciar", self)
        r.setShortcut(QKeySequence("Ctrl+R"))
        r.triggered.connect(self.on_restart_clicked)
        m.addAction(r)

        m.addSeparator()

        self.pause_action = QAction("&Pausar", self)
        self.pause_action.setShortcut(QKeySequence("Space"))
        self.pause_action.triggered.connect(self.on_pause_clicked)
        self.pause_action.setEnabled(False)
        m.addAction(self.pause_action)

        m.addSeparator()

        e = QAction("&Salir", self)
        e.setShortcut(QKeySequence("Ctrl+Q"))
        e.triggered.connect(self.close_application)
        m.addAction(e)

        h = self.addMenu("&Ayuda")
        a = QAction("&Acerca de", self)
        a.triggered.connect(self.show_about)
        h.addAction(a)

    def on_start_clicked(self):
        log_msg("info", "menu.start_clicked")
        self.start_requested.emit()
        self._set_state(running=True, paused=False)

    def on_restart_clicked(self):
        log_msg("info", "menu.restart_clicked")
        self.restart_requested.emit()
        self._set_state(running=True, paused=False)

    def on_pause_clicked(self):
        log_msg("info", "menu.pause_clicked")
        self.pause_requested.emit()
        self._set_state(running=True, paused=True)

    def _set_state(self, running: bool, paused: bool):
        self.is_running, self.is_paused = running, paused
        self.start_action.setEnabled(not running or paused)
        self.pause_action.setEnabled(running and not paused)
        self.start_action.setText("&Reanudar" if paused else "&Iniciar")

    def close_application(self):
        p = self.parent()
        if isinstance(p, QWidget) and hasattr(p, "close"):
            p.close()

    def show_about(self):
        p = self.parent()
        if isinstance(p, QWidget):
            QMessageBox.about(
                p,
                "Acerca de AgentMon",
                "AgentMon v1.0\n\nSistema Multi-Agente para PyBoy\nDesarrollado con PySide6 y PyBoy\n© 2025 UNAD"
            )