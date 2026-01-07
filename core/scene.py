"""
Сцена для 3D движка Py3D.

Управляет объектами, освещением, игроком и рендерингом.
Организует основной цикл отрисовки.
"""

import time
import tkinter as tk
from typing import Any

import numpy as np

from .player import Player
from .screen import Screen
from .light import Light
from .object import Object
from .types import Polygon, DrawData


class Scene:
    """
    Главная сцена 3D движка.
    
    Объединяет все компоненты: объекты, освещение, игрока,
    экран. Управляет рендерингом и обработкой ввода.
    
    Attributes:
        root: Окно tkinter.
        player: Контроллер игрока с камерой.
        objects: Список 3D объектов на сцене.
        lights: Список источников света.
        screen: Экран для рендеринга.
        show_fps: Флаг отображения FPS.
        fullscreen: Флаг полноэкранного режима.
    """
    
    def __init__(
        self,
        player: Player,
        screen_size: tuple[int, int],
        objects: list[Object] = None,
        lights: list[Light] = None,
        show_fps: bool = False,
        fullscreen: bool = False
    ) -> None:
        """
        Создаёт сцену.
        
        Args:
            player: Контроллер игрока.
            screen_size: Размер окна (ширина, высота).
            objects: Список 3D объектов.
            lights: Список источников света.
            show_fps: Показывать счётчик FPS.
            fullscreen: Запустить в полноэкранном режиме.
        """
        self.root = tk.Tk()
        self.root.config(cursor="none")
        
        # Время для расчёта FPS
        self._frame_start = time.time()
        
        # Инициализация игрока
        self.player = player
        self.player.screen = np.array([screen_size[0], screen_size[1]])
        self.player.last = self.player.screen / 2
        
        # Компоненты сцены
        self.objects = objects if objects is not None else []
        self.lights = list(lights) if lights is not None else []
        
        # Экран
        self.screen = Screen(self.root, screen_size[0], screen_size[1])
        self._default_screen_size = screen_size
        
        # Настройки
        self.show_fps = show_fps
        self.fullscreen = fullscreen
        
        # Привязка клавиш
        self._bind_controls()
        
        # Полноэкранный режим
        self.root.attributes("-fullscreen", fullscreen)
    
    def _bind_controls(self) -> None:
        """Привязывает обработчики клавиш и мыши."""
        # Движение WASD
        for key in ['w', 's', 'a', 'd']:
            self.root.bind(f'<{key}>', self.player.move)
        
        # Вверх/вниз
        self.root.bind('<space>', self.player.move)
        self.root.bind('<z>', self.player.move)
        
        # Поворот мышью
        self.root.bind("<Motion>", self.player.turn)
        
        # Переключение полноэкранного режима
        self.root.bind("<p>", self._toggle_fullscreen)
    
    def _toggle_fullscreen(self, event: Any = None) -> None:
        """
        Переключает полноэкранный режим.
        
        Args:
            event: Событие клавиатуры (игнорируется).
        """
        self.fullscreen = not self.fullscreen
        self.root.attributes("-fullscreen", self.fullscreen)
        
        # Определяем новый размер экрана
        if self.fullscreen:
            new_size = (self.root.winfo_screenwidth(), self.root.winfo_screenheight())
        else:
            new_size = self._default_screen_size
        
        # Обновляем размер экрана игрока
        self.player.screen = np.array([new_size[0], new_size[1]])
        
        # Пересоздаём canvas с новым размером
        self.screen.canvas.destroy()
        self.screen = Screen(self.root, new_size[0], new_size[1])
    
    def _sort_by_distance(self, polygons: list[Polygon]) -> list[Polygon]:
        """
        Сортирует полигоны по расстоянию от камеры (дальние первые).
        
        Используется для правильного порядка отрисовки (painter's algorithm).
        
        Args:
            polygons: Список полигонов с цветами.
            
        Returns:
            Отсортированный список (от дальних к ближним).
        """
        # Вычисляем расстояния до центров полигонов
        distances = [
            np.linalg.norm(np.mean(poly, axis=0) - self.player.position)
            for poly, _ in polygons
        ]
        
        # Сортируем по убыванию расстояния (дальние первые)
        sorted_indices = np.argsort(distances)[::-1]
        
        return [polygons[i] for i in sorted_indices]
    
    def _compute_lighting(self, poly: np.ndarray) -> float:
        """
        Вычисляет освещённость полигона от всех источников.
        
        Args:
            poly: Треугольник в мировых координатах.
            
        Returns:
            Суммарная интенсивность освещения [0, 1].
        """
        if not self.lights:
            return None
        
        total_intensity = 0.0
        for light in self.lights:
            total_intensity += light.get_intensity(poly)
        
        return min(1.0, total_intensity)
    
    def render(self) -> None:
        """
        Отрисовывает один кадр сцены.
        
        Выполняет:
        1. Сбор видимых полигонов от всех объектов
        2. Сортировку по глубине
        3. Проецирование на экран
        4. Расчёт освещения
        5. Отрисовку
        """
        self._frame_start = time.time()
        
        # Обновляем окно tkinter
        self.root.update()
        
        # Собираем видимые полигоны от всех объектов
        visible_polys: list[Polygon] = []
        for obj in self.objects:
            visible_polys.extend(obj.get_visible_polys(self.player.camera.is_visible))
        
        # Сортируем по глубине (painter's algorithm)
        visible_polys = self._sort_by_distance(visible_polys)
        
        # Подготавливаем данные для отрисовки
        draw_data: list[DrawData] = []
        for poly, color in visible_polys:
            # Проецируем на экран
            screen_coords = self.player.camera.to_canvas(poly, self.screen.screen)
            
            # Вычисляем освещение
            intensity = self._compute_lighting(poly)
            
            draw_data.append([screen_coords, color, intensity])
        
        # Отрисовываем
        self.screen.multi_draw(draw_data)
        
        # FPS
        if self.show_fps:
            frame_time = time.time() - self._frame_start
            fps = 1.0 / frame_time if frame_time > 0 else 0
            self.screen.draw_fps(fps)
