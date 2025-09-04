# backend/agents/combat/combat_agent.py

import json
import os
import random
from typing import Dict, Any, List
from pyboy import PyBoy
from config.logger_core import log_msg


class CombatAgent:    
    def __init__(self, pyboy: PyBoy):
        self.pyboy = pyboy
        self.actions_dict = self._load_actions_dict()
        self.combat_actions = self._get_combat_actions()
        self.battle_turn_counter = 0
        
    def _load_actions_dict(self) -> Dict[str, Any]:
        actions_path = os.path.join("src", "json", "actions.json")
        try:
            with open(actions_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            log_msg("error", "combat.actions_not_found", file=actions_path)
            return {}
    
    def _get_combat_actions(self) -> List[str]:
        context_actions = self.actions_dict.get("contexts", {}).get("combat", {})
        return context_actions.get("primary_actions", ["a", "b"])
    
    def read_battle_state(self) -> Dict[str, Any]:
        try:
            player_hp = self.pyboy.memory[0xD015]
            enemy_hp = self.pyboy.memory[0xCFE6]
            turn_flag = self.pyboy.memory[0xCC3E]
            
            return {
                "player_hp": player_hp,
                "enemy_hp": enemy_hp,
                "turn_active": turn_flag > 0,
                "battle_active": self.pyboy.memory[0xD057] > 0
            }
        except Exception as e:
            log_msg("error", "combat.state_read_error", error=str(e))
            return {"battle_active": False}
    
    def choose_combat_action(self, battle_state: Dict[str, Any]) -> str:
        if not battle_state.get("turn_active", False):
            return "a"
        
        if battle_state.get("player_hp", 100) < 30:
            if random.random() < 0.3:
                return "down"
            else:
                return "a"
        else:
            if random.random() < 0.9:
                return "a"
            else:
                return "down"
    
    def execute_action(self, action: str) -> None:
        try:
            for btn in ["up", "down", "left", "right", "a", "b"]:
                self.pyboy.button_release(btn)
            
            self.pyboy.button_press(action)
            
        except Exception as e:
            log_msg("error", "combat.action_execution_error", action=action, error=str(e))
    
    def step(self) -> None:
        battle_state = self.read_battle_state()
        
        if not battle_state.get("battle_active", False):
            log_msg("info", "combat.no_battle_active")
            return
        
        action = self.choose_combat_action(battle_state)
        self.execute_action(action)
        
        self.battle_turn_counter += 1
        
        log_msg("info", "combat.step_completed",
               action=action,
               turn=self.battle_turn_counter,
               player_hp=battle_state.get("player_hp", "unknown"),
               enemy_hp=battle_state.get("enemy_hp", "unknown"))
    
    def get_combat_stats(self) -> Dict[str, Any]:
        current_state = self.read_battle_state()
        return {
            "battle_turns": self.battle_turn_counter,
            "current_battle_state": current_state
        }