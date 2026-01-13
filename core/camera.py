"""
Камера для 3D движка Py3D.

Обеспечивает проекцию 3D точек на 2D экран и отсечение
невидимых полигонов (frustum culling, backface culling).
"""

import numpy as np

from . import Object, Polygon
from .types import Vector3, Vector2, Triangle, ScreenCoords
from .constants import (
    DEFAULT_FOV,
    DEFAULT_FOCUS,
    DEFAULT_POSITION,
    DEFAULT_DIRECTION,
    MATRIX_REGULARIZATION,
    UP_VECTOR
)
from . import constants
from .utils import to_radians, set_ort, get_angle


class Camera(Object):
    """
    Камера для проекции 3D сцены на 2D экран.
    
    Использует перспективную проекцию с настраиваемым FOV.
    Поддерживает отсечение невидимых полигонов.
    
    Attributes:
        position: Позиция камеры в мировых координатах.
        direction: Нормализованное направление взгляда.
        FOV: Угол обзора в радианах.
        focus: Фокусное расстояние.
        view_dot: Точка фокуса для проекции.
    """
    position: Vector3
    direction: Vector3
    FOV: float
    focus: float
    view_dot: Vector3

    def __init__(
            self,
            position: tuple[float, float, float] = DEFAULT_POSITION,
            direction: tuple[float, float, float] = DEFAULT_DIRECTION,
            fov: float = DEFAULT_FOV
    ) -> None:
        """
        Создаёт камеру.
        
        Args:
            position: Начальная позиция камеры (x, y, z).
            direction: Направление взгляда (будет нормализовано).
            fov: Угол обзора в градусах (обычно 60-120).
        """
        super().__init__(
            position=position,
            direction=direction,
        )

        self.FOV: float = to_radians(180 - DEFAULT_FOV)
        self.focus: float = DEFAULT_FOCUS

        self.set_position(position, direction, fov)

        # Храним обратную матрицу
        self._math_cache: None | np.ndarray = None
        print("@@@@", self._moved)

    def set_position(
            self,
            position: tuple[float, float, float] = DEFAULT_POSITION,
            direction: tuple[float, float, float] = DEFAULT_DIRECTION,
            fov: float = DEFAULT_FOV
    ) -> None:
        """
        Перемещает камеру в новую позицию с новым направлением.
        
        Args:
            position: Новая позиция камеры.
            direction: Новое направление взгляда.
            fov: Новый угол обзора в градусах.
        """
        # Защита от нулевого направления
        if all(d == 0 for d in direction):
            direction = DEFAULT_DIRECTION

        self.FOV = to_radians(180 - fov)
        self.focus = DEFAULT_FOCUS
        self.position = np.array(position, dtype=np.float32)

        self.direction = set_ort(np.array(direction, dtype=np.float32))

        # Вычисляем точку фокуса для проекции
        # view_dot находится перед камерой на расстоянии, зависящем от FOV
        self.view_dot = self.position + self.direction * (self.focus / 2 * np.tan(self.FOV / 2))

    def is_point_visible(self, point: Vector3) -> bool:
        to_vertex = point - self.position
        return get_angle(to_vertex, self.direction) <= self.FOV / 2

    def is_polygon_visible(self, poly: Triangle) -> bool:
        """
        Проверяет видимость полигона.
        
        Выполняет две проверки:
        1. Frustum culling: хотя бы одна вершина в поле зрения камеры
        2. Backface culling: полигон обращён к камере
        
        Args:
            poly: Треугольник (массив 3x3 вершин).
            
        Returns:
            True если полигон видим, False если его можно отсечь.
        """
        a, b, c = poly

        # Вычисляем нормаль для backface culling
        normal = set_ort(np.cross(b - a, c - a))

        # Вектор от камеры к центру (для backface culling)
        center = (a + b + c) / 3
        to_center = center - self.position

        # Backface culling: полигон должен быть обращён к камере
        if np.dot(normal, to_center) < 0:
            return False

        # Frustum culling: проверяем каждую вершину
        # Полигон видим, если хотя бы одна вершина в поле зрения

        for vertex in [a, b, c]:
            if self.is_point_visible(vertex):
                return True

        return False

    def transform_point_to_screen(self, point: Vector3) -> Vector2:
        """
        Проецирует 3D точку на 2D экран (относительно центра).
        
        Использует матричное преобразование для перехода из
        мировых координат в координаты экрана.
        
        Args:
            point: 3D точка в мировых координатах.
            
        Returns:
            2D координаты на экране (относительно центра).
        """
        if not self._moved and self._math_cache is not None:
            M_inv = self._math_cache
        else:
            # Строим базис камеры
            # a - вектор вправо (перпендикулярен direction и UP)
            a = np.cross(self.direction, np.array(UP_VECTOR))
            # b - вектор вверх камеры (перпендикулярен a и direction)
            b = np.cross(a, self.direction)

            # Матрица преобразования из мировых координат в координаты камеры
            M = np.array([a, b, self.direction]).T

            # Инвертируем матрицу (с регуляризацией для вырожденных случаев)
            try:
                M_inv = np.linalg.inv(M)
            except np.linalg.LinAlgError:
                M_inv = np.linalg.inv(M + MATRIX_REGULARIZATION)

            self._math_cache = M_inv
            self._moved = False

        # Преобразуем точку и масштабируем
        result = (M_inv @ (point.T - self.view_dot))[:2] * (constants.PROJECTION_SCALE / self.focus)
        result[1] *= -1  # Инвертируем Y (экранные координаты растут вниз)
        return result

    def project_point(self, world_point: Vector3) -> None | Vector2:
        """
        Проецирует 3D точку на экран с учётом размера экрана.

        Вычисляет пересечение луча камера->точка с плоскостью проекции.

        Args:
            world_point: 3D точка в мировых координатах.

        Returns:
            Абсолютные 2D координаты на экране, или None если точка за камерой.
        """
        # Вектор от камеры к точке
        ray = world_point - self.position

        # Проверяем что точка перед камерой (не за ней и не слишком близко)
        depth = np.dot(ray, self.direction)
        if depth < constants.NEAR_PLANE:
            return None

        # Система уравнений для нахождения точки пересечения с плоскостью проекции
        A = np.array([
            self.direction,
            [ray[1], -ray[0], 0],
            [ray[2], 0, -ray[0]]
        ])

        b = np.array([
            [(self.view_dot * self.direction).sum()],
            [ray[1] * self.position[0] - ray[0] * self.position[1]],
            [ray[2] * self.position[0] - ray[0] * self.position[2]]
        ])

        try:
            intersection = np.linalg.solve(A, b).T[0]
        except np.linalg.LinAlgError:
            # Регуляризация для вырожденных случаев
            intersection = np.linalg.solve(A + MATRIX_REGULARIZATION, b + MATRIX_REGULARIZATION).T[0]

        return self.transform_point_to_screen(intersection)

    def to_canvas(self, polygon: Triangle, screen_size: Vector2) -> ScreenCoords | None:
        """
        Проецирует треугольник на экран.

        Args:
            polygon: Треугольник (массив 3x3 вершин).
            screen_size: Размер экрана (ширина, высота).

        Returns:
            Список из 3 точек в экранных координатах,
            или None если хотя бы одна вершина за камерой.
        """
        points = []
        for i in range(3):
            point = self.project_point(polygon[i])
            if point is None:
                return None  # Вершина за камерой - пропускаем весь полигон
            points.append(point + (screen_size / 2))
        return points

    def _generate_polygons(self) -> list[Polygon]:
        return []
