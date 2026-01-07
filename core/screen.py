"""
Экран (рендерер) для 3D движка Py3D.

Обёртка над tkinter Canvas для отрисовки полигонов,
текста и управления окном.
"""

import tkinter as tk
from typing import Optional

import numpy as np

from .types import Color, ScreenCoords, DrawData
from .constants import DEFAULT_BG_COLOR, FPS_TEXT_COLOR
from .utils import to_float


class Screen:
    """
    Экран для отрисовки 3D сцены.
    
    Использует tkinter Canvas для рендеринга полигонов.
    
    Attributes:
        root: Родительское окно tkinter.
        screen: Размер экрана (ширина, высота).
        canvas: Canvas для отрисовки.
    """
    
    def __init__(
        self,
        window: tk.Tk,
        width: int,
        height: int,
        bg_color: str = DEFAULT_BG_COLOR
    ) -> None:
        """
        Создаёт экран для рендеринга.
        
        Args:
            window: Родительское окно tkinter.
            width: Ширина экрана в пикселях.
            height: Высота экрана в пикселях.
            bg_color: Цвет фона (hex строка).
        """
        self.root = window
        self.screen = np.array([width, height], dtype=np.int32)
        self.canvas = tk.Canvas(
            self.root,
            width=width,
            height=height,
            bg=bg_color,
            cursor='none',
            highlightthickness=0
        )
        self.canvas.pack()
    
    def draw_polygon(
        self,
        poly: ScreenCoords,
        base_color: Color,
        intensity: Optional[float]
    ) -> None:
        """
        Отрисовывает один полигон с освещением.
        
        Args:
            poly: Экранные координаты вершин.
            base_color: Базовый RGB цвет.
            intensity: Интенсивность освещения (0-1), None = без освещения.
        """
        # Если интенсивность не задана, используем полную яркость
        if intensity is None:
            intensity = 1.0 - 1e-10  # Чуть меньше 1 для корректного округления
        
        # Применяем освещение к цвету
        r = int(base_color[0] * intensity)
        g = int(base_color[1] * intensity)
        b = int(base_color[2] * intensity)
        
        # Преобразуем в hex
        color_hex = f'#{r:02x}{g:02x}{b:02x}'
        
        # Отрисовываем
        self.canvas.create_polygon(
            to_float(poly),
            outline=color_hex,
            fill=color_hex
        )
    
    def clear(self) -> None:
        """Очищает экран (удаляет все объекты с canvas)."""
        self.canvas.delete("all")
    
    def draw_fps(self, fps: float) -> None:
        """
        Отображает счётчик FPS.
        
        Args:
            fps: Текущее значение кадров в секунду.
        """
        self.canvas.create_text(
            10, 10,
            text=f"FPS: {fps:.1f}",
            fill=FPS_TEXT_COLOR,
            font=("Arial", 16, "bold"),
            anchor="nw"
        )
    
    def multi_draw(self, polygons: list[DrawData]) -> None:
        """
        Отрисовывает список полигонов.
        
        Args:
            polygons: Список данных для отрисовки.
                      Каждый элемент: [coords, color, intensity].
        """
        self.clear()
        
        for poly_data in polygons:
            coords, color, intensity = poly_data
            
            if coords is None:
                continue
            
            self.draw_polygon(coords, color, intensity)
