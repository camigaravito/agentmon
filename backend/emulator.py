# backend/emulator.py

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
    rom_path = os.getenv('ROM_PATH')
    if not rom_path or not os.path.exists(rom_path):
        log_msg("error", "emulator.rom_not_found", rom_path=rom_path)
        return None, None

    try:
        # Inicializar PyBoy con configuración para headless
        pyboy = PyBoy(
            rom_path, 
            window="null",           # Sin ventana nativa
            sound_emulated=False,    # Sin sonido
            debug=False
        )
        
        # Dar tiempo para que PyBoy inicialice completamente
        for _ in range(10):
            if not pyboy.tick():
                break
        
        # Verificar que el screen esté disponible
        if not hasattr(pyboy, 'screen'):
            log_msg("error", "emulator.no_screen_buffer")
            pyboy.stop()
            return None, None
            
        # Crear agentes
        coordinator = MetaController(pyboy)
        explorer = ExplorerAgent(pyboy)
        combat = CombatAgent(pyboy)
        coordinator.register_agents(explorer, combat)

        def emulator_loop():
            step_count = 0
            max_steps = 50000
            log_frequency = 2000
            
            try:
                while step_count < max_steps:
                    # Hacer tick de PyBoy primero
                    if not pyboy.tick():
                        log_msg("info", "emulator.tick_failed", step=step_count)
                        break
                    
                    # Ejecutar paso del coordinador
                    coordinator.step()
                    step_count += 1
                    
                    # Log de progreso
                    if step_count % log_frequency == 0:
                        log_msg("info", "system.thread_progress", 
                               step=step_count, max_steps=max_steps)
                    
                    # Pequeña pausa para no saturar CPU
                    time.sleep(0.001)
                        
            except Exception as e:
                log_msg("error", "emulator.thread_error", error=str(e))
            finally:
                pyboy.stop()
                log_msg("info", "emulator.thread_stopped")

        # Crear e iniciar thread
        thread = threading.Thread(target=emulator_loop, daemon=True)
        thread.start()
        
        log_msg("info", "emulator.thread_started", rom_path=rom_path)
        return pyboy, thread

    except Exception as e:
        log_msg("error", "emulator.thread_creation_error", error=str(e))
        return None, None