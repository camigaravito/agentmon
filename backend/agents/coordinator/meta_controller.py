import json
import os
from typing import Dict, Any, Optional
from enum import Enum
from pyboy import PyBoy
from config.logger_core import log_msg


class GameContext(Enum):
    EXPLORATION = "exploration"
    COMBAT = "combat"
    MENU = "menu"
    UNKNOWN = "unknown"


class MetaController:
    def __init__(self, pyboy: PyBoy):
        self.pyboy = pyboy
        self.actions_dict = self._load_actions_dict()
        self.current_context = GameContext.EXPLORATION
        self.context_history = []
        
        self.explorer_agent = None
        self.combat_agent = None
        
    def _load_actions_dict(self) -> Dict[str, Any]:
        actions_path = os.path.join("src", "json", "actions.json")
        try:
            with open(actions_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            log_msg("error", "config.file_not_found", file=actions_path)
            return {}
    
    def register_agents(self, explorer_agent, combat_agent):
        self.explorer_agent = explorer_agent
        self.combat_agent = combat_agent
        log_msg("info", "coordinator.agents_registered")
    
    def detect_game_context(self) -> GameContext:
        try:
            battle_flag = self.pyboy.memory[0xD057]
            menu_flag = self.pyboy.memory[0xCC26]
            
            if battle_flag > 0:
                return GameContext.COMBAT
            elif menu_flag > 0:
                return GameContext.MENU
            else:
                return GameContext.EXPLORATION
                
        except Exception as e:
            log_msg("error", "coordinator.context_detection_error", error=str(e))
            return GameContext.UNKNOWN
    
    def should_switch_context(self, new_context: GameContext) -> bool:
        if new_context != self.current_context:
            if len(self.context_history) > 0:
                if self.context_history[-1] == new_context:
                    return False
            return True
        return False
    
    def get_active_agent(self):
        if self.current_context == GameContext.EXPLORATION:
            return self.explorer_agent
        elif self.current_context == GameContext.COMBAT:
            return self.combat_agent
        else:
            return self.explorer_agent
    
    def step(self) -> str:
        detected_context = self.detect_game_context()
        
        if self.should_switch_context(detected_context):
            previous_context = self.current_context
            self.current_context = detected_context
            self.context_history.append(previous_context)
            
            if len(self.context_history) > 10:
                self.context_history.pop(0)
                
            log_msg("info", "coordinator.context_switched", 
                   from_context=previous_context.value, 
                   to_context=detected_context.value)
        
        active_agent = self.get_active_agent()
        if active_agent:
            active_agent.step()
            return f"Agent: {active_agent.__class__.__name__}, Context: {self.current_context.value}"
        else:
            log_msg("error", "coordinator.no_active_agent")
            return "No active agent"
    
    def get_actions_for_context(self, context: str) -> Dict[str, Any]:
        return self.actions_dict.get("contexts", {}).get(context, {})
    
    def get_current_context(self) -> GameContext:
        return self.current_context
