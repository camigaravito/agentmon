import sys
import os
from PySide6.QtWidgets import QApplication

sys.path.append(os.path.dirname(__file__))

from ui.main_window import MainWindow
from config.logger_core import get_logger, log_msg

def main():
    logger = get_logger()
    log_msg("info", "system.ready")
    
    app = QApplication(sys.argv)
    app.setApplicationName("AgentMon")
    app.setOrganizationName("UNAD")
    
    main_window = MainWindow()
    main_window.show()
    
    log_msg("info", "ui.application_started")

    try:
        exit_code = app.exec()
        log_msg("info", "ui.application_closed", exit_code=exit_code)
        return exit_code
    except KeyboardInterrupt:
        log_msg("info", "ui.application_interrupted")
        return 0

if __name__ == "__main__":
    sys.exit(main())