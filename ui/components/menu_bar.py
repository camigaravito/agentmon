from PySide6.QtWidgets import QMenuBar, QWidget, QMessageBox
from PySide6.QtGui import QKeySequence, QAction
from PySide6.QtCore import Signal
from config.logger_core import log_msg

class GameMenuBar(QMenuBar):
    start_requested   = Signal()
    restart_requested = Signal()
    pause_requested   = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._running = False
        self._paused = False
        self._init_menu()

    def _init_menu(self):
        emu = self.addMenu("&Emulador")

        self._start = QAction("&Iniciar", self)
        self._start.setShortcut(QKeySequence("Ctrl+S"))
        self._start.triggered.connect(self._on_start)
        emu.addAction(self._start)

        restart = QAction("&Reiniciar", self)
        restart.setShortcut(QKeySequence("Ctrl+R"))
        restart.triggered.connect(self._on_restart)
        emu.addAction(restart)

        emu.addSeparator()

        self._pause = QAction("&Pausar", self)
        self._pause.setShortcut(QKeySequence("Space"))
        self._pause.triggered.connect(self._on_pause)
        self._pause.setEnabled(False)
        emu.addAction(self._pause)

        emu.addSeparator()

        exit_action = QAction("&Salir", self)
        exit_action.setShortcut(QKeySequence("Ctrl+Q"))
        exit_action.triggered.connect(self._on_exit)
        emu.addAction(exit_action)

        help_menu = self.addMenu("&Ayuda")
        about = QAction("&Acerca de", self)
        about.triggered.connect(self._on_about)
        help_menu.addAction(about)

    def _on_start(self):
        log_msg("info", "menu.start_clicked")
        self.start_requested.emit()
        self._update_state(running=True, paused=False)

    def _on_restart(self):
        log_msg("info", "menu.restart_clicked")
        self.restart_requested.emit()
        self._update_state(running=True, paused=False)

    def _on_pause(self):
        log_msg("info", "menu.pause_clicked")
        self.pause_requested.emit()
        self._update_state(running=True, paused=True)

    def _on_exit(self):
        parent = self.parent()
        if isinstance(parent, QWidget):
            parent.close()

    def _on_about(self):
        parent = self.parent()
        if isinstance(parent, QWidget):
            QMessageBox.about(
                parent,
                "Acerca de AgentMon",
                "AgentMon v1.0\nSistema Multi-Agente para PyBoy\n© 2025 UNAD"
            )

    def _update_state(self, running: bool, paused: bool):
        self._running, self._paused = running, paused
        self._start.setEnabled(not running or paused)
        self._pause.setEnabled(running and not paused)
        self._start.setText("&Reanudar" if paused else "&Iniciar")
