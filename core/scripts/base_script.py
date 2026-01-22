"""
Базовые скрипты для 3D движка Py3D.

Предоставляет систему скриптов для создания динамических сцен
с возможностью обработки событий и обновления объектов каждый кадр.
"""

from abc import ABC, abstractmethod
from typing import Callable

from core import Scene


class AppScript(ABC):
    """
    Базовый класс для скриптов сцены.
    
    Скрипты позволяют создавать динамические сцены с обработкой
    событий клавиатуры/мыши и обновлением объектов каждый кадр.
    """
    
    @abstractmethod
    def init(self, scene: Scene, root_bind_func: Callable[[str, Callable], None] = None):
        """
        Инициализация скрипта при старте приложения.
        
        Выполняется один раз при создании приложения. Здесь можно:
        - Добавить объекты на сцену
        - Привязать обработчики событий клавиатуры/мыши
        - Инициализировать состояние скрипта
        
        Args:
            scene: Сцена для добавления объектов и управления.
            root_bind_func: Функция для привязки обработчиков событий tkinter.
                           Принимает паттерн события (например, "<w>") и обработчик.
        """

    @abstractmethod
    def run(self, scene: Scene):
        """
        Обновление скрипта каждый кадр.
        
        Выполняется каждый кадр перед рендерингом. Здесь можно:
        - Изменять позиции, повороты, масштабы объектов
        - Добавлять/удалять объекты и источники света
        - Обновлять параметры сцены
        
        Args:
            scene: Сцена для доступа к объектам и источникам света.
        """

    @staticmethod
    def get_empty_script():
        class EmptyScript(AppScript):
            def init(self, scene: Scene,root_bind_func: Callable[[str, Callable], None] = None):
                pass

            def run(self, scene: Scene):
                pass

        return EmptyScript
