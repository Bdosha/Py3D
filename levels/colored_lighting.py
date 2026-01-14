import core
from core import obj
import numpy as np
import time

from core.app import RenderScript, App, Settings


class RollingScript(RenderScript):
    def __init__(self,
                 radius=1.0,
                 center_y=0.0,
                 rotation_speed=0.6
                 ):

        self.radius = radius  # Радиус круга
        self.center_y = center_y  # Высота центра вращения
        self.rotation_speed = rotation_speed  # Скорость вращения (радиан в секунду)
        self._start_time = None

        self.rgb_lights = None
        self.ground = None

    def init(self, scene: core.Scene):
        self.rgb_lights = [
            core.SpotLight(color=(255, 0, 0)),
            core.SpotLight(color=(0, 255, 0)),
            core.SpotLight(color=(0, 0, 255)),
        ]

        for light in self.rgb_lights:
            scene.lights.append(light)

        self.ground = obj.Surface(
            position=(0, 7, 0),
            details=9,
            direction=(90, 0, 0),
            side=10,
        )
        scene.objects.append(self.ground)

    def run(self, scene: core.Scene):

        # Инициализация времени при первом вызове
        if self._start_time is None:
            self._start_time = time.time()

        # Проверяем, что есть 3 источника света
        if len(self.rgb_lights) != 3:
            return

        current_time = time.time()
        elapsed = current_time - self._start_time

        base_angle = elapsed * self.rotation_speed

        triangle_angles = [0, 2 * np.pi / 3, 4 * np.pi / 3]

        for i, light in enumerate(self.rgb_lights):
            angle = base_angle + triangle_angles[i]

            x = self.radius * np.cos(angle)
            z = self.radius * np.sin(angle)

            light.position = (x, self.center_y, z)


def colored_lighting():
    """Точка входа в приложение."""
    # Создаём сцену

    return App(
        player=core.Player(
            position=(0, -14, 0),
            direction=(0, 1, 0)
        ),
        settings=Settings(bg_color='aqua'),
        render_script=RollingScript())


if __name__ == "__main__":
    app = colored_lighting()
    app.run()
