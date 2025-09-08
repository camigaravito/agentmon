# main.py

import sys
import os
import warnings
from config.logger_core import get_logger, log_msg, get_log_file_path

# Suprimir warnings de SDL2
warnings.filterwarnings("ignore", message="Using SDL2 binaries from pysdl2-dll")

def run_console():
    """Ejecuta solo la simulación en consola (modo original)"""
    from backend.emulator import run_pyboy_threaded
    import threading
    
    logger = get_logger()
    log_msg("info", "system.ready")
    logger.info(f"Archivo de log: {get_log_file_path()}")
    
    # Configurar variables de entorno para deshabilitar SDL2
    os.environ['SDL_VIDEODRIVER'] = 'dummy'
    os.environ['SDL_AUDIODRIVER'] = 'dummy'
    
    pyboy, thread = run_pyboy_threaded()
    if pyboy and thread:
        try:
            # Esperar a que termine el thread
            thread.join()
        except KeyboardInterrupt:
            log_msg("info", "system.interrupted")
            if pyboy:
                pyboy.stop()
    else:
        log_msg("error", "system.failed_to_start")

def run_interface():
    """Ejecuta la simulación con interfaz gráfica"""
    from PySide6.QtWidgets import QApplication
    from ui.main_window import MainWindow
    
    # Configurar variables de entorno para deshabilitar SDL2
    os.environ['SDL_VIDEODRIVER'] = 'dummy'
    os.environ['SDL_AUDIODRIVER'] = 'dummy'
    
    logger = get_logger()
    log_msg("info", "system.ready")
    logger.info(f"Archivo de log: {get_log_file_path()}")
    
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
    # Detectar si se quiere ejecutar en modo consola o interfaz
    if len(sys.argv) > 1 and sys.argv[1] == "--console":
        run_console()
    else:
        # Por defecto ejecutar con interfaz gráfica
        sys.exit(run_interface())