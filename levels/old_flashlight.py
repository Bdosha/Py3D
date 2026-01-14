import core
from core import obj, Scene
from core.app import RenderScript, App


class FlashlightScript(RenderScript):
    def __init__(self,
                 fov=15,
                 power=5
                 ):
        self.fov = fov
        self.power = power

        self.flashlight = None
        self.skybox = None

    def init(self, scene: Scene):
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
        self.flashlight.position = scene.player.position
        self.flashlight.direction = scene.player.direction


def flashlight_demo():
    """Точка входа в приложение."""

    # Создаём игрока (камеру от первого лица)
    player = core.Player(
        position=(0, 2, 0),
        direction=(0, 1, 0)
    )

    return App(
        player=player,
        render_script=FlashlightScript()
    )
