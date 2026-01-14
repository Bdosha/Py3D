import core
from core import obj, Scene
from core.app import RenderScript, App


class BottleScript(RenderScript):
    def __init__(self):
        self.bottle = None
        self._i = 0

    def init(self, scene: Scene):
        self.bottle = obj.Model(
            model_path="levels/scene.gltf",
            position=(0, 20, 0),
            color=(255, 255, 255)
        )
        scene.lights.append(
            core.Light(
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
        render_script=BottleScript(),
    )
