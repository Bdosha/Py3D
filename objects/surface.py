"""
Плоская поверхность (плоскость).

Генерирует прямоугольную плоскость с настраиваемой детализацией.
Может быть односторонней или двусторонней.
"""

import numpy as np

from core.object import Object
from core.utils import swap
from core.types import Color
from core.constants import DEFAULT_COLOR, DEFAULT_POSITION, DEFAULT_ROTATION, DEFAULT_SCALING


class Surface(Object):
    """
    Плоская прямоугольная поверхность.
    
    Разбивается на сетку треугольников в соответствии с детализацией.
    
    Attributes:
        side: Длина стороны квадратной поверхности.
        details: Количество сегментов разбиения.
        double_sided: Если True, поверхность видна с обеих сторон.
    """
    
    def __init__(
        self,
        position: tuple[float, float, float] = DEFAULT_POSITION,
        side: float = 10,
        rotate: tuple[float, float, float] = DEFAULT_ROTATION,
        details: int = 1,
        scaling: tuple[float, float, float] = DEFAULT_SCALING,
        color: Color = DEFAULT_COLOR,
        double_sided: bool = False,
        inverted: bool = False
    ) -> None:
        """
        Создаёт плоскую поверхность.
        
        Args:
            position: Позиция центра поверхности.
            side: Длина стороны (поверхность квадратная).
            rotate: Углы поворота в градусах.
            details: Уровень детализации сетки.
            scaling: Масштаб по осям.
            color: RGB цвет поверхности.
            double_sided: Если True, создаёт полигоны с обеих сторон.
            inverted: Если True, инвертирует нормали.
        """
        self.side = side
        self.details = details
        self.double_sided = double_sided
        
        super().__init__(
            position=position,
            rotate=rotate,
            scaling=scaling,
            color=color,
            inverted=inverted
        )
    
    def _generate_polys(self) -> None:
        """
        Генерирует полигоны поверхности.
        
        Создаёт сетку треугольников на плоскости Z=0.
        При double_sided=True добавляет зеркальные треугольники.
        """
        half_side = self.side / 2
        divisions = np.linspace(-half_side, half_side, self.details)
        
        for i in range(1, self.details):
            for j in range(1, self.details):
                # Координаты текущей ячейки
                x0, x1 = divisions[i - 1], divisions[i]
                y0, y1 = divisions[j - 1], divisions[j]
                
                # Первый треугольник ячейки
                tri1 = np.array([
                    [x0, y0, 0],
                    [x1, y0, 0],
                    [x0, y1, 0]
                ], dtype=np.float32)
                
                # Второй треугольник ячейки
                tri2 = np.array([
                    [x1, y1, 0],
                    [x0, y1, 0],
                    [x1, y0, 0]
                ], dtype=np.float32)
                
                # Лицевая сторона
                self.polys.append((tri1.copy(), self.color))
                self.polys.append((tri2.copy(), self.color))
                
                # Обратная сторона (если двусторонняя)
                if self.double_sided:
                    self.polys.append((-swap(tri1), self.color))
                    self.polys.append((-swap(tri2), self.color))
