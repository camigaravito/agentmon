# backend/agents/explorer/explorer_agent.py

import os
import json
import random
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
        self.last_pos = (0,0)
        self.logs = 0
        self.log_freq = 500

        # Mapa de ruido (centrar jugador en la ventana)
        self.noise = NoiseVisitMap(NoiseConfig(rows=15, cols=20, decay=0.997))
        self._stay_ticks = 0

    def read_position(self) -> Tuple[int,int]:
        try:
            # Pokémon Rojo/Azul: X=0xD361, Y=0xD362 (dirección puede variar por versión)
            return (self.pyboy.memory[0xD361], self.pyboy.memory[0xD362])
        except Exception:
            return self.last_pos

    def choose_action(self, pos: Tuple[int,int]) -> str:
        if pos == self.last_pos:
            self.stuck += 1
        else:
            self.stuck, self.last_pos = 0, pos
        if self.stuck > 20:
            # forzar movimiento diferente si se atasca
            return random.choice(self.actions)
        # favorecer movimiento; ocasional "a" para probar interacción
        return random.choice(self.actions) if random.random() < 0.85 else "a"

    def _grid_center(self) -> Tuple[int,int]:
        return self.noise.cfg.rows // 2, self.noise.cfg.cols // 2

    def _mark_block_ahead_on_fail(self, act: str):
        r, c = self._grid_center()
        dr = -1 if act == "up" else (1 if act == "down" else 0)
        dc = -1 if act == "left" else (1 if act == "right" else 0)
        tr, tc = r + dr, c + dc
        self.noise.mark_blocked(tr, tc, True)

    def _detect_interaction(self) -> bool:
        """
        Stub: devolver True si se percibe que A produjo algo (por ejemplo, se abrió diálogo).
        Conectar después a lectura de estado/UI del juego.
        """
        return False

    def _detect_interest_kind(self) -> Optional[str]:
        """
        Stub: devolver 'shop'|'item'|'heal' si se detecta un sitio de interés.
        Conectar a detección de tile/NPC/banderas del mapa cuando esté disponible.
        """
        return None

    def step(self):
        pos_before = self.read_position()
        act = self.choose_action(pos_before)

        # liberar botones
        for b in ["up","down","left","right","a","b"]:
            self.pyboy.button_release(b)

        moved = False
        try:
            self.pyboy.button_press(act)
        except Exception as e:
            if self.logs % (self.log_freq * 10) == 0:
                log_msg("error", "explorer.action_execution_error", action=act, error=str(e))

        pos_after = self.read_position()
        moved = (pos_after != pos_before)

        # actualizar mapa
        self.noise.decay_all()
        r, c = self._grid_center()
        if moved and act in ("up","down","left","right"):
            self.noise.add_visit(r, c)
        elif act == "a":
            # probar interacción en la celda actual
            if self._detect_interaction():
                self.noise.add_interact(r, c)
                kind = self._detect_interest_kind()
                if kind:
                    self.noise.set_interest(r, c, kind)

        # bloqueo si intentó moverse y no cambió posición por 2 ticks
        if act in ("up","down","left","right"):
            if not moved:
                self._stay_ticks += 1
                if self._stay_ticks >= 2:
                    self._mark_block_ahead_on_fail(act)
            else:
                self._stay_ticks = 0

        # contadores y log
        self.visits[pos_after] = self.visits.get(pos_after, 0) + 1
        self.logs += 1
        if self.logs % self.log_freq == 0:
            log_msg("info", "explorer.step_summary",
                    position=pos_after, total_steps=self.logs,
                    unique_positions=len(self.visits), stuck=self.stuck)

    # API para UI/otros agentes
    def get_noise_grayscale(self):
        return self.noise.to_grayscale_u8()

    def get_stats(self) -> Dict[str, Any]:
        return {
            "visited_positions": len(self.visits),
            "total_steps": sum(self.visits.values()),
            "current_position": self.last_pos,
            "stuck": self.stuck
        }