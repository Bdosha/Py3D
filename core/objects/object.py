"""
Базовый класс для всех 3D объектов в движке Py3D.

Определяет абстрактный интерфейс и общую логику трансформаций
для всех геометрических примитивов и моделей.
"""
import uuid
from typing import Optional
from abc import ABC, abstractmethod
import numpy as np

from core.tools.types import Vector3, Color, Polygon
from core.tools.constants import (
    DEFAULT_POSITION,
    DEFAULT_ROTATION,
    DEFAULT_SCALING,
    DEFAULT_COLOR,
    EPSILON
)
from core.tools.utils import to_new_system, swap


class Object(ABC):
    """
    Абстрактный базовый класс для всех 3D объектов.
    
    Предоставляет общую функциональность для позиционирования,
    вращения, масштабирования и инверсии объектов.
    
    Attributes:
        position: Позиция объекта в мировых координатах (x, y, z).
        direction: Углы поворота в градусах (rx, ry, rz) - углы Эйлера.
        scaling: Масштаб объекта по осям X, Y, Z.
        _inverted: Флаг инверсии нормалей (для внутренних поверхностей).
        color: Базовый цвет объекта.
        polygons: Список полигонов объекта с цветами.
    """

    _position: Vector3
    _direction: Vector3
    _scaling: Vector3

    _inverted: bool

    def __init__(
            self,
            position: tuple[float, float, float] = DEFAULT_POSITION,
            direction: tuple[float, float, float] = DEFAULT_ROTATION,
            scaling: tuple[float, float, float] = DEFAULT_SCALING,
            color: tuple[float, float, float] = DEFAULT_COLOR,
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

        self._id = uuid.uuid4()

        self._position = DEFAULT_POSITION
        self._direction = DEFAULT_ROTATION
        self._scaling = DEFAULT_SCALING

        self.position = position
        self.direction = direction
        self.scaling = scaling

        self._transformed_polygons: list[Polygon] = []
        self._moved: bool = False

        # Буфер для освещенных цветов
        self._lighting_colors: Optional[list[Color]] = None
        self._lighting_cache_valid: bool = False

        self.color: Color = np.array(color)
        self._inverted: bool = inverted

        self._raw_polygons: list[Polygon] = self._generate_polygons()

        if self._inverted:
            for poly, color in self._raw_polygons:
                poly[1], poly[2] = poly[2].copy(), poly[1].copy()

        self._far_point = 0
        if self._raw_polygons:
            all_points = np.vstack([i[0] for i in self._raw_polygons])
            distances = np.linalg.norm(all_points, axis=1)
            max_idx = np.argmax(distances)

            self._far_point = all_points[max_idx]

    @property
    def id(self) -> str:
        return str(self._id)

    @property
    def max_far_point(self) -> Vector3:
        return self._far_point

    @property
    def position(self) -> Vector3:
        return self._position

    @property
    def direction(self) -> Vector3:
        """
        Углы поворота объекта в градусах (rx, ry, rz).
        
        Это углы Эйлера, которые используются для создания матрицы поворота.
        Значения в градусах, не в радианах.
        """
        return self._direction

    @property
    def scaling(self) -> Vector3:
        return self._scaling

    @property
    def is_moved(self) -> bool:
        return self._moved

    @property
    def polygons(self) -> list[Polygon]:
        if self._moved or not self._transformed_polygons:
            self._transformed_polygons: list[Polygon] = []
            for poly, color in self._raw_polygons:
                self._transformed_polygons.append((to_new_system(
                    poly * self.scaling,
                    self.direction,
                    self.position), color))
            self._moved = False

        return self._transformed_polygons

    @position.setter
    def position(self, value: tuple[float, float, float]):
        new = np.array(value, dtype=np.float32)
        self._moved = not np.array_equal(new, self._position)
        self._position: Vector3 = new
        if self._moved:
            self.invalidate_lighting_cache()

    @direction.setter
    def direction(self, value: tuple[float, float, float]):
        """
        Устанавливает углы поворота объекта.
        
        Args:
            value: Углы поворота в градусах (rx, ry, rz) - углы Эйлера.
        """
        new = np.array(value, dtype=np.float32)
        self._moved = not np.array_equal(new, self._direction)
        self._direction: Vector3 = new
        if self._moved:
            self.invalidate_lighting_cache()

    @scaling.setter
    def scaling(self, value: tuple[float, float, float]):
        new = np.array(value, dtype=np.float32) + EPSILON
        self._moved = not np.array_equal(new, self._scaling)
        self._scaling: Vector3 = new
        if self._moved:
            self.invalidate_lighting_cache()

    def update_coloring(self, colors: list[Color]):
        """
        Обновляет цвета полигонов.
        
        Args:
            colors: Список цветов для каждого полигона.
        """
        if not colors:
            return
        
        if len(colors) != len(self._transformed_polygons):
            raise ValueError(
                f"Количество цветов ({len(colors)}) не совпадает с "
                f"количеством полигонов ({len(self._transformed_polygons)})"
            )
        
        self._transformed_polygons = [(poly[0], colors[i]) for i, poly in enumerate(self._transformed_polygons)]
    
    def set_lighting_colors(self, colors: list[Color]) -> None:
        """
        Устанавливает освещенные цвета для полигонов.
        
        Args:
            colors: Список освещенных цветов для каждого полигона.
        """
        if not colors:
            self._lighting_colors = None
            self._lighting_cache_valid = False
            return
        
        if len(colors) != len(self.polygons):
            raise ValueError(
                f"Количество цветов ({len(colors)}) не совпадает с "
                f"количеством полигонов ({len(self.polygons)})"
            )
        
        self._lighting_colors = colors
        self._lighting_cache_valid = True
    
    def get_lighted_polygons(self) -> list[Polygon]:
        """
        Возвращает полигоны с освещенными цветами.
        
        Если освещенные цвета не установлены, возвращает полигоны
        с базовыми цветами.
        
        Returns:
            Список полигонов с цветами (освещенными или базовыми).
        """
        polygons = self.polygons
        
        if self._lighting_colors is not None and self._lighting_cache_valid:
            # Возвращаем полигоны с освещенными цветами
            return [(poly[0], self._lighting_colors[i]) for i, poly in enumerate(polygons)]
        else:
            # Возвращаем полигоны с базовыми цветами
            return polygons
    
    def invalidate_lighting_cache(self) -> None:
        """Инвалидирует кэш освещения объекта."""
        self._lighting_cache_valid = False
        self._lighting_colors = None

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
