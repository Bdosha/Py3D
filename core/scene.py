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
from .editor import Editor
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
        show_axes: Флаг отображения индикатора осей.
        fullscreen: Флаг полноэкранного режима.
        editor: Редактор сцены.
    """

    def __init__(
            self,
            player: Player,
            screen_size: tuple[int, int],
            objects: list[Object] = None,
            lights: list[Light] = None,
            show_fps: bool = False,
            show_axes: bool = False,
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
            show_axes: Показывать индикатор осей координат.
            fullscreen: Запустить в полноэкранном режиме.
        """
        self.root = tk.Tk()
        self.root.title("Py3D Engine")
        self.root.config(cursor="none", bg='#2b2b2b')

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

        # Настройки отображения
        self.show_fps = show_fps
        self.show_axes = show_axes
        self.fullscreen = fullscreen

        # Редактор сцены
        self.editor = Editor(
            self.root, self.objects, self.screen.canvas,
            lights=self.lights, player=self.player
        )
        self._editor_mode = False
        self._skip_mouse_event = False  # Флаг для пропуска первого события мыши после редактора

        # Привязка клавиш
        self._bind_controls()

        # Полноэкранный режим
        self.root.attributes("-fullscreen", fullscreen)

    def _bind_controls(self) -> None:
        """Привязывает обработчики клавиш и мыши."""
        # Движение WASD
        for key in ['w', 's', 'a', 'd']:
            self.root.bind(f'<{key}>', self._handle_movement)

        # Вверх/вниз
        self.root.bind('<space>', self._handle_movement)
        self.root.bind('<z>', self._handle_movement)

        # Поворот мышью
        self.root.bind("<Motion>", self._handle_mouse)

        # Переключение полноэкранного режима
        self.root.bind("<p>", self._toggle_fullscreen)

        # Редактор
        self.root.bind("<Tab>", self._toggle_editor)
        self.root.bind("<Escape>", self._deselect_object)

    def _handle_movement(self, event: Any) -> None:
        """Обрабатывает движение (только если редактор не активен)."""
        if not self._editor_mode:
            self.player.move(event)

    def _handle_mouse(self, event: Any) -> None:
        """Обрабатывает движение мыши (только если редактор не активен)."""
        if self._editor_mode:
            return

        # Пропускаем первое событие после закрытия редактора
        if self._skip_mouse_event:
            self._skip_mouse_event = False
            # Обновляем last на текущую позицию курсора (относительно центра, с инверсией Y)
            cursor = np.array([event.x, event.y], dtype=np.float32) - self.player.screen / 2
            cursor[1] *= -1
            self.player.last = cursor
            return

        self.player.turn(event)

    def _toggle_editor(self, event: Any = None) -> None:
        """Переключает режим редактора."""
        self._editor_mode = not self._editor_mode
        self.editor.toggle()

        # Меняем курсор
        if self._editor_mode:
            self.root.config(cursor="arrow")
        else:
            self.root.config(cursor="none")
            # Пропускаем следующее событие мыши чтобы камера не "улетела"
            self._skip_mouse_event = True

    def _deselect_object(self, event: Any = None) -> None:
        """Снимает выделение объекта в редакторе."""
        if self._editor_mode:
            self.editor.deselect()

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
        self.editor.set_canvas(self.screen.canvas)
        self.editor.set_lights(self.lights)
        self.editor.set_player(self.player)

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

    def _compute_lighting(self, poly: np.ndarray) -> float | None:
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

    def add_object(self, obj: Object) -> None:
        """
        Добавляет объект на сцену.
        
        Args:
            obj: 3D объект для добавления.
        """
        self.objects.append(obj)
        self.editor.update_objects(self.objects)

    def remove_object(self, index: int) -> None:
        """
        Удаляет объект со сцены.
        
        Args:
            index: Индекс объекта в списке.
        """
        if 0 <= index < len(self.objects):
            self.objects.pop(index)
            self.editor.update_objects(self.objects)

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
            visible_polys += [
                poly
                for poly in obj.polygons
                if self.player.camera.is_visible(poly[0])
            ]


        # Сортируем по глубине (painter's algorithm)
        visible_polys: list[Polygon] = self._sort_by_distance(visible_polys)

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

        # HUD элементы
        if self.show_fps:
            frame_time = time.time() - self._frame_start
            fps = 1.0 / frame_time if frame_time > 0 else 0
            self.screen.draw_fps(fps)

        if self.show_axes:
            self.screen.draw_axes_gizmo(self.player.direction)

        # Подсказка про редактор
        if not self._editor_mode:
            self.screen.canvas.create_text(
                self.screen.screen[0] - 10, 10,
                text="Tab - Editor",
                fill='#888888',
                font=("Arial", 10),
                anchor="ne"
            )
