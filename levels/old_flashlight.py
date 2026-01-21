from typing import override, Callable

import core
from core import obj, Scene
from core.app import AppScript, App
from core.app_scripts.player_script import PlayerScript


class FlashlightScript(AppScript):
    def __init__(self,
                 fov=15,
                 power=5
                 ):
        self.fov = fov
        self.power = power

        self.flashlight = None
        self.skybox = None

    @override
    def init(self, scene: Scene, root_bind_func: Callable[[str, Callable], None] = None):
        self.flashlight = core.SpotLight(
            fov=self.fov,
            power=self.power,
        )
        scene.lights.append(self.flashlight)
        self.skybox = obj.Cube(
            position=(0.1, 20, 0),
            scaling=(1, 2, 1),
            details=8,
            side=20,
            inverted=True
        )
        scene.objects.append(self.skybox)

    def run(self, scene: Scene):
        self.flashlight.position = scene.camera.position
        self.flashlight.direction = scene.camera.direction


def flashlight_demo():
    """Точка входа в приложение."""

    # Создаём игрока (камеру от первого лица)
    camera = core.Camera(
        position=(0, 2, 0),
        direction=(0, 1, 0)
    )

    return App(
        camera=camera,
        app_scripts=[FlashlightScript(), PlayerScript()]
    )
