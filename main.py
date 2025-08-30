from backend.emulator import run_pyboy
from config.logger_core import get_logger, log_msg, get_log_file_path

if __name__ == "__main__":
    logger = get_logger()
    log_msg("info", "system.ready")
    logger.info(f"Archivo de log: {get_log_file_path()}")
    
    run_pyboy()