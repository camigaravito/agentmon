import os
import threading
from typing import Tuple, Optional
from pyboy import PyBoy
from dotenv import load_dotenv
from backend.agents.coordinator.meta_controller import MetaController
from backend.agents.explorer.explorer_agent import ExplorerAgent
from backend.agents.combat.combat_agent import CombatAgent
from config.logger_core import log_msg

load_dotenv()

def run_pyboy() -> None:
    rom_path = os.getenv('ROM_PATH')
    log_msg("info", "emulator.start", rom_path=rom_path)
    pyboy = PyBoy(rom_path)
    coordinator = MetaController(pyboy)
    explorer = ExplorerAgent(pyboy)
    combat = CombatAgent(pyboy)
    coordinator.register_agents(explorer, combat)
    step_count = 0
    max_steps = 5000
    while step_count < max_steps and pyboy.tick():
        coordinator.step()
        step_count += 1
        if step_count % 100 == 0:
            log_msg(
                "info", "system.step_update",
                step=step_count,
                explorer_stats=explorer.get_exploration_stats(),
                combat_stats=combat.get_combat_stats()
            )
    log_msg(
        "info", "system.final_stats",
        total_steps=step_count,
        explorer_positions=len(explorer.get_visited_map()),
        combat_turns=combat.get_combat_stats()["battle_turns"]
    )
    pyboy.stop()
    log_msg("info", "emulator.stop")

def run_pyboy_threaded() -> Tuple[Optional[PyBoy], Optional[threading.Thread]]:
    rom_path = os.getenv('ROM_PATH')
    if not rom_path:
        log_msg("error", "emulator.rom_not_found", rom_path=rom_path)
        return None, None
    try:
        pyboy = PyBoy(rom_path)
        coordinator = MetaController(pyboy)
        explorer = ExplorerAgent(pyboy)
        combat = CombatAgent(pyboy)
        coordinator.register_agents(explorer, combat)
        def emulator_loop():
            step_count = 0
            max_steps = 50000
            try:
                while step_count < max_steps and pyboy.tick():
                    coordinator.step()
                    step_count += 1
            except Exception as e:
                log_msg("error", "emulator.thread_error", error=str(e))
            finally:
                pyboy.stop()
                log_msg("info", "emulator.thread_stopped")
        thread = threading.Thread(target=emulator_loop, daemon=True)
        thread.start()
        log_msg("info", "emulator.thread_started", rom_path=rom_path)
        return pyboy, thread
    except Exception as e:
        log_msg("error", "emulator.thread_creation_error", error=str(e))
        return None, None