# backend/agents/explorer/explorer_agent.py

import json
import os
import random
from typing import Dict, Any, Tuple, List
from pyboy import PyBoy
from config.logger_core import log_msg


class ExplorerAgent:    
    def __init__(self, pyboy: PyBoy):
        self.pyboy = pyboy
        self.actions_dict = self._load_actions_dict()
        self.visited_positions: Dict[Tuple[int, int], int] = {}
        self.current_direction: str = 'up'
        self.exploration_actions = self._get_exploration_actions()
        self.stuck_counter = 0
        self.last_position = (0, 0)
        
    def _load_actions_dict(self) -> Dict[str, Any]:
        actions_path = os.path.join("src", "json", "actions.json")
        try:
            with open(actions_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            log_msg("error", "explorer.actions_not_found", file=actions_path)
            return {}
    
    def _get_exploration_actions(self) -> List[str]:
        context_actions = self.actions_dict.get("contexts", {}).get("exploration", {})
        return context_actions.get("primary_actions", ["up", "down", "left", "right"])
    
    def read_player_position(self) -> Tuple[int, int]:
        x = self.pyboy.memory[0xD361]
        y = self.pyboy.memory[0xD362]
        return (x, y)
    
    def is_stuck(self, current_pos: Tuple[int, int]) -> bool:
        if current_pos == self.last_position:
            self.stuck_counter += 1
        else:
            self.stuck_counter = 0
            self.last_position = current_pos
        
        return self.stuck_counter > 10
    
    def choose_exploration_action(self, current_pos: Tuple[int, int]) -> str:
        if self.is_stuck(current_pos):
            available_actions = self.exploration_actions.copy()
            return random.choice(available_actions)
        
        movement_actions = ["up", "down", "left", "right"]
        
        if random.random() < 0.8:
            return random.choice(movement_actions)
        else:
            return "a"
    
    def execute_action(self, action: str) -> None:
        try:
            for btn in ["up", "down", "left", "right", "a", "b"]:
                self.pyboy.button_release(btn)

            self.pyboy.button_press(action)
            
        except Exception as e:
            log_msg("error", "explorer.action_execution_error", action=action, error=str(e))
    
    def step(self) -> None:
        current_pos = self.read_player_position()

        self.visited_positions[current_pos] = self.visited_positions.get(current_pos, 0) + 1
        action = self.choose_exploration_action(current_pos)

        self.execute_action(action)
        
        log_msg("info", "explorer.step_completed", 
               position=current_pos, 
               action=action, 
               visits=self.visited_positions[current_pos])
    
    def get_visited_map(self) -> Dict[Tuple[int, int], int]:
        """Retorna el mapa de posiciones visitadas."""
        return self.visited_positions
    
    def get_exploration_stats(self) -> Dict[str, Any]:
        return {
            "positions_visited": len(self.visited_positions),
            "total_steps": sum(self.visited_positions.values()),
            "current_position": self.read_player_position(),
            "stuck_counter": self.stuck_counter
        }