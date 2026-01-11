"""
Куб - базовый геометрический примитив.

Генерирует куб с заданным размером стороны и детализацией.
Каждая грань разбивается на сетку треугольников.
"""

import numpy as np

from core.object import Object
from core.utils import swap, to_new_system
from core.types import Color, Polygon, Triangle
from core.constants import DEFAULT_COLOR, DEFAULT_POSITION, DEFAULT_ROTATION, DEFAULT_SCALING


class Cube(Object):
    """
    Куб с настраиваемым размером и детализацией.
    
    Attributes:
        side: Длина стороны куба.
        details: Уровень детализации (количество сегментов на грань).
    """

    def __init__(
            self,
            position: tuple[float, float, float] = DEFAULT_POSITION,
            side: float = 10,
            direction: tuple[float, float, float] = DEFAULT_ROTATION,
            details: int = 1,
            scaling: tuple[float, float, float] = DEFAULT_SCALING,
            color: Color = DEFAULT_COLOR,
            inverted: bool = False
    ) -> None:
        """
        Создаёт куб.
        
        Args:
            position: Позиция центра куба в мировых координатах.
            side: Длина стороны куба.
            direction: Углы поворота в градусах (rx, ry, rz).
            details: Уровень детализации (1 = 2 треугольника на грань).
            scaling: Масштаб по осям.
            color: RGB цвет куба.
            inverted: Если True, нормали направлены внутрь (для скайбокса).
        """
        self.side = side
        self.details = details + 1  # +1 для корректного разбиения

        super().__init__(
            position=position,
            direction=direction,
            scaling=scaling,
            color=color,
            inverted=inverted
        )

    @staticmethod
    def rotate_to(vertices: Triangle, direction: tuple[float, float, float]) -> Triangle:
        """
        Поворачивает вершины на заданные углы.

        Args:
            vertices: Массив вершин для поворота.
            rotate: Углы поворота в градусах (rx, ry, rz).

        Returns:
            Массив повёрнутых вершин.
        """
        return to_new_system(direction, vertices)

    def _generate_polygons(self) -> list[Polygon]:
        """
        Генерирует полигоны куба.
        
        Создаёт 6 граней, каждая разбивается на сетку треугольников
        в соответствии с уровнем детализации.
        """
        half_side = self.side / 2
        divisions = np.linspace(-half_side, half_side, self.details)

        created_polygons: list[Polygon] = []
        for i in range(1, self.details):
            for j in range(1, self.details):
                # Координаты текущей ячейки сетки
                x0, x1 = divisions[i - 1], divisions[i]
                y0, y1 = divisions[j - 1], divisions[j]

                # Первый треугольник ячейки (верхняя грань Z+)
                tri1 = np.array([
                    [x0, y0, half_side],
                    [x0, y1, half_side],
                    [x1, y0, half_side]
                ], dtype=np.float32)

                # Второй треугольник ячейки (верхняя грань Z+)
                tri2 = np.array([
                    [x1, y1, half_side],
                    [x1, y0, half_side],
                    [x0, y1, half_side]
                ], dtype=np.float32)

                # Верхняя грань (Z+)
                created_polygons.append((tri1.copy(), self.color))
                created_polygons.append((tri2.copy(), self.color))

                # Нижняя грань (Z-) - инвертированная верхняя
                created_polygons.append((-swap(tri1), self.color))
                created_polygons.append((-swap(tri2), self.color))

                # Боковые грани через поворот базовых треугольников
                # Грань Y+ (поворот на 90° вокруг X)
                created_polygons.append((Cube.rotate_to(tri1, (90, 0, 0)), self.color))
                created_polygons.append((Cube.rotate_to(tri2, (90, 0, 0)), self.color))

                # Грань Y- (поворот на -90° вокруг X)
                created_polygons.append((Cube.rotate_to(tri1, (-90, 0, 0)), self.color))
                created_polygons.append((Cube.rotate_to(tri2, (-90, 0, 0)), self.color))

                # Грань X+ (поворот на 90° вокруг Y)
                created_polygons.append((Cube.rotate_to(tri1, (0, 90, 0)), self.color))
                created_polygons.append((Cube.rotate_to(tri2, (0, 90, 0)), self.color))

                # Грань X- (поворот на -90° вокруг Y)
                created_polygons.append((Cube.rotate_to(tri1, (0, -90, 0)), self.color))
                created_polygons.append((Cube.rotate_to(tri2, (0, -90, 0)), self.color))

        return created_polygons
