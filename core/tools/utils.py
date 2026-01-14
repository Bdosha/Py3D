"""
Математические утилиты для 3D движка Py3D.

Содержит функции для работы с векторами, матрицами поворота
и преобразованиями координат.
"""
import numpy as np
from numpy.typing import NDArray

from core import Vector3

# _matrix_cache: dict[tuple[float, float, float], tuple[NDArray[float], NDArray[float], NDArray[float]]] = {}

_matrix_cache: dict[tuple[float, float, float], NDArray[float]] = {}


def to_radians(degrees: float) -> float:
    """
    Преобразует градусы в радианы.
    
    Args:
        degrees: Угол в градусах.
        
    Returns:
        Угол в радианах, нормализованный в диапазон [0, 2π).
    """
    return (degrees * np.pi / 180) % (2 * np.pi)


def get_len(vector: NDArray) -> float:
    """
    Вычисляет длину (норму) вектора.
    
    Args:
        vector: Вектор произвольной размерности.
        
    Returns:
        Евклидова длина вектора.
    """
    return np.sqrt(np.sum(vector ** 2))


def set_len(vector: NDArray, length: float) -> NDArray:
    """
    Изменяет длину вектора на заданную.
    
    Args:
        vector: Исходный вектор.
        length: Желаемая длина.
        
    Returns:
        Вектор того же направления с заданной длиной.
        Если исходный вектор нулевой, возвращает его без изменений.
    """
    vector = vector.copy()
    vec_len = get_len(vector)

    if vec_len == 0:
        return vector
    return vector * length / vec_len


def set_ort(vector: NDArray) -> NDArray:
    """
    Нормализует вектор (приводит к единичной длине).
    
    Args:
        vector: Вектор для нормализации.
        
    Returns:
        Единичный вектор того же направления.
    """
    return set_len(vector, 1)


# def create_matrix(rotate: tuple[float, float, float]) -> tuple[NDArray, NDArray, NDArray]:
def create_matrix(rotate: tuple[float, float, float]) -> NDArray:
    """
    Создаёт матрицы поворота вокруг осей X, Y, Z.
    
    Использует соглашение об углах Эйлера: поворот вокруг X,
    затем вокруг Y, затем вокруг Z.
    
    Args:
        rotate: Углы поворота в градусах (rx, ry, rz).
        
    Returns:
        Кортеж из трёх матриц поворота 3x3 (Mx, My, Mz).
    """
    ans = _matrix_cache.get(rotate)

    if ans is not None:
        return ans

    np_rotate = np.array(rotate)

    rotate_rad = np.radians(np_rotate)
    cos = np.cos(rotate_rad)
    sin = np.sin(rotate_rad)

    # Матрица поворота вокруг оси X
    Mx = np.array([
        [1, 0, 0],
        [0, cos[0], -sin[0]],
        [0, sin[0], cos[0]]
    ], dtype=np.float32)

    # Матрица поворота вокруг оси Y
    My = np.array([
        [cos[1], 0, sin[1]],
        [0, 1, 0],
        [-sin[1], 0, cos[1]]
    ], dtype=np.float32)

    # Матрица поворота вокруг оси Z
    Mz = np.array([
        [cos[2], -sin[2], 0],
        [sin[2], cos[2], 0],
        [0, 0, 1]
    ], dtype=np.float32)

    _matrix_cache[rotate] = Mx @ My @ Mz
    return Mx @ My @ Mz


def get_cos(vector1: NDArray, vector2: NDArray) -> float:
    """
    Вычисляет угол между двумя векторами.
    
    Args:
        vector1: Первый вектор.
        vector2: Второй вектор.
        
    Returns:
        Угол между векторами в радианах [0, π].
    """
    return np.dot(set_ort(vector1), set_ort(vector2))


def to_new_system(
        vertices: NDArray,
        direction: tuple | Vector3,
        position: NDArray = np.array([0, 0, 0]),
) -> NDArray:
    """
    Преобразует вершины в новую систему координат.

    Вычисляет матрицы поворота по направлению.
    Применяет матрицы поворота и смещение позиции.
    Порядок применения: Mx -> My -> Mz -> смещение.
    
    Args:
        direction: Вектор направления объекта
        vertices: Массив вершин для преобразования.
        position: Вектор смещения (позиция объекта).

    Returns:
        Массив преобразованных вершин.
    """
    simple_direction = (float(direction[0]), float(direction[1]), float(direction[2]))

    M = create_matrix(simple_direction)
    return vertices @ M + position


def swap(poly: NDArray) -> NDArray:
    """
    Меняет порядок вершин в треугольнике.
    
    Используется для инверсии нормали (изменения направления
    обхода вершин с CW на CCW или наоборот).
    
    Args:
        poly: Треугольник (массив 3x3 вершин).
        
    Returns:
        Треугольник с переставленными вершинами [0, 2, 1].
    """
    temp = poly.copy()
    temp[1], temp[2] = temp[2].copy(), temp[1].copy()
    return temp


def to_float(poly: list) -> list[tuple[float, float]]:
    """
    Преобразует координаты полигона в список float-кортежей.
    
    Используется для передачи координат в tkinter Canvas.
    
    Args:
        poly: Список 2D точек (например, экранных координат).
        
    Returns:
        Список кортежей (x, y) с float координатами.
    """
    return [(float(point[0]), float(point[1])) for point in poly]


def mean(arr: list | NDArray) -> float:
    """
    Вычисляет среднее арифметическое.
    
    Args:
        arr: Список или массив чисел.
        
    Returns:
        Среднее значение элементов.
    """
    return sum(arr) / len(arr)
