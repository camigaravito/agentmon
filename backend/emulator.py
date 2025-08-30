import os
from pyboy import PyBoy
from dotenv import load_dotenv
from config.logger_core import log_msg

load_dotenv()

def run_pyboy():
  rom_path = os.getenv('ROM_PATH')
  log_msg("info", "emulator.start", rom_path=rom_path)
  
  pyboy = PyBoy(rom_path)
  while pyboy.tick():
      pass
  pyboy.stop()
  log_msg("info", "emulator.stop")