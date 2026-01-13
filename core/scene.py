"""
Сцена для 3D движка Py3D.

Управляет объектами, освещением, игроком и рендерингом.
Организует основной цикл отрисовки.
"""

import time
import tkinter as tk
from typing import Any, Callable

import numpy as np

from core.objects.player import Player
from .screen import Screen
from core.objects.light import Light
from core.object import Object
from core.tools.editor import Editor
from core.objects.lighting import LightingSystem
from core.tools.types import Polygon, DrawData


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
            player: Player = Player(),
            screen_size: tuple[int, int] = (800, 600),
            objects: list[Object] = None,
            lights: list[Light] = None,
            render_script: Callable = None,
            show_fps: bool = True,
            show_axes: bool = True,
            fullscreen: bool = False,
            bg_color: str = "black",
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

        # Компоненты сцены
        self.objects = objects if objects is not None else []
        self.lights = list(lights) if lights is not None else []

        # Система освещения
        self.lighting_system = LightingSystem()

        # Экран
        self.screen = Screen(self.root, screen_size[0], screen_size[1], bg_color=bg_color)
        self._default_screen_size = screen_size

        self.render_script = render_script

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

        self._attributes_hash: dict[str, Object] = {}

    def _update_attributes(self):
        self._attributes_hash: dict[str, Object] = {}
        for light in self.lights:
            self._attributes_hash[light.id] = light
        for obj in self.objects:
            self._attributes_hash[obj.id] = obj


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
        if not polygons:
            return polygons

        # Векторизованное вычисление центров и расстояний
        centers = np.array([np.mean(poly, axis=0) for poly, _ in polygons])
        distances = np.linalg.norm(centers - self.player.position, axis=1)

        # Сортируем по убыванию расстояния (дальние первые)
        sorted_indices = np.argsort(distances)[::-1]

        return [polygons[i] for i in sorted_indices]

    def _compute_lighting(self, obj: Object) -> None:
        """
        Вычисляет освещение для объекта используя LightingSystem.
        
        Обновляет освещенные цвета объекта через кэширование.
        
        Args:
            obj: 3D объект для освещения.
        """
        if not self.lights:
            # Если нет источников света, инвалидируем кэш
            obj.invalidate_lighting_cache()
            return

        # Вычисляем освещенные цвета через систему освещения
        lighting_colors = self.lighting_system.compute_lighting(obj, self.lights)

        # Устанавливаем освещенные цвета в объект
        obj.set_lighting_colors(lighting_colors)

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

        self._update_attributes()

        if self.render_script:
            self.render_script()

        # Обновляем окно tkinter
        self.root.update()

        # Вычисляем освещение для всех объектов
        for obj in self.objects:
            self._compute_lighting(obj)

        # Собираем видимые полигоны от всех объектов (с освещенными цветами)
        visible_polys: list[Polygon] = []

        for obj in self.objects:
            # Используем get_lighted_polygons() для получения полигонов с освещенными цветами
            lighted_polygons = obj.get_lighted_polygons()

            # Фильтруем видимые полигоны
            for poly in lighted_polygons:
                if self.player.camera.is_polygon_visible(poly[0]):
                    visible_polys.append(poly)

        # Сбрасываем флаги движения источников света
        for light in self.lights:
            light.set_moved(False)

        # Сортируем по глубине (painter's algorithm)
        visible_polys: list[Polygon] = self._sort_by_distance(visible_polys)

        # Подготавливаем данные для отрисовки
        draw_data: list[DrawData] = []
        for poly, color in visible_polys:
            screen_coords = self.player.camera.get_canvas_coords(poly, self.screen.screen)
            if screen_coords is not None:
                draw_data.append((screen_coords, color))

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
