"""
3D объекты для движка Py3D.

Модуль экспортирует все доступные геометрические примитивы
и загрузчики моделей.
"""

from core.objects.bodies.cube import Cube
from core.objects.bodies.graphics import Graphic, ParametricSurface, Lab  # Lab - алиас для совместимости
from core.objects.bodies.model import Model
from core.objects.bodies.sphere import Sphere
from core.objects.bodies.surface import Surface

__all__ = [
    'Cube',
    'Graphic',
    'ParametricSurface',
    'Lab',  # Deprecated: используйте ParametricSurface
    'Model',
    'Sphere',
    'Surface',
]
