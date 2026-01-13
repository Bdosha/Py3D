from typing import Callable
from abc import ABC, abstractmethod

from core import Scene


class RenderScript(ABC):
    @abstractmethod
    def init(self, scene: Scene):
        """Метод будет выполняться в инициализации сцены, тут можно получить данные для сцены и реализации функционала"""

    @abstractmethod
    def run(self, scene: Scene):
        """Этот метод будет выполняться каждый кадр при вызове render в классе Scene.
        Может использовать любые публичные методы и поля сцены.

        Изменение сцены, ее объектов, размеров состояний и так далее"""


class App:
    def __init__(self,
                 scene: Scene,
                 render_script: RenderScript = None
                 ):
        self.scene = scene
        self.render_script = render_script

        self.render_script.init(self.scene)

    def run(self):
        while True:
            self.render_script.run(self.scene)

            self.scene.render()
