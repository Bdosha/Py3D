"""
Ядро 3D движка Py3D.

Содержит основные компоненты для рендеринга:
- Camera: проекция 3D на 2D
- Light: источники освещения
- Object: базовый класс объектов
- Player: управление игроком
- Scene: управление сценой и рендеринг
- Screen: вывод на экран через tkinter
"""

from .camera import Camera
from .light import Light
from .object import Object
from .scene import Scene
from .screen import Screen
from .player import Player
from .constants import *
from .types import Vector3, Vector2, Triangle, Color, Polygon

__all__ = [
    'Camera',
    'Light',
    'Object',
    'Scene',
    'Screen',
    'Player',
    'Vector3',
    'Vector2',
    'Triangle',
    'Color',
    'Polygon',
]
