"""
Генераторы полигонов для графиков и параметрических поверхностей.

Содержит функции для создания сеток треугольников из:
- Функций z = f(x, y)
- Параметрических поверхностей (u, v) -> (x, y, z)
"""
from typing import Callable

import numpy as np
from numpy.typing import NDArray

from core.utils import mean
from core.types import Color, Polygon


def get_color(poly: NDArray, max_height: float) -> float:
    """
    Вычисляет компоненту цвета на основе средней высоты полигона.
    
    Args:
        poly: Треугольник (массив 3x3).
        max_height: Максимальная высота для нормализации.
        
    Returns:
        Значение цвета 0-255.
    """
    if max_height == 0:
        return 127  # Средний цвет для плоских поверхностей
    return (mean(poly[:, 2]) + max_height) / (2 * max_height) * 255


def get_colors(poly: NDArray, max_height: float) -> Color:
    """
    Вычисляет RGB цвет полигона на основе высоты.
    
    Создаёт градиент от пурпурного (низ) к зелёному (верх).
    
    Args:
        poly: Треугольник (массив 3x3).
        max_height: Максимальная высота для нормализации.
        
    Returns:
        RGB кортеж цвета.
    """
    c = get_color(poly, max_height)
    return (int(c), int(255 - c), int(c))


# =============================================================================
# Параметрические функции поверхностей
# =============================================================================

def spiral(alpha: float, beta: float, U: NDArray, V: NDArray) -> tuple[NDArray, NDArray, NDArray]:
    """
    Спиральная поверхность.
    
    Args:
        alpha, beta: Параметры формы.
        U, V: Сетки параметров.
        
    Returns:
        Координаты X, Y, Z поверхности.
    """
    X = (alpha + beta * np.cos(V)) * np.cos(U)
    Y = (alpha + beta * np.sin(V)) * np.sin(U)
    Z = beta * np.sin(V) + alpha * U
    return X, Y, Z


def mobius(alpha: float, beta: float, U: NDArray, V: NDArray) -> tuple[NDArray, NDArray, NDArray]:
    """
    Лента Мёбиуса.
    
    Args:
        alpha, beta: Параметры формы.
        U, V: Сетки параметров.
        
    Returns:
        Координаты X, Y, Z поверхности.
    """
    X = (alpha + V * np.cos(U / 2)) * np.cos(U)
    Y = (alpha + V * np.cos(U / 2)) * np.sin(U)
    Z = beta * np.sin(U / 2) * V
    return X, Y, Z


def torus(alpha: float, beta: float, U: NDArray, V: NDArray) -> tuple[NDArray, NDArray, NDArray]:
    """
    Тор (бублик).
    
    Args:
        alpha: Радиус тора (расстояние от центра до центра трубки).
        beta: Радиус трубки.
        U, V: Сетки параметров.
        
    Returns:
        Координаты X, Y, Z поверхности.
    """
    X = (alpha + beta * np.cos(V)) * np.cos(U)
    Y = (alpha + beta * np.cos(V)) * np.sin(U)
    Z = beta * np.sin(V)
    return X, Y, Z


def screw(alpha: float, beta: float, U: NDArray, V: NDArray) -> tuple[NDArray, NDArray, NDArray]:
    """
    Винтовая поверхность (геликоид).
    
    Args:
        alpha, beta: Параметры формы.
        U, V: Сетки параметров.
        
    Returns:
        Координаты X, Y, Z поверхности.
    """
    X = alpha * U * np.cos(U)
    Y = beta * U * np.sin(U)
    Z = V
    return X, Y, Z


def sea_shell(alpha: float, beta: float, U: NDArray, V: NDArray) -> tuple[NDArray, NDArray, NDArray]:
    """
    Морская раковина (экспоненциальная спираль).
    
    Args:
        alpha, beta: Параметры формы.
        U, V: Сетки параметров.
        
    Returns:
        Координаты X, Y, Z поверхности.
    """
    exp_term = alpha * np.exp(beta * V)
    X = exp_term * np.cos(V) * (1 + np.cos(U))
    Y = exp_term * np.cos(V) * (1 + np.cos(U))
    Z = exp_term * np.sin(U)
    return X, Y, Z


# =============================================================================
# Конфигурация параметрических поверхностей
# =============================================================================

# Формат: (U_min, U_max, V_min, V_max, function, scale)
SURFACE_CONFIG = {
    0: (-2 * np.pi, 2 * np.pi, -np.pi, np.pi, spiral, 1.5),
    1: (0, 2 * np.pi, -0.5, 0.5, mobius, 4),
    2: (0, 2 * np.pi, 0, 2 * np.pi, torus, 3),
    3: (0, 4 * np.pi, -2, 2, screw, 0.7),
    4: (0, 2 * np.pi, 0, 6 * np.pi, sea_shell, 1.5e-8),
}


def get_surface_info(surface_type: int) -> tuple:
    """
    Возвращает параметры для типа поверхности.
    
    Args:
        surface_type: Индекс типа поверхности (0-4).
        
    Returns:
        Кортеж (U_min, U_max, V_min, V_max, function, scale).
        
    Raises:
        KeyError: Если тип поверхности не существует.
    """
    return SURFACE_CONFIG[surface_type]


def load_parametric_surface(
    alpha: float,
    beta: float,
    details: int,
    surface_type: int
) -> list[Polygon]:
    """
    Загружает полигоны параметрической поверхности.
    
    Args:
        alpha, beta: Параметры формы поверхности.
        details: Количество точек разбиения по каждому параметру.
        surface_type: Тип поверхности (0-4).
        
    Returns:
        Список полигонов с цветами.
    """
    u_min, u_max, v_min, v_max, func, scale = get_surface_info(surface_type)
    
    U, V = np.meshgrid(
        np.linspace(u_min, u_max, details),
        np.linspace(v_min, v_max, details),
        indexing='ij'
    )
    
    X, Y, Z = func(alpha, beta, U, V)
    max_z = max(Z.max(), abs(Z.min()))
    
    polys = create_triangle_mesh(X, Y, Z, max_z, details)
    
    # Применяем масштаб
    return [(poly * scale, color) for poly, color in polys]


def load_graphic(
    func: Callable,
    details: int,
    range_limit: float
) -> list[Polygon]:
    """
    Загружает полигоны для графика функции z = f(x, y).
    
    Args:
        func: Функция двух переменных, принимает массивы numpy.
        details: Количество точек разбиения.
        range_limit: Диапазон по X и Y: [-range_limit, range_limit].
        
    Returns:
        Список полигонов с цветами.
    """
    u = np.linspace(-range_limit, range_limit, details)
    x, y = np.meshgrid(u, u, indexing='ij')
    z = func(x, y)
    
    return create_triangle_mesh(x, y, z, range_limit, details)


def create_triangle_mesh(
    x: NDArray,
    y: NDArray,
    z: NDArray,
    max_z: float,
    details: int
) -> list[Polygon]:
    """
    Создаёт сетку треугольников из массивов координат.
    
    Генерирует двустороннюю поверхность с раскраской по высоте.
    
    Args:
        x, y, z: 2D массивы координат точек.
        max_z: Максимальная высота для ограничения и раскраски.
        details: Размер сетки.
        
    Returns:
        Список полигонов с цветами.
    """
    # Ограничиваем значения Z
    z = np.clip(z, -max_z, max_z)
    
    # Создаём массивы для двух типов треугольников в каждой ячейке
    n = details - 1
    tris1 = np.empty((n, n, 3, 3), dtype=np.float32)
    tris2 = np.empty((n, n, 3, 3), dtype=np.float32)
    
    # Первый тип: верхний правый угол ячейки
    tris1[:, :, 0] = np.stack([x[1:, 1:], y[1:, 1:], z[1:, 1:]], axis=-1)
    tris1[:, :, 1] = np.stack([x[:-1, 1:], y[:-1, 1:], z[:-1, 1:]], axis=-1)
    tris1[:, :, 2] = np.stack([x[1:, :-1], y[1:, :-1], z[1:, :-1]], axis=-1)
    
    # Второй тип: нижний левый угол ячейки
    tris2[:, :, 0] = np.stack([x[:-1, :-1], y[:-1, :-1], z[:-1, :-1]], axis=-1)
    tris2[:, :, 1] = np.stack([x[1:, :-1], y[1:, :-1], z[1:, :-1]], axis=-1)
    tris2[:, :, 2] = np.stack([x[:-1, 1:], y[:-1, 1:], z[:-1, 1:]], axis=-1)
    
    # Объединяем все треугольники (лицевые и обратные стороны)
    all_tris = np.vstack([
        tris1.reshape(-1, 3, 3),
        tris2.reshape(-1, 3, 3),
        np.flip(tris1, axis=2).reshape(-1, 3, 3),  # Обратная сторона
        np.flip(tris2, axis=2).reshape(-1, 3, 3),  # Обратная сторона
    ])
    
    # Фильтруем треугольники на границе (полностью на пределе Z)
    result = []
    for tri in all_tris:
        # Пропускаем если все три вершины на границе
        if not (abs(tri[0, 2]) == max_z and abs(tri[1, 2]) == max_z and abs(tri[2, 2]) == max_z):
            result.append((tri, get_colors(tri, max_z)))
    
    return result


# Алиас для обратной совместимости
load_lab = load_parametric_surface
