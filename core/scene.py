"""
Сцена для 3D движка Py3D.

Управляет объектами, освещением, игроком и рендерингом.
Организует основной цикл отрисовки.
"""

import numpy as np

from core.objects.player import Player
from .screen import Screen
from core.objects.lights import BaseLight
from core.object import Object
from core.objects.lighting import LightingSystem
from core.tools.types import Polygon, DrawData


class Scene:
    """
    Главная сцена 3D движка.
    
    Объединяет все компоненты: объекты, освещение, игрока,
    экран. Управляет рендерингом и обработкой ввода.
    
    Attributes:
        player: Контроллер игрока с камерой.
        objects: Список 3D объектов на сцене.
        lights: Список источников света.
        screen: Экран для рендеринга.
    """

    def __init__(
            self,
            screen: Screen,
            player: Player = Player(),
            objects: list[Object] = None,
            lights: list[BaseLight] = None,
    ) -> None:
        """
        Создаёт сцену.
        
        Args:
            player: Контроллер игрока.
            # screen_size: Размер окна (ширина, высота).
            objects: Список 3D объектов.
            lights: Список источников света.
            # show_fps: Показывать счётчик FPS.
            # show_axes: Показывать индикатор осей координат.
            # fullscreen: Запустить в полноэкранном режиме.
        """
        # Инициализация игрока
        self.player = player

        # Компоненты сцены
        self.objects = objects if objects is not None else []
        self.lights = lights if lights is not None else []

        # Система освещения
        self.lighting_system = LightingSystem()

        # Экран
        self.screen = screen

        self._attributes_hash: dict[str, Object] = {}

    def _update_attributes(self):
        self._attributes_hash: dict[str, Object] = {}
        for light in self.lights:
            self._attributes_hash[light.id] = light
        for obj in self.objects:
            self._attributes_hash[obj.id] = obj

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

        self._update_attributes()

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
