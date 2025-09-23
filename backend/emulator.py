# backend/emulator.py

import os
import threading
import time
import traceback
from typing import Tuple, Optional
from pyboy import PyBoy
from dotenv import load_dotenv
from backend.agents.coordinator.meta_controller import MetaController
from backend.agents.explorer.explorer_agent import ExplorerAgent
from backend.agents.combat.combat_agent import CombatAgent
from config.logger_core import log_msg

load_dotenv()

# Variable de módulo para exponer el agente explorador
last_explorer: Optional[ExplorerAgent] = None

def run_pyboy_threaded() -> Tuple[Optional[PyBoy], Optional[threading.Thread]]:
    global last_explorer

    rom_path = os.getenv('ROM_PATH')
    if not rom_path or not os.path.exists(rom_path):
        log_msg("error", "emulator.rom_not_found", rom_path=rom_path)
        return None, None

    log_msg("info", "emulator.start", rom_path=os.path.abspath(rom_path))

    pyboy = PyBoy(
        rom_path,
        window="null",
        sound_emulated=False,
        debug=False
    )

    for _ in range(10):
        if not pyboy.tick():
            break

    if not hasattr(pyboy, 'screen'):
        log_msg("error", "emulator.no_screen_buffer")
        pyboy.stop()
        return None, None

    coordinator = MetaController(pyboy)
    explorer = ExplorerAgent(pyboy)
    combat = CombatAgent(pyboy)
    coordinator.register_agents(explorer, combat)

    # Exponer en variable de módulo
    last_explorer = explorer

    log_msg("info", "emulator.agents_created",
           coordinator=type(coordinator).__name__,
           explorer=type(explorer).__name__,
           combat=type(combat).__name__)

    def emulator_loop():
        step_count = 0
        max_steps = 50000
        log_frequency = 2000
        try:
            while step_count < max_steps:
                if not pyboy.tick():
                    log_msg("info", "emulator.tick_failed", step=step_count)
                    break
                coordinator.step()
                step_count += 1
                if step_count % log_frequency == 0:
                    stats = explorer.get_stats()
                    log_msg("info", "system.thread_progress",
                           step=step_count, max_steps=max_steps,
                           visited=stats["visited_positions"],
                           pos=stats["current_position"])
                time.sleep(0.001)
        except Exception as e:
            tb = traceback.format_exc()
            log_msg("error", "emulator.thread_error",
                   error=f"{type(e).__name__}: {e}",
                   traceback=tb)
        finally:
            pyboy.stop()
            log_msg("info", "emulator.thread_stopped")

    thread = threading.Thread(target=emulator_loop, daemon=True)
    thread.start()

    log_msg("info", "emulator.thread_started", rom_path=rom_path)
    return pyboy, thread