"""
Источники света для 3D движка Py3D.

Реализует точечные направленные источники света с затуханием
по расстоянию и ограниченным углом освещения.
"""

import numpy as np

from core import Object
from core.tools.types import Polygon, Color, Vector3
from core.tools.constants import (
    DEFAULT_POSITION,
    DEFAULT_DIRECTION,
    DEFAULT_FOV,
    LIGHT_POWER_DIVISOR, DEFAULT_COLOR
)
from core.tools import constants
from core.tools.utils import to_radians, set_ort, get_angle, get_len


class Light(Object):
    """
    Направленный точечный источник света.
    
    Освещает объекты в пределах конуса с заданным углом (FOV).
    Интенсивность затухает с расстоянием.
    
    Attributes:
        position: Позиция источника света.
        direction: Направление света (нормализованное).
        FOV: Угол конуса света в радианах.
        power: Мощность света (влияет на яркость и затухание).
    """

    def __init__(
            self,
            position: tuple[float, float, float] = DEFAULT_POSITION,
            direction: tuple[float, float, float] = DEFAULT_DIRECTION,
            color: tuple[float, float, float] = DEFAULT_COLOR,
            fov: float = DEFAULT_FOV,
            power: float = 10.0
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
            color=color
        )
        self.FOV: float = to_radians(fov)
        # Нормализуем мощность с минимальным порогом
        self.power: float = max(constants.MIN_LIGHT_POWER, power) / LIGHT_POWER_DIVISOR
        self._moved = True

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
        angle_to_poly = get_angle(to_poly, self.direction)
        if angle_to_poly > self.FOV / 2:
            # Вне основного конуса - затухание по углу
            intensity = (intensity / angle_to_poly * self.FOV/2) ** self.power

        # Затухание по расстоянию
        distance = get_len(center - self.position)
        falloff = (self.power * constants.LIGHT_FALLOFF_MULTIPLIER) / distance

        # Итоговая интенсивность (не меньше 0)
        return max(0.0, intensity * falloff) * self.color * polygon[1] / 255.0

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
