# backend/agents/explorer/explorer_agent.py

import json
import os
import random
from typing import Dict, Any, Tuple, List
from pyboy import PyBoy
from config.logger_core import log_msg


class ExplorerAgent:
    """
    Agente especializado en exploración del mundo y navegación de menús.
    """
    
    def __init__(self, pyboy: PyBoy):
        self.pyboy = pyboy
        self.actions_dict = self._load_actions_dict()
        self.visited_positions: Dict[Tuple[int, int], int] = {}
        self.current_direction: str = 'up'
        self.exploration_actions = self._get_exploration_actions()
        self.stuck_counter = 0
        self.last_position = (0, 0)
        
        # Control de logging para reducir frecuencia
        self.log_counter = 0
        self.log_frequency = 500  # Log cada 500 pasos
        
    def _load_actions_dict(self) -> Dict[str, Any]:
        """Carga el diccionario de acciones compartidas."""
        actions_path = os.path.join("src", "json", "actions.json")
        try:
            with open(actions_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            log_msg("error", "explorer.actions_not_found", file=actions_path)
            return {}
    
    def _get_exploration_actions(self) -> List[str]:
        """Obtiene las acciones disponibles para exploración."""
        context_actions = self.actions_dict.get("contexts", {}).get("exploration", {})
        return context_actions.get("primary_actions", ["up", "down", "left", "right"])
    
    def read_player_position(self) -> Tuple[int, int]:
        """Lee la posición del jugador desde la memoria RAM."""
        try:
            x = self.pyboy.memory[0xD361]
            y = self.pyboy.memory[0xD362]
            return (x, y)
        except:
            return (0, 0)
    
    def is_stuck(self, current_pos: Tuple[int, int]) -> bool:
        """Detecta si el jugador está atascado en la misma posición."""
        if current_pos == self.last_position:
            self.stuck_counter += 1
        else:
            self.stuck_counter = 0
            self.last_position = current_pos
        
        return self.stuck_counter > 30  # Aumentado para evitar cambios muy frecuentes
    
    def choose_exploration_action(self, current_pos: Tuple[int, int]) -> str:
        """
        Elige la siguiente acción de exploración basada en:
        - Posiciones menos visitadas
        - Evitar quedarse atascado
        - Exploración inteligente
        """
        if self.is_stuck(current_pos):
            # Si está atascado, elegir dirección aleatoria o interactuar
            available_actions = self.exploration_actions.copy()
            return random.choice(available_actions)
        
        # Estrategia simple: alternar entre movimiento y ocasionalmente interactuar
        movement_actions = ["up", "down", "left", "right"]
        
        # 90% probabilidad de moverse, 10% de interactuar
        if random.random() < 0.9:
            return random.choice(movement_actions)
        else:
            # Ocasionalmente presionar 'a' para interactuar
            return "a"
    
    def execute_action(self, action: str) -> None:
        """Ejecuta una acción en PyBoy."""
        try:
            # Liberar todas las teclas primero
            for btn in ["up", "down", "left", "right", "a", "b"]:
                self.pyboy.button_release(btn)
            
            # Presionar la acción seleccionada
            self.pyboy.button_press(action)
            
        except Exception as e:
            if self.log_counter % (self.log_frequency * 10) == 0:  # Log errores menos frecuente
                log_msg("error", "explorer.action_execution_error", action=action, error=str(e))
    
    def step(self) -> None:
        """
        Realiza un paso de exploración:
        1. Lee la posición actual
        2. Actualiza el mapa de visitas
        3. Elige y ejecuta la próxima acción
        """
        # Leer posición del jugador
        current_pos = self.read_player_position()
        
        # Actualizar contador de visitas
        self.visited_positions[current_pos] = self.visited_positions.get(current_pos, 0) + 1
        
        # Elegir acción basada en estrategia de exploración
        action = self.choose_exploration_action(current_pos)
        
        # Ejecutar acción
        self.execute_action(action)
        
        # Log solo ocasionalmente para reducir spam
        self.log_counter += 1
        if self.log_counter % self.log_frequency == 0:
            log_msg("info", "explorer.step_summary", 
                   position=current_pos, 
                   total_steps=self.log_counter,
                   unique_positions=len(self.visited_positions),
                   stuck_counter=self.stuck_counter)
    
    def get_visited_map(self) -> Dict[Tuple[int, int], int]:
        """Retorna el mapa de posiciones visitadas."""
        return self.visited_positions
    
    def get_exploration_stats(self) -> Dict[str, Any]:
        """Retorna estadísticas de exploración."""
        return {
            "positions_visited": len(self.visited_positions),
            "total_steps": sum(self.visited_positions.values()),
            "current_position": self.read_player_position(),
            "stuck_counter": self.stuck_counter
        }