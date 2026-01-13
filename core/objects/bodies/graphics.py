"""
Графики и параметрические поверхности.

Содержит классы для визуализации:
- Graphic: график функции z = f(x, y)
- ParametricSurface: параметрические поверхности (тор, спираль и т.д.)
"""

import numpy as np

from core.object import Object
from core.tools.types import SurfaceFunction, Polygon
from core.tools.constants import DEFAULT_POSITION, DEFAULT_ROTATION, DEFAULT_SCALING
from .load_graphic import load_parametric_surface, load_graphic


class Graphic(Object):
    """
    3D график функции z = f(x, y).
    
    Визуализирует математическую функцию двух переменных как
    поверхность в 3D пространстве.
    
    Цвет полигонов определяется высотой (координатой Z).
    """

    def __init__(
            self,
            position: tuple[float, float, float] = DEFAULT_POSITION,
            direction: tuple[float, float, float] = DEFAULT_ROTATION,
            z_func: SurfaceFunction = None,
            details: int = 20,
            scaling: tuple[float, float, float] = DEFAULT_SCALING,
            inverted: bool = False
    ) -> None:
        """
        Создаёт график функции.
        
        Args:
            position: Позиция центра графика.
            direction: Углы поворота в градусах.
            z_func: Функция z = f(x, y), принимает массивы numpy.
            details: Количество точек разбиения по каждой оси.
            scaling: Масштаб по осям.
            inverted: Если True, инвертирует нормали.
        """
        self.z_func = z_func if z_func is not None else lambda x, y: np.zeros_like(x)
        self.details = details
        self._range = 5  # Диапазон по X и Y: [-range, range]

        super().__init__(
            position=position,
            direction=direction,
            scaling=scaling,
            color=(255, 255, 255),  # Цвет вычисляется динамически
            inverted=inverted
        )

    def _generate_polygons(self) -> list[Polygon]:
        """Генерирует полигоны графика функции."""
        return load_graphic(self.z_func, self.details, self._range)


class ParametricSurface(Object):
    """
    Параметрическая поверхность.
    
    Поддерживает различные типы поверхностей:
    - 0: Спираль (spiral)
    - 1: Лента Мёбиуса (Möbius strip)
    - 2: Тор (torus)
    - 3: Винт (screw)
    - 4: Морская раковина (sea shell)
    
    Цвет определяется высотой точки на поверхности.
    """

    # Константы для типов поверхностей
    SPIRAL = 0
    MOBIUS = 1
    TORUS = 2
    SCREW = 3
    SEA_SHELL = 4

    def __init__(
            self,
            position: tuple[float, float, float] = DEFAULT_POSITION,
            direction: tuple[float, float, float] = DEFAULT_ROTATION,
            surface_type: int = 0,
            details: int = 10,
            scaling: tuple[float, float, float] = DEFAULT_SCALING,
            inverted: bool = False
    ) -> None:
        """
        Создаёт параметрическую поверхность.
        
        Args:
            position: Позиция центра поверхности.
            direction: Углы поворота в градусах.
            surface_type: Тип поверхности (0-4, см. константы класса).
            details: Детализация сетки.
            scaling: Масштаб по осям.
            inverted: Если True, инвертирует нормали.
        """
        self.surface_type = surface_type
        self.details = details

        super().__init__(
            position=position,
            direction=direction,
            scaling=scaling,
            color=(255, 255, 255),  # Цвет вычисляется динамически
            inverted=inverted
        )

    def _generate_polygons(self) -> list[Polygon]:
        """Генерирует полигоны параметрической поверхности."""
        return load_parametric_surface(
            alpha=1,
            beta=1,
            details=self.details,
            surface_type=self.surface_type
        )


# Алиас для обратной совместимости
Lab = ParametricSurface
