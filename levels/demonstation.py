from typing import Callable, override

import numpy as np

import core
from core import obj, Scene, Object, PointLight, Camera, BaseLight
from core.app import AppScript, App, Settings
from core.objects import Surface
from core.scripts import DeltaMoveScript, PlayerScript


class DemonstrationScript(AppScript):
    def __init__(self):
        self.bottle = None
        self.bottle_moving_script: DeltaMoveScript = None
        self.bottle_light: BaseLight = None

        self.added_rgb = False
        self.light_scripts: list[DeltaMoveScript] = []

    @override
    def init(self, scene: Scene, root_bind_func: Callable[[str, Callable], None] = None):
        scene.objects.append(
            Surface(
                position=(0, 60, 0),
                direction=(90, 0, 0),
                details=10,
                scaling=(3, 3, 3)
            )
        )

        scene.objects.append(
            obj.Cube(
                position=(0, 50, 5),
                scaling=(0.5, 0.5, 0.5),
                direction=(45, 45, 45),
                color=(200, 255, 30),
            )
        )

        scene.objects.append(
            obj.Sphere(
                position=(10, 50, 5),
                scaling=(0.5, 0.5, 0.5),
                direction=(45, 45, 45),
                color=(250, 20, 200),
            )
        )

        self.bottle = obj.Model(
            model_path="levels/feature/scene.gltf",
            position=(5, 20, 0),
            direction=(-90, 0, 0),
            color=(200, 255, 200),

        )
        self.bottle_moving_script: DeltaMoveScript = DeltaMoveScript(
            self.bottle,
            speed=3,
            position_delta=(0, 38, -2),
            direction_delta=(380, 0, 0),
            destroy=True

        )
        self.bottle_light = PointLight(
            position=self.bottle.position,
            power=0.1
        )
        scene.objects.append(self.bottle)
        scene.lights.append(self.bottle_light)

    def rgb_animation(self, scene: Scene):
        temp = [0, 0, 0]
        dir_deltas = (
            (10, 0, -5),
            (-3, 0, 10),
            (-7, 0, -5)
        )
        for i in range(3):
            t = temp.copy()
            t[i] = 255
            light = PointLight(
                position=(5, 58, 0),
                color=t,
                power=2
            )
            scene.lights.append(light)
            self.light_scripts.append(DeltaMoveScript(
                light,
                position_delta=dir_deltas[i],
                destroy=True

            ))

    @override
    def run(self, scene: Scene):
        if not self.bottle_moving_script.is_ended:
            self.bottle_moving_script.run(scene)
            if not self.bottle_moving_script.is_ended:
                self.bottle_light.position = self.bottle.position + np.array((-1, 0, 2))
                return

        if not self.added_rgb:
            self.bottle_light.destroy()
            self.added_rgb = True
            self.rgb_animation(scene)

        flag = False
        for s in self.light_scripts:
            s.run(scene)
            if not s.is_ended:
                flag = True
        if not flag and self.bottle_light in scene.lights:

            scene.lights.remove(self.bottle_light)
            for s in self.light_scripts:
                scene.lights.remove(s.obj)


def main_demo():
    """Точка входа в приложение."""
    return App(
        camera=Camera(
            position=(-8, 5, -8),
            direction=(1, 5, 1),
        ),
        settings=Settings(
            bg_color="black",

        ),
        lights=[
            PointLight(power=0
                       )
        ],
        app_scripts=[PlayerScript(),

                     DemonstrationScript(),
                     ],
    )
