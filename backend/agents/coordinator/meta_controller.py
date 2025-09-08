import os
import json
from typing import Dict, Any
from enum import Enum
from pyboy import PyBoy
from config.logger_core import log_msg

class GameContext(Enum):
    EXPLORATION = "exploration"
    COMBAT      = "combat"
    MENU        = "menu"
    UNKNOWN     = "unknown"

class MetaController:
    def __init__(self, pyboy: PyBoy):
        self.pyboy = pyboy
        path = os.path.join("src", "json", "actions.json")
        try:
            with open(path, encoding="utf-8") as f:
                self.actions_dict = json.load(f)
        except FileNotFoundError:
            log_msg("error","config.file_not_found",file=path)
            self.actions_dict = {}

        self.current = GameContext.EXPLORATION
        self.history = []
        self.explorer = None
        self.combat   = None

    def register_agents(self, explorer, combat):
        self.explorer, self.combat = explorer, combat
        log_msg("info","coordinator.agents_registered")

    def detect_game_context(self) -> GameContext:
        try:
            if self.pyboy.memory[0xD057] > 0:
                return GameContext.COMBAT
            if self.pyboy.memory[0xCC26] > 0:
                return GameContext.MENU
            return GameContext.EXPLORATION
        except Exception as e:
            log_msg("error","coordinator.context_detection_error",error=str(e))
            return GameContext.UNKNOWN

    def should_switch(self, ctx: GameContext) -> bool:
        return ctx != self.current and (not self.history or self.history[-1] != ctx)

    def step(self) -> str:
        ctx = self.detect_game_context()
        if self.should_switch(ctx):
            prev = self.current
            self.current = ctx
            self.history.append(prev)
            if len(self.history) > 10:
                self.history.pop(0)
            log_msg("info","coordinator.context_switched",
                   from_context=prev.value,to_context=ctx.value)

        agent = self.explorer if self.current == GameContext.EXPLORATION else self.combat
        if agent:
            agent.step()
            return f"Agent: {agent.__class__.__name__}, Context: {self.current.value}"
        log_msg("error","coordinator.no_active_agent")
        return "No active agent"

    def get_actions_for_context(self, ctx: str) -> Dict[str, Any]:
        return self.actions_dict.get("contexts",{}).get(ctx,{})

    def get_current_context(self) -> GameContext:
        return self.current