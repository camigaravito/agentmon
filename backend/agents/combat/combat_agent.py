import os
import json
import random
from typing import Dict, Any
from pyboy import PyBoy
from config.logger_core import log_msg

class CombatAgent:
    def __init__(self, pyboy: PyBoy):
        self.pyboy = pyboy
        path = os.path.join("src", "json", "actions.json")
        try:
            with open(path, encoding="utf-8") as f:
                ctx = json.load(f)["contexts"]["combat"]
                self.actions = ctx.get("primary_actions", ["a","b"])
        except Exception:
            log_msg("error","combat.actions_not_found",file=path)
            self.actions = ["a","b"]

        self.turns = 0
        self.logs = 0
        self.log_freq = 100

    def read_state(self) -> Dict[str, Any]:
        try:
            return {
                "player_hp":    self.pyboy.memory[0xD015],
                "enemy_hp":     self.pyboy.memory[0xCFE6],
                "turn_active":  self.pyboy.memory[0xCC3E] > 0,
                "battle_active":self.pyboy.memory[0xD057] > 0
            }
        except Exception as e:
            if self.logs % (self.log_freq*10) == 0:
                log_msg("error","combat.state_read_error",error=str(e))
            return {"battle_active": False}

    def choose_action(self, st: Dict[str, Any]) -> str:
        if not st.get("turn_active", False):
            return "a"
        hp = st.get("player_hp",100)
        if hp < 30:
            return "down" if random.random()<0.3 else "a"
        return "a" if random.random()<0.9 else "down"

    def step(self):
        st = self.read_state()
        if not st.get("battle_active",False):
            return
        act = self.choose_action(st)
        for b in ["up","down","left","right","a","b"]:
            self.pyboy.button_release(b)
        try:
            self.pyboy.button_press(act)
        except Exception as e:
            if self.logs % (self.log_freq*5) == 0:
                log_msg("error","combat.action_execution_error",action=act,error=str(e))
        self.turns += 1
        self.logs += 1
        if self.logs % self.log_freq == 0:
            log_msg("info","combat.battle_summary",
                   turns=self.turns,
                   player_hp=st.get("player_hp","?"),
                   enemy_hp= st.get("enemy_hp","?"))

    def get_stats(self) -> Dict[str, Any]:
        return {"battle_turns": self.turns, "state": self.read_state()}