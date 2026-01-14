"""
Источники света для 3D движка Py3D.

Реализует точечные направленные источники света с затуханием
по расстоянию и ограниченным углом освещения.
"""
import abc
from abc import ABC

import numpy as np

from core import Object
from core.tools.types import Polygon, Color, Vector3
from core.tools.constants import (
    DEFAULT_POSITION,
    DEFAULT_DIRECTION,
    DEFAULT_COLOR,
)
from core.tools import constants
from core.tools.utils import set_ort, get_len


class BaseLight(Object, ABC):
    """
    Направленный точечный источник света.

    Освещает объекты в пределах конуса с заданным углом (FOV).
    Интенсивность затухает с расстоянием.

    Attributes:
        position: Позиция источника света.
        direction: Направление света (нормализованное).
        _half_fov_cos: Угол конуса света в радианах.
        _power: Мощность света (влияет на яркость и затухание).
    """

    def __init__(
            self,
            position: tuple[float, float, float] = DEFAULT_POSITION,
            direction: tuple[float, float, float] = DEFAULT_DIRECTION,
            color: tuple[float, float, float] = DEFAULT_COLOR,
            power: float = 10
    ) -> None:
        """
        Создаёт источник света.

        Args:
            position: Позиция источника в мировых координатах.
            direction: Направление света (будет нормализовано).
            power: Мощность света (минимум MIN_LIGHT_POWER).
        """

        super().__init__(
            position=position,
            direction=direction,
            color=color
        )

        # Нормализуем мощность с минимальным порогом
        self._power: float = max(constants.MIN_LIGHT_POWER, power)
        self._moved = True

    @abc.abstractmethod
    def get_light_color(self, polygon: Polygon) -> Color:
        """
        Вычисляет интенсивность освещения для полигона.

        Args:
            polygon: Треугольник (массив 3x3 вершин).

        Returns:
            Цвет полигона смешанный со светом
        """

    def set_moved(self, moved: bool) -> None:
        """
        Устанавливает флаг движения источника света.

        Args:
            moved: True если источник света двигался.
        """
        self._moved = moved

    @property
    def direction(self) -> Vector3:
        """
        Направление света (нормализованный вектор).

        Это не углы Эйлера, а вектор направления в 3D пространстве.
        """
        return self._direction

    @direction.setter
    def direction(self, value: tuple[float, float, float] | Vector3):
        """
        Устанавливает направление света.

        Вектор автоматически нормализуется. Если вектор нулевой,
        используется направление по умолчанию.

        Args:
            value: Вектор направления (будет нормализован).
        """
        direction_arr = np.array(value, dtype=np.float32)

        # Защита от нулевого направления
        length = get_len(direction_arr)
        if length < 1e-6:
            direction_arr = np.array(DEFAULT_DIRECTION, dtype=np.float32)

        # Нормализуем вектор
        new = set_ort(direction_arr)

        # Проверяем, изменилось ли направление
        self._moved = not np.array_equal(new, self._direction)
        self._direction = new

        # Инвалидируем кэш освещения при изменении направления
        if self._moved:
            self.invalidate_lighting_cache()
            # Помечаем свет как перемещенный для пересчета освещения всех объектов
            self.set_moved(True)

    def _generate_polygons(self) -> list[Polygon]:
        return []
