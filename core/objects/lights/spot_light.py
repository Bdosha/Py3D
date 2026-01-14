"""
Источники света для 3D движка Py3D.

Реализует точечные направленные источники света с затуханием
по расстоянию и ограниченным углом освещения.
"""

import numpy as np

from core.objects.lights.base_light import BaseLight
from core.tools.types import Polygon, Color
from core.tools import constants
from core.tools.constants import (
    DEFAULT_POSITION,
    DEFAULT_DIRECTION,
    DEFAULT_COLOR,
    DEFAULT_LIGHT_FOV,
)
from core.tools.utils import to_radians, set_ort, get_cos, get_len


class SpotLight(BaseLight):
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
            fov: float = DEFAULT_LIGHT_FOV,
            power: float = 10
    ) -> None:
        """
        Создаёт источник света.
        
        Args:
            position: Позиция источника в мировых координатах.
            direction: Направление света (будет нормализовано).
            fov: Угол конуса света в градусах.
            power: Мощность света (минимум MIN_LIGHT_POWER).
        """

        super().__init__(
            position=position,
            direction=direction,
            color=color,
            power=power,
        )
        self.fov: float = fov

    @property
    def fov(self) -> float:
        return np.arccos(self._half_fov_cos * 2)

    @fov.setter
    def fov(self, fov: float) -> None:
        fov = np.clip(fov, 10, 90)
        self._half_fov_cos = np.cos(to_radians(fov / 2))

    def get_light_color(self, polygon: Polygon) -> Color:
        """
        Вычисляет интенсивность освещения для полигона.

        Учитывает:
        - Угол между нормалью полигона и направлением к свету
        - Расстояние от источника до полигона
        - Угол относительно направления источника (FOV)

        Args:
            polygon: Треугольник (массив 3x3 вершин).

        Returns:
            Интенсивность освещения в диапазоне [0, 1].
        """
        a, b, c = polygon[0]
        center = (a + b + c) / 3

        # Нормаль полигона
        normal = set_ort(np.cross(b - a, c - a))

        # Направление от источника к центру полигона
        to_poly = set_ort(center - self.position)

        # Базовая интенсивность: косинус угла между нормалью и направлением к свету
        intensity = np.dot(normal, to_poly)

        # Проверяем, находится ли полигон в конусе света
        cos_to_poly = np.clip(get_cos(to_poly, self.direction), -1, 1)
        if cos_to_poly < self._half_fov_cos:
            # Вне основного конуса - затухание по углу
            intensity = intensity - 2 * (self._half_fov_cos - cos_to_poly) * 10

        # Затухание по расстоянию
        distance = get_len(center - self.position)
        falloff = self._power / distance * constants.LIGHT_FALLOFF_MULTIPLIER

        # Итоговая интенсивность (не меньше 0)
        return max(0.0, intensity * falloff) * self.color * polygon[1] / 255.0
