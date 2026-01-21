import tkinter
from abc import ABC, abstractmethod
from typing import Callable

from core import Scene


class AppScript(ABC):
    @abstractmethod
    def init(self, scene: Scene, root_bind_func: Callable[[str, Callable], None] = None):
        """Метод будет выполняться в инициализации сцены, тут можно получить данные для сцены и реализации функционала
        Функция root_bind - метод из окна"""

    @abstractmethod
    def run(self, scene: Scene):
        """Этот метод будет выполняться каждый кадр при вызове render в классе Scene.
        Может использовать любые публичные методы и поля сцены.

        Изменение сцены, ее объектов, размеров состояний и так далее"""

    @staticmethod
    def get_empty_script():
        class EmptyScript(AppScript):
            def init(self, scene: Scene,root_bind_func: Callable[[str, Callable], None] = None):
                pass

            def run(self, scene: Scene):
                pass

        return EmptyScript
