"""
Сфера - геометрический примитив.

Генерирует сферу с помощью параметрического представления
через сферические координаты (theta, phi).
"""

import numpy as np

from core.object import Object
from core.tools.types import Color, Polygon
from core.tools.constants import (
    DEFAULT_COLOR,
    DEFAULT_POSITION,
    DEFAULT_ROTATION,
    DEFAULT_SCALING,
    MIN_SPHERE_DETAILS,
    SPHERE_SCALE_MULTIPLIER
)


class Sphere(Object):
    """
    Сфера с настраиваемой детализацией.
    
    Генерируется через разбиение сферической поверхности на
    треугольники с помощью широтно-долготной сетки.
    
    Attributes:
        details: Количество сегментов по широте.
    """
    
    def __init__(
        self,
        position: tuple[float, float, float] = DEFAULT_POSITION,
        direction: tuple[float, float, float] = DEFAULT_ROTATION,
        details: int = 8,
        scaling: tuple[float, float, float] = DEFAULT_SCALING,
        color: Color = DEFAULT_COLOR,
        inverted: bool = False
    ) -> None:
        """
        Создаёт сферу.
        
        Args:
            position: Позиция центра сферы в мировых координатах.
            direction: Углы поворота в градусах.
            details: Детализация (минимум 3, больше = более гладкая).
            scaling: Масштаб по осям (можно создать эллипсоид).
            color: RGB цвет сферы.
            inverted: Если True, нормали направлены внутрь.
        """
        self.details = max(details, MIN_SPHERE_DETAILS)
        
        # Применяем множитель масштаба специфичный для сферы
        adjusted_scaling = tuple(s * SPHERE_SCALE_MULTIPLIER for s in scaling)
        
        super().__init__(
            position=position,
            direction=direction,
            scaling=adjusted_scaling,
            color=color,
            inverted=inverted
        )
    
    def _generate_polygons(self) -> list[Polygon]:
        """
        Генерирует полигоны сферы.
        
        Использует параметрическое представление сферы:
        x = sin(theta) * cos(phi)
        y = sin(theta) * sin(phi)
        z = cos(theta)
        
        где theta ∈ [0, π] (широта), phi ∈ [0, 2π) (долгота).
        """
        phi_steps = 2 * self.details    # Шаги по долготе
        theta_steps = self.details       # Шаги по широте
        
        # Генерация вершин
        vertices = []
        for i in range(theta_steps + 1):
            theta = i * np.pi / theta_steps
            sin_theta = np.sin(theta)
            cos_theta = np.cos(theta)
            
            for j in range(phi_steps):
                phi = j * 2 * np.pi / phi_steps
                sin_phi = np.sin(phi)
                cos_phi = np.cos(phi)
                
                x = sin_theta * cos_phi
                y = sin_theta * sin_phi
                z = cos_theta
                vertices.append(np.array([x, y, z], dtype=np.float32))
        
        # Генерация треугольников
        polygons = []
        for i in range(theta_steps):
            for j in range(phi_steps):
                next_j = (j + 1) % phi_steps
                
                # Индексы вершин текущего и следующего кольца
                i0 = i * phi_steps + j
                i1 = i * phi_steps + next_j
                i2 = (i + 1) * phi_steps + j
                i3 = (i + 1) * phi_steps + next_j
                
                # Верхний треугольник (пропускаем на полюсе)
                if i != 0:
                    tri = np.array([vertices[i0], vertices[i1], vertices[i2]])
                    polygons.append((tri, self.color))
                
                # Нижний треугольник (пропускаем на полюсе)
                if i != theta_steps - 1:
                    tri = np.array([vertices[i1], vertices[i3], vertices[i2]])
                    polygons.append((tri, self.color))
        return polygons
