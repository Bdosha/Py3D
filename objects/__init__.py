"""
3D объекты для движка Py3D.

Модуль экспортирует все доступные геометрические примитивы
и загрузчики моделей.
"""

from .cube import Cube
from .graphics import Graphic, ParametricSurface, Lab  # Lab - алиас для совместимости
from .model import Model
from .sphere import Sphere
from .surface import Surface

__all__ = [
    'Cube',
    'Graphic',
    'ParametricSurface',
    'Lab',  # Deprecated: используйте ParametricSurface
    'Model',
    'Sphere',
    'Surface',
]
