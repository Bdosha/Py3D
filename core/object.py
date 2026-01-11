"""
Базовый класс для всех 3D объектов в движке Py3D.

Определяет абстрактный интерфейс и общую логику трансформаций
для всех геометрических примитивов и моделей.
"""

from abc import ABC, abstractmethod
import numpy as np

from .types import Vector3, Color, Polygon, VisibilityCheck
from .constants import (
    DEFAULT_POSITION,
    DEFAULT_ROTATION,
    DEFAULT_SCALING,
    DEFAULT_COLOR,
    EPSILON
)
from .utils import to_new_system, swap


class Object(ABC):
    """
    Абстрактный базовый класс для всех 3D объектов.
    
    Предоставляет общую функциональность для позиционирования,
    вращения, масштабирования и инверсии объектов.
    
    Attributes:
        position: Позиция объекта в мировых координатах.
        scaling: Масштаб объекта по осям X, Y, Z.
        is_inverted: Флаг инверсии нормалей (для внутренних поверхностей).
        color: Базовый цвет объекта.
        polygons: Список полигонов объекта с цветами.
        Mx, My, Mz: Матрицы поворота вокруг осей X, Y, Z.
    """

    def __init__(
            self,
            position: tuple[float, float, float] = DEFAULT_POSITION,
            direction: tuple[float, float, float] = DEFAULT_ROTATION,
            scaling: tuple[float, float, float] = DEFAULT_SCALING,
            color: Color = DEFAULT_COLOR,
            inverted: bool = False
    ) -> None:
        """
        Инициализирует базовые параметры объекта.
        
        Args:
            position: Позиция объекта в мировых координатах (x, y, z).
            direction: Углы поворота в градусах (rx, ry, rz).
            scaling: Масштаб по осям (sx, sy, sz).
            color: RGB цвет объекта (r, g, b), значения 0-255.
            inverted: Если True, нормали полигонов направлены внутрь.
        """
        self.position: Vector3 = np.array(position, dtype=np.float32)
        self.direction: Vector3 = np.array(direction, dtype=np.float32)

        # self.Mx, self.My, self.Mz = create_matrix(direction)

        self.scaling: Vector3 = np.array(scaling, dtype=np.float32) + EPSILON

        self.color: Color = color
        self.is_inverted: bool = inverted
        self.polygons: list[Polygon] = self._apply_polygons()

    @abstractmethod
    def _generate_polygons(self) -> list[Polygon]:
        """
        Генерирует полигоны объекта.
        
        Этот метод должен быть реализован в каждом дочернем классе.
        Должен вернуть список кортежей (triangle, color).
        """
        pass

    @staticmethod
    def _apply_inversion(polygons: list[Polygon]) -> list[Polygon]:
        """
        Инвертирует нормали всех полигонов.

        Меняет порядок вершин в треугольниках для изменения
        направления нормалей (используется для внутренних поверхностей).
        """
        inverted_polys = []
        for poly, color in polygons:
            inverted_polys.append((swap(poly), color))
        return inverted_polys

    def _apply_polygons(self):
        temp_polygons = self._generate_polygons()
        if self.is_inverted:
            temp_polygons = Object._apply_inversion(temp_polygons)

        return temp_polygons

    def get_visible_polys(self, visibility_check: VisibilityCheck) -> list[Polygon]:
        """
        Возвращает список видимых полигонов.
        
        Фильтрует полигоны по функции проверки видимости
        (frustum culling, backface culling).
        
        Args:
            visibility_check: Функция проверки видимости полигона.
            
        Returns:
            Список видимых полигонов с цветами.
        """
        visible = []
        for poly, color in self.polygons:

            transformed = to_new_system(self.direction,
                                        poly * self.scaling,
                                        self.position)

            if visibility_check(transformed):
                visible.append((transformed, color))
        return visible
