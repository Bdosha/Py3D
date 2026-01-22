from typing import Callable, override

import core
from core import obj, Scene
from core.app import AppScript, App
from core.scripts.move_script import DeltaMoveScript
from core.scripts.player_script import PlayerScript


class BottleScript(AppScript):
    def __init__(self):
        self.bottle = None
        self._i = 0

    @override
    def init(self, scene: Scene, root_bind_func: Callable[[str, Callable], None] = None):
        self.bottle = obj.Model(
            model_path="levels/scene.gltf",
            position=(0, 20, 0),
            color=(255, 255, 255)
        )
        scene.lights.append(
            core.SpotLight(
                fov=20,
            )
        )

        scene.objects.append(self.bottle)

    def run(self, scene: Scene):
        self.bottle.direction = [self._i] * 3
        self._i += 1


def model_demo():
    """Точка входа в приложение."""
    bottle = obj.Model(
        model_path="levels/feature/scene.gltf",
        position=(5, 20, 0),
        direction=(-90, 0, 0),
    )
    return App(
        objects=[bottle],
        app_scripts=[
            DeltaMoveScript(bottle,
                            speed=0.5,
                            position_delta=(-10, 0, 0),
                            direction_delta=(0, 720, 0)
                            )
        ],
    )
