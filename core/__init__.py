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

from core.tools.types import Vector3, Vector2, Triangle, Color, Polygon
from core.object import Object
from core.objects.camera import Camera
from core.objects.light import Light
from .scene import Scene
from .screen import Screen
from core.objects.player import Player
from core.tools.editor import Editor
from core.tools.constants import *
import core.objects as obj
from core.app import App

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
    'App'
]
