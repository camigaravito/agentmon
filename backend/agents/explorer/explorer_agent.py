import os
import json
import random
from typing import Dict, Tuple, Any
from pyboy import PyBoy
from config.logger_core import log_msg

class ExplorerAgent:
    def __init__(self, pyboy: PyBoy):
        self.pyboy = pyboy
        path = os.path.join("src", "json", "actions.json")
        try:
            with open(path, encoding="utf-8") as f:
                ctx = json.load(f)["contexts"]["exploration"]
                self.actions = ctx.get("primary_actions", ["up","down","left","right"])
        except Exception:
            log_msg("error", "explorer.actions_not_found", file=path)
            self.actions = ["up","down","left","right"]

        self.visits: Dict[Tuple[int,int],int] = {}
        self.stuck = 0
        self.last_pos = (0,0)
        self.logs = 0
        self.log_freq = 500

    def read_position(self) -> Tuple[int,int]:
        try:
            return (self.pyboy.memory[0xD361], self.pyboy.memory[0xD362])
        except:
            return self.last_pos

    def choose_action(self, pos: Tuple[int,int]) -> str:
        if pos == self.last_pos:
            self.stuck += 1
        else:
            self.stuck, self.last_pos = 0, pos
        if self.stuck > 30:
            return random.choice(self.actions)
        return random.choice(self.actions) if random.random() < 0.9 else "a"

    def step(self):
        pos = self.read_position()
        self.visits[pos] = self.visits.get(pos, 0) + 1
        act = self.choose_action(pos)
        for b in ["up","down","left","right","a","b"]:
            self.pyboy.button_release(b)
        try:
            self.pyboy.button_press(act)
        except Exception as e:
            if self.logs % (self.log_freq * 10) == 0:
                log_msg("error", "explorer.action_execution_error", action=act, error=str(e))
        self.logs += 1
        if self.logs % self.log_freq == 0:
            log_msg("info", "explorer.step_summary",
                   position=pos, total_steps=self.logs,
                   unique_positions=len(self.visits), stuck=self.stuck)

    def get_stats(self) -> Dict[str, Any]:
        return {
            "visited_positions": len(self.visits),
            "total_steps": sum(self.visits.values()),
            "current_position": self.last_pos,
            "stuck": self.stuck
        }