from typing import override, Callable

import numpy as np

from core import Object, Vector3, Scene
from core.scripts.base_script import AppScript
from core.tools.utils import get_len


class StateMoveScript(AppScript):
    def __init__(self,
                 obj: Object,
                 speed: float = 1,
                 final_position: Vector3 = None,
                 final_direction: Vector3 = None,
                 final_scaling: Vector3 = None,
                 destroy: bool = False,
                 ):
        self.obj: Object = obj
        self.destroy = destroy

        speed = abs(speed)
        speed /= 10

        self.pos_steps = 0
        if final_position is not None:
            self.pos_vector = final_position - obj.position
            self.pos_steps: int = int(get_len(self.pos_vector)) / speed
            if self.pos_steps != 0:
                self.pos_vector /= self.pos_steps

        self.dir_steps = 0
        if final_direction is not None:
            self.dir_vector = final_direction - obj.direction
            self.dir_steps: int = int(get_len(self.dir_vector)) / speed / 10
            if self.dir_steps != 0:
                self.dir_vector /= self.dir_steps

        self.scale_steps = 0
        if final_scaling is not None:
            self.scale_vector = final_scaling - obj.scaling
            self.scale_steps: int = int(get_len(self.scale_vector)) / speed
            if self.scale_steps != 0:
                self.scale_vector /= self.scale_steps

        self._is_ended = False

    @property
    def is_ended(self) -> bool:
        return self._is_ended

    @override
    def init(self,
             scene: Scene,
             root_bind_func: Callable[[str, Callable], None] = None):
        pass

    @override
    def run(self, scene: Scene):
        if self._is_ended:
            return
        moved = False
        if self.pos_steps > 0:
            self.obj.position = self.obj.position + self.pos_vector
            self.pos_steps -= 1
            moved = True

        if self.dir_steps > 0:
            self.obj.direction = self.obj.direction + self.dir_vector
            self.dir_steps -= 1
            moved = True

        if self.scale_steps > 0:
            self.obj.scaling = self.obj.scaling + self.scale_vector
            self.scale_steps -= 1
            moved = True

        if not moved:
            self._is_ended = True
            if self.destroy:
                self.obj.destroy()


class DeltaMoveScript(StateMoveScript):
    def __init__(self,
                 obj: Object,
                 speed: float = 1,
                 position_delta: Vector3 = None,
                 direction_delta: Vector3 = None,
                 scaling_delta: Vector3 = None,
                 destroy: bool = False,
                 ):

        if position_delta is None:
            position_delta = np.array((0, 0, 0))
        if direction_delta is None:
            direction_delta = np.array((0, 0, 0))
        if scaling_delta is None:
            scaling_delta = np.array((0, 0, 0))

        super().__init__(
            obj,
            speed,
            obj.position + position_delta,
            obj.direction + direction_delta,
            obj.scaling + scaling_delta,
            destroy
        )
