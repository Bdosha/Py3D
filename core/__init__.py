"""
Ядро 3D движка Py3D.

Содержит основные компоненты для рендеринга:
- Camera: проекция 3D на 2D, отсечение невидимых полигонов
- BaseLight, SpotLight, PointLight: источники освещения
- Object: базовый класс объектов
- Scene: управление сценой и рендеринг
- Screen: вывод на экран через tkinter
- App: обёртка для работы со скриптами
- Editor: GUI редактор сцены
"""

from core.tools.types import Vector3, Vector2, Triangle, Color, Polygon
from core.objects.object import Object
from core.objects.camera import Camera
from core.objects.lights import BaseLight, SpotLight, PointLight
from .scene import Scene
from .screen import Screen
from core.tools.editor import Editor
from core.tools.constants import *
import core.objects as obj
from core.app import App

__all__ = [
    'Camera',
    'BaseLight',
    'SpotLight',
    'PointLight',
    'Object',
    'Scene',
    'Screen',
    'Vector3',
    'Vector2',
    'Triangle',
    'Color',
    'Polygon',
    'App',
    'Editor',
]
