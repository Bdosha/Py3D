"""
Камера для 3D движка Py3D.

Обеспечивает проекцию 3D точек на 2D экран и отсечение
невидимых полигонов (frustum culling, backface culling).
"""

import numpy as np
from numpy.typing import NDArray

from .types import Vector3, Vector2, Triangle, ScreenCoords
from .constants import (
    DEFAULT_FOV,
    DEFAULT_FOCUS,
    DEFAULT_POSITION,
    DEFAULT_DIRECTION,
    PROJECTION_SCALE,
    MATRIX_REGULARIZATION,
    UP_VECTOR
)
from .utils import to_radians, set_ort, get_angle


class Camera:
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
        self.position: Vector3 = np.array(DEFAULT_POSITION, dtype=np.float32)
        self.direction: Vector3 = np.array(DEFAULT_DIRECTION, dtype=np.float32)
        self.FOV: float = to_radians(180 - DEFAULT_FOV)
        self.focus: float = DEFAULT_FOCUS
        self.view_dot: Vector3 = np.array(DEFAULT_POSITION, dtype=np.float32)
        
        self.move_to(position, direction, fov)
    
    def move_to(
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
    
    def is_visible(self, poly: Triangle) -> bool:
        """
        Проверяет видимость полигона.
        
        Выполняет две проверки:
        1. Frustum culling: полигон в поле зрения камеры
        2. Backface culling: полигон обращён к камере
        
        Args:
            poly: Треугольник (массив 3x3 вершин).
            
        Returns:
            True если полигон видим, False если его можно отсечь.
        """
        a, b, c = poly
        center = (a + b + c) / 3
        
        # Вектор от камеры к центру полигона
        to_poly = center - self.position
        
        # Frustum culling: проверяем угол между направлением и вектором к полигону
        if get_angle(to_poly, self.direction) > self.FOV / 2:
            return False
        
        # Backface culling: вычисляем нормаль полигона
        normal = set_ort(np.cross(b - a, c - a))
        
        # Полигон виден если его нормаль направлена к камере
        if np.dot(normal, to_poly) < 0:
            return False
        
        return True
    
    def to_screen(self, point: Vector3) -> Vector2:
        """
        Проецирует 3D точку на 2D экран (относительно центра).
        
        Использует матричное преобразование для перехода из
        мировых координат в координаты экрана.
        
        Args:
            point: 3D точка в мировых координатах.
            
        Returns:
            2D координаты на экране (относительно центра).
        """
        # Строим базис камеры
        # a - вектор вправо (перпендикулярен direction и UP)
        a = np.cross(self.direction, np.array(UP_VECTOR))
        # b - вектор вверх камеры (перпендикулярен a и direction)
        b = np.cross(a, self.direction)
        
        # Матрица преобразования из мировых координат в координаты камеры
        M = np.array([a, b, self.direction]).T
        P = self.view_dot.T
        
        # Инвертируем матрицу (с регуляризацией для вырожденных случаев)
        try:
            M_inv = np.linalg.inv(M)
        except np.linalg.LinAlgError:
            M_inv = np.linalg.inv(M + MATRIX_REGULARIZATION)
        
        # Преобразуем точку и масштабируем
        result = (M_inv @ (point.T - P.T))[:2] * (PROJECTION_SCALE / self.focus)
        return result
    
    def project_point(self, world_point: Vector3, screen_size: Vector2) -> Vector2:
        """
        Проецирует 3D точку на экран с учётом размера экрана.
        
        Вычисляет пересечение луча камера->точка с плоскостью проекции.
        
        Args:
            world_point: 3D точка в мировых координатах.
            screen_size: Размер экрана (ширина, высота).
            
        Returns:
            Абсолютные 2D координаты на экране.
        """
        # Вектор от камеры к точке
        ray = world_point - self.position
        
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
        
        # Преобразуем в экранные координаты
        screen_coords = self.to_screen(intersection)
        screen_coords[1] *= -1  # Инвертируем Y (экранные координаты растут вниз)
        
        return screen_coords + (screen_size / 2)
    
    def to_canvas(self, poly: Triangle, screen_size: Vector2) -> ScreenCoords:
        """
        Проецирует треугольник на экран.
        
        Args:
            poly: Треугольник (массив 3x3 вершин).
            screen_size: Размер экрана (ширина, высота).
            
        Returns:
            Список из 3 точек в экранных координатах.
        """
        return [self.project_point(poly[i], screen_size) for i in range(3)]
