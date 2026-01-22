from typing import Callable, override

import core
from core import obj, Scene
from core.app import AppScript, App


class BottleScript(AppScript):
    def __init__(self):
        self.bottle = None
        self._i = 0

    @override
    def init(self, scene: Scene, root_bind_func: Callable[[str, Callable], None] = None):
        self.bottle = obj.Model(
            model_path="levels/feature/scene.gltf",
            position=(0.1, 20, 0),
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

    return App(
        app_scripts=[BottleScript()]
    )
