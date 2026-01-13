"""
Экран (рендерер) для 3D движка Py3D.

Обёртка над tkinter Canvas для отрисовки полигонов,
текста и управления окном.
"""

import tkinter as tk

import numpy as np

from core.tools.types import Color, ScreenCoords, DrawData
from core.tools.constants import DEFAULT_BG_COLOR, FPS_TEXT_COLOR
from core.tools.utils import to_float


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
        base_color: Color
    ) -> None:
        """
        Отрисовывает один полигон с освещением.
        
        Args:
            poly: Экранные координаты вершин.
            base_color: Базовый RGB цвет.
        """
        r = min(255, max(0, int(base_color[0])))
        g = min(255, max(0, int(base_color[1])))
        b = min(255, max(0, int(base_color[2])))
        
        color_hex = f'#{r:02x}{g:02x}{b:02x}'
        
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
    
    def draw_axes_gizmo(
        self,
        camera_direction: np.ndarray,
        size: int = 50,
        margin: int = 10
    ) -> None:
        """
        Отрисовывает индикатор осей координат (gizmo).
        
        Показывает RGB оси (X-красный, Y-зелёный, Z-синий),
        которые вращаются в соответствии с направлением камеры.
        
        Args:
            camera_direction: Направление камеры (нормализованный вектор).
            size: Длина осей в пикселях.
            margin: Отступ от края экрана.
        """
        # Позиция центра gizmo (левый нижний угол)
        center_x = margin + size
        center_y = self.screen[1] - margin - size
        
        # Строим базис камеры для проекции осей
        up = np.array([0, 0, 1], dtype=np.float32)
        
        # Вектор вправо камеры
        right = np.cross(camera_direction, up)
        right_len = np.linalg.norm(right)
        if right_len > 0:
            right = right / right_len
        else:
            right = np.array([1, 0, 0], dtype=np.float32)
        
        # Вектор вверх камеры
        cam_up = np.cross(right, camera_direction)
        cam_up_len = np.linalg.norm(cam_up)
        if cam_up_len > 0:
            cam_up = cam_up / cam_up_len
        
        # Оси мировой системы координат
        axes = [
            (np.array([1, 0, 0]), '#ff3333', 'X'),  # X - красный
            (np.array([0, 1, 0]), '#33ff33', 'Y'),  # Y - зелёный  
            (np.array([0, 0, 1]), '#3333ff', 'Z'),  # Z - синий
        ]
        
        # Собираем данные для сортировки по глубине
        axis_data = []
        for axis_vec, color, label in axes:
            # Проецируем ось на плоскость экрана
            # x_screen = dot(axis, right), y_screen = dot(axis, cam_up)
            x_proj = np.dot(axis_vec, right) * size
            y_proj = np.dot(axis_vec, cam_up) * size
            # Глубина для сортировки (насколько ось направлена к камере)
            depth = np.dot(axis_vec, camera_direction)
            
            axis_data.append((depth, x_proj, y_proj, color, label))
        
        # Сортируем по глубине (дальние рисуем первыми)
        axis_data.sort(key=lambda x: x[0])
        
        # Рисуем оси
        for depth, x_proj, y_proj, color, label in axis_data:
            end_x = center_x + x_proj
            end_y = center_y - y_proj  # Инвертируем Y для экранных координат
            
            # Толщина линии зависит от того, направлена ли ось к нам
            width = 3 if depth > 0 else 2
            
            # Рисуем линию оси
            self.canvas.create_line(
                center_x, center_y,
                end_x, end_y,
                fill=color,
                width=width,
                arrow=tk.LAST,
                arrowshape=(8, 10, 4)
            )
            
            # Подпись оси (немного дальше конца стрелки)
            label_offset = 1.2
            label_x = center_x + x_proj * label_offset
            label_y = center_y - y_proj * label_offset
            
            self.canvas.create_text(
                label_x, label_y,
                text=label,
                fill=color,
                font=("Arial", 11, "bold"),
                anchor="center"
            )
        
        # Рисуем точку в центре
        self.canvas.create_oval(
            center_x - 3, center_y - 3,
            center_x + 3, center_y + 3,
            fill='white',
            outline='#333333'
        )
    
    def multi_draw(self, polygons: list[DrawData]) -> None:
        """
        Отрисовывает список полигонов.
        
        Args:
            polygons: Список данных для отрисовки.
                      Каждый элемент: (coords, color).
        """
        self.clear()
        
        for coords, color in polygons:
            if coords is not None:
                self.draw_polygon(coords, color)
