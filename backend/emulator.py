import os
from pyboy import PyBoy
from dotenv import load_dotenv
from backend.agents.coordinator.meta_controller import MetaController
from backend.agents.explorer.explorer_agent import ExplorerAgent
from backend.agents.combat.combat_agent import CombatAgent
from config.logger_core import log_msg

load_dotenv()

def run_pyboy():
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
        active_info = coordinator.step()
        step_count += 1
        
        if step_count % 100 == 0:
            log_msg("info", "system.step_update", 
                   step=step_count, 
                   active=active_info,
                   explorer_stats=explorer.get_exploration_stats(),
                   combat_stats=combat.get_combat_stats())
    
    log_msg("info", "system.final_stats",
           total_steps=step_count,
           explorer_positions=len(explorer.get_visited_map()),
           combat_turns=combat.get_combat_stats()["battle_turns"])
    
    pyboy.stop()
    log_msg("info", "emulator.stop")