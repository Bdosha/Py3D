"""
Загрузчик 3D моделей из файлов.

Поддерживает загрузку моделей из формата GLTF/GLB
с использованием библиотеки trimesh.
"""

import numpy as np
import trimesh

from core.object import Object
from core.utils import swap
from core.types import Color, Polygon
from core.constants import DEFAULT_POSITION, DEFAULT_ROTATION, DEFAULT_SCALING, DEFAULT_COLOR


def load_polygons_from_gltf(file_path: str) -> list[np.ndarray]:
    """
    Загружает полигоны из GLTF/GLB файла.
    
    Args:
        file_path: Путь к файлу модели.
        
    Returns:
        Список треугольников (массивов 3x3).
        
    Raises:
        ValueError: Если файл не содержит поддерживаемых мешей.
        FileNotFoundError: Если файл не найден.
    """
    loaded = trimesh.load(file_path)
    polygons = []

    if isinstance(loaded, trimesh.Scene):
        # Файл содержит сцену с несколькими объектами
        for geometry in loaded.geometry.values():
            if isinstance(geometry, trimesh.Trimesh):
                polygons.extend(_extract_triangles(geometry))
    elif isinstance(loaded, trimesh.Trimesh):
        # Файл содержит один меш
        polygons.extend(_extract_triangles(loaded))
    else:
        raise ValueError(f"Файл не содержит поддерживаемых мешей: {file_path}")

    return polygons


def _extract_triangles(mesh: trimesh.Trimesh) -> list[np.ndarray]:
    """
    Извлекает треугольники из меша.
    
    Args:
        mesh: Trimesh объект.
        
    Returns:
        Список треугольников.
    """
    triangles = []
    for face in mesh.faces:
        triangle = np.array([
            mesh.vertices[face[0]],
            mesh.vertices[face[1]],
            mesh.vertices[face[2]]
        ], dtype=np.float32)
        triangles.append(triangle)
    return triangles


class Model(Object):
    """
    3D модель, загруженная из файла.
    
    Поддерживает форматы GLTF и GLB через библиотеку trimesh.
    
    Attributes:
        model_path: Путь к файлу модели.
    """

    def __init__(
            self,
            model_path: str,
            position: tuple[float, float, float] = DEFAULT_POSITION,
            direction: tuple[float, float, float] = DEFAULT_ROTATION,
            scaling: tuple[float, float, float] = DEFAULT_SCALING,
            color: Color = DEFAULT_COLOR,
            inverted: bool = False
    ) -> None:
        """
        Загружает и создаёт 3D модель.
        
        Args:
            model_path: Путь к файлу модели (GLTF/GLB).
            position: Позиция модели в мировых координатах.
            direction: Углы поворота в градусах.
            scaling: Масштаб по осям.
            color: Базовый цвет модели (если нет текстур).
            inverted: Если True, инвертирует нормали.
        """
        self.model_path = model_path

        super().__init__(
            position=position,
            direction=direction,
            scaling=scaling,
            color=color,
            inverted=inverted
        )

    def _generate_polygons(self) -> list[Polygon]:
        """
        Загружает полигоны из файла модели.
        
        Корректирует порядок вершин для правильных нормалей.
        """
        raw_polys = load_polygons_from_gltf(self.model_path)
        polygons = []
        for poly in raw_polys:
            # Корректируем порядок вершин (swap для правильных нормалей)
            polygons.append((swap(poly), self.color))
        return polygons
