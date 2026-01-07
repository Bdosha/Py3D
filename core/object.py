"""
Базовый класс для всех 3D объектов в движке Py3D.

Определяет абстрактный интерфейс и общую логику трансформаций
для всех геометрических примитивов и моделей.
"""

from abc import ABC, abstractmethod
import numpy as np

from .types import Vector3, Triangle, Color, Polygon, VisibilityCheck
from .constants import (
    DEFAULT_POSITION,
    DEFAULT_ROTATION,
    DEFAULT_SCALING,
    DEFAULT_COLOR,
    EPSILON
)
from .utils import create_matrix, to_new_system, swap


class Object(ABC):
    """
    Абстрактный базовый класс для всех 3D объектов.
    
    Предоставляет общую функциональность для позиционирования,
    вращения, масштабирования и инверсии объектов.
    
    Attributes:
        position: Позиция объекта в мировых координатах.
        scale: Масштаб объекта по осям X, Y, Z.
        inverted: Флаг инверсии нормалей (для внутренних поверхностей).
        color: Базовый цвет объекта.
        polys: Список полигонов объекта с цветами.
        Mx, My, Mz: Матрицы поворота вокруг осей X, Y, Z.
    """
    
    def __init__(
        self,
        position: tuple[float, float, float] = DEFAULT_POSITION,
        rotate: tuple[float, float, float] = DEFAULT_ROTATION,
        scaling: tuple[float, float, float] = DEFAULT_SCALING,
        color: Color = DEFAULT_COLOR,
        inverted: bool = False
    ) -> None:
        """
        Инициализирует базовые параметры объекта.
        
        Args:
            position: Позиция объекта в мировых координатах (x, y, z).
            rotate: Углы поворота в градусах (rx, ry, rz).
            scaling: Масштаб по осям (sx, sy, sz).
            color: RGB цвет объекта (r, g, b), значения 0-255.
            inverted: Если True, нормали полигонов направлены внутрь.
        """
        self.position: Vector3 = np.array(position, dtype=np.float32)
        self.Mx, self.My, self.Mz = create_matrix(rotate)
        self.scale: Vector3 = np.array(scaling, dtype=np.float32) + EPSILON
        self.color: Color = color
        self.inverted: bool = inverted
        self.polys: list[Polygon] = []
        
        # Генерация полигонов вызывается в конце инициализации
        self._generate_polys()
        
        # Применение инверсии после генерации
        if self.inverted:
            self._apply_inversion()
    
    @abstractmethod
    def _generate_polys(self) -> None:
        """
        Генерирует полигоны объекта.
        
        Этот метод должен быть реализован в каждом дочернем классе.
        Должен заполнить self.polys списком кортежей (triangle, color).
        """
        pass
    
    def _apply_inversion(self) -> None:
        """
        Инвертирует нормали всех полигонов.
        
        Меняет порядок вершин в треугольниках для изменения
        направления нормалей (используется для внутренних поверхностей).
        """
        inverted_polys = []
        for poly, color in self.polys:
            inverted_polys.append((swap(poly), color))
        self.polys = inverted_polys
    
    def to_system(self, vertices: Triangle) -> Triangle:
        """
        Преобразует вершины в мировую систему координат.
        
        Применяет матрицы поворота и смещение позиции.
        
        Args:
            vertices: Массив вершин в локальных координатах.
            
        Returns:
            Массив вершин в мировых координатах.
        """
        return to_new_system(self.Mx, self.My, self.Mz, self.position, vertices)
    
    def rotate_to(self, vertices: Triangle, rotate: tuple[float, float, float]) -> Triangle:
        """
        Поворачивает вершины на заданные углы.
        
        Args:
            vertices: Массив вершин для поворота.
            rotate: Углы поворота в градусах (rx, ry, rz).
            
        Returns:
            Массив повёрнутых вершин.
        """
        Xb, Yb, Zb = create_matrix(rotate)
        return to_new_system(Xb, Yb, Zb, np.array([0, 0, 0]), vertices)
    
    def move_to(self, position: tuple[float, float, float]) -> None:
        """
        Перемещает объект в новую позицию.
        
        Args:
            position: Новая позиция объекта (x, y, z).
        """
        self.position = np.array(position, dtype=np.float32)
    
    def set_rotation(self, rotate: tuple[float, float, float]) -> None:
        """
        Устанавливает новый поворот объекта.
        
        Args:
            rotate: Новые углы поворота в градусах (rx, ry, rz).
        """
        self.Mx, self.My, self.Mz = create_matrix(rotate)
    
    def get_color(self, poly: Triangle) -> Color:
        """
        Возвращает цвет для полигона.
        
        Может быть переопределён в дочерних классах для
        динамического расчёта цвета (например, по высоте).
        
        Args:
            poly: Треугольник для которого нужен цвет.
            
        Returns:
            RGB цвет полигона.
        """
        return self.color
    
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
        for poly, color in self.polys:
            transformed = self.to_system(poly * self.scale)
            if visibility_check(transformed):
                visible.append((transformed, color))
        return visible
