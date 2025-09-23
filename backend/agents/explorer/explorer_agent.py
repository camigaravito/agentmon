import os
import json
import random
import numpy as np  # <-- agregar esta línea
from typing import Dict, Tuple, Any, Optional
from pyboy import PyBoy
from config.logger_core import log_msg
from backend.utils.noise_map import NoiseVisitMap, NoiseConfig

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
        self.last_pos = (0, 0)
        self.logs = 0
        self.log_freq = 500

        self.noise = NoiseVisitMap(NoiseConfig(rows=15, cols=20, decay=0.997))
        self._stay_ticks = 0

        self._world_offset = (0, 0)

    def read_position(self) -> Tuple[int,int]:
        try:
            x = self.pyboy.memory[0xD362]
            y = self.pyboy.memory[0xD361]
            return (x, y)
        except Exception:
            return self.last_pos

    def choose_action(self, pos: Tuple[int,int]) -> str:
        if pos == self.last_pos:
            self.stuck += 1
        else:
            self.stuck = 0
            
        if self.stuck > 20:
            return random.choice(self.actions)

        return random.choice(self.actions) if random.random() < 0.85 else "a"

    def world_to_local_grid(self, world_pos: Tuple[int,int]) -> Tuple[int,int]:
        wx, wy = world_pos
        center_r = self.noise.cfg.rows // 2
        center_c = self.noise.cfg.cols // 2
        
        current_x, current_y = self.last_pos if hasattr(self, 'last_pos') else (0, 0)
        
        rel_x = wx - current_x
        rel_y = wy - current_y
        
        local_r = center_r + rel_y
        local_c = center_c + rel_x
        
        return (local_r, local_c)

    def _detect_interaction(self) -> bool:
        return False

    def _detect_interest_kind(self) -> Optional[str]:
        return None

    def step(self):
        pos_before = self.read_position()

        action = self.choose_action(pos_before)

        for b in ["up","down","left","right","a","b"]:
            self.pyboy.button_release(b)
        
        try:
            self.pyboy.button_press(action)
        except Exception as e:
            if self.logs % (self.log_freq * 10) == 0:
                log_msg("error", "explorer.action_execution_error", action=action, error=str(e))

        pos_after = self.read_position()
        moved = (pos_after != pos_before)

        self.noise.decay_all()

        if moved and action in ("up","down","left","right"):
            self.last_pos = pos_after
            
            local_r, local_c = self.world_to_local_grid(pos_after)
            
            if self.noise.in_bounds(local_r, local_c):
                self.noise.add_visit(local_r, local_c)
                
            log_msg("debug", "explorer.moved", 
                   from_pos=pos_before, to_pos=pos_after, 
                   action=action, grid_pos=(local_r, local_c))
            
            self._stay_ticks = 0

        elif action in ("up","down","left","right") and not moved:
            self._stay_ticks += 1
            
            if self._stay_ticks >= 3:
                center_r = self.noise.cfg.rows // 2
                center_c = self.noise.cfg.cols // 2
                
                dr = -1 if action == "up" else (1 if action == "down" else 0)
                dc = -1 if action == "left" else (1 if action == "right" else 0)
                
                blocked_r = center_r + dr
                blocked_c = center_c + dc
                
                self.noise.mark_blocked(blocked_r, blocked_c, True)
                
                log_msg("debug", "explorer.blocked", 
                       direction=action, ticks=self._stay_ticks,
                       blocked_cell=(blocked_r, blocked_c))

        elif action == "a":
            if self._detect_interaction():
                center_r = self.noise.cfg.rows // 2
                center_c = self.noise.cfg.cols // 2
                self.noise.add_interact(center_r, center_c)
                
                interest_kind = self._detect_interest_kind()
                if interest_kind:
                    self.noise.set_interest(center_r, center_c, interest_kind)

        # Actualizar estadísticas generales
        self.visits[pos_after] = self.visits.get(pos_after, 0) + 1
        self.logs += 1
        
        # Log periódico de progreso
        if self.logs % self.log_freq == 0:
            unique_tiles = len(self.visits)
            total_visits = sum(self.visits.values())
            
            log_msg("info", "explorer.step_summary",
                    position=pos_after, total_steps=self.logs,
                    unique_tiles=unique_tiles, total_visits=total_visits,
                    stuck_ticks=self._stay_ticks)

    def get_noise_grayscale(self) -> Optional[np.ndarray]:
        """
        Devuelve el mapa de visitas como array 2D uint8 en escala de grises.
        Valores altos (visitados frecuentemente) = más oscuro
        Valores bajos (no visitados) = más claro/blanco
        """
        try:
            return self.noise.to_grayscale_u8()
        except Exception as e:
            log_msg("error", "explorer.noise_map_error", error=str(e))
            return None

    def get_stats(self) -> Dict[str, Any]:
        return {
            "visited_positions": len(self.visits),
            "total_steps": sum(self.visits.values()),
            "current_position": self.last_pos,
            "stuck_ticks": self._stay_ticks,
            "grid_shape": self.noise.shape
        }