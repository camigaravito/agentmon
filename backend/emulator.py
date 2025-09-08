import os
import threading
import time
from typing import Tuple, Optional
from pyboy import PyBoy
from dotenv import load_dotenv
from backend.agents.coordinator.meta_controller import MetaController
from backend.agents.explorer.explorer_agent import ExplorerAgent
from backend.agents.combat.combat_agent import CombatAgent
from config.logger_core import log_msg

load_dotenv()

def run_pyboy_threaded() -> Tuple[Optional[PyBoy], Optional[threading.Thread]]:
    rom = os.getenv("ROM_PATH")
    if not rom or not os.path.exists(rom):
        log_msg("error","emulator.rom_not_found",rom_path=rom)
        return None, None

    try:
        pyboy = PyBoy(rom, window="null", sound_emulated=False, debug=False)
        for _ in range(10):
            if not pyboy.tick():
                break
        if not hasattr(pyboy, "screen"):
            log_msg("error","emulator.no_screen_buffer")
            pyboy.stop()
            return None, None

        coord = MetaController(pyboy)
        exp   = ExplorerAgent(pyboy)
        comb  = CombatAgent(pyboy)
        coord.register_agents(exp, comb)

        def loop():
            cnt, max_s, freq = 0, 50000, 2000
            try:
                while cnt < max_s:
                    if not pyboy.tick():
                        log_msg("info","emulator.tick_failed",step=cnt)
                        break
                    coord.step()
                    cnt += 1
                    if cnt % freq == 0:
                        log_msg("info","system.thread_progress",step=cnt,max_steps=max_s)
                    time.sleep(0.001)
            except Exception as e:
                log_msg("error","emulator.thread_error",error=str(e))
            finally:
                pyboy.stop()
                log_msg("info","emulator.thread_stopped")

        thread = threading.Thread(target=loop, daemon=True)
        thread.start()
        log_msg("info","emulator.thread_started",rom_path=rom)
        return pyboy, thread

    except Exception as e:
        log_msg("error","emulator.thread_creation_error",error=str(e))
        return None, None