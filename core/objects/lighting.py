"""
Система освещения для 3D движка Py3D.

Управляет вычислением и кэшированием освещенных цветов для объектов.
Отделяет логику освещения от рендеринга для лучшей архитектуры.
"""

from typing import Optional
import numpy as np

from core.object import Object
from core.objects.light import Light
from core.tools.types import Color


class LightingSystem:
    """
    Система управления освещением с кэшированием.
    
    Вычисляет освещенные цвета для объектов и кэширует результаты,
    пересчитывая только при изменении объектов или источников света.
    
    Attributes:
        _cache: Кэш освещенных цветов {object_id: (colors, light_states, obj_state)}
    """
    
    def __init__(self) -> None:
        """Создаёт систему освещения."""
        self._cache: dict[str, tuple[list[Color], tuple, tuple]] = {}
    
    def _get_light_states(self, lights: list[Light]) -> tuple:
        """
        Получает состояния всех источников света для проверки изменений.
        
        Args:
            lights: Список источников света.
            
        Returns:
            Кортеж состояний (позиция, направление, FOV, power) для каждого света.
        """
        states = []
        for light in lights:
            states.append((
                tuple(light.position),
                tuple(light.direction),
                light.FOV,
                light.power
            ))
        return tuple(states)
    
    def _get_object_state(self, obj: Object) -> tuple:
        """
        Получает состояние объекта для проверки изменений.
        
        Args:
            obj: 3D объект.
            
        Returns:
            Кортеж состояния (позиция, направление, масштаб).
        """
        return (
            tuple(obj.position),
            tuple(obj.direction),
            tuple(obj.scaling)
        )
    
    def is_cache_valid(self, obj: Object, lights: list[Light]) -> bool:
        """
        Проверяет валидность кэша для объекта.
        
        Args:
            obj: 3D объект.
            lights: Список источников света.
            
        Returns:
            True если кэш валиден, False если нужен пересчет.
        """
        obj_id = str(obj._id)
        
        # Если объекта нет в кэше, кэш невалиден
        if obj_id not in self._cache:
            return False
        
        # Получаем сохраненные состояния
        _, cached_light_states, cached_obj_state = self._cache[obj_id]
        
        # Проверяем состояние объекта
        current_obj_state = self._get_object_state(obj)
        if current_obj_state != cached_obj_state:
            return False
        
        # Проверяем состояния источников света
        current_light_states = self._get_light_states(lights)
        if current_light_states != cached_light_states:
            return False
        
        return True
    
    def compute_lighting(self, obj: Object, lights: list[Light]) -> list[Color]:
        """
        Вычисляет освещенные цвета для объекта.
        
        Использует кэш если он валиден, иначе пересчитывает освещение.
        
        Args:
            obj: 3D объект.
            lights: Список источников света.
            
        Returns:
            Список освещенных цветов для каждого полигона объекта.
        """
        obj_id = str(obj._id)
        
        # Проверяем кэш
        if self.is_cache_valid(obj, lights):
            colors, _, _ = self._cache[obj_id]
            return colors
        
        # Кэш невалиден или отсутствует - пересчитываем
        new_colors = []
        
        # Получаем полигоны объекта
        polygons = obj.polygons
        
        # Вычисляем освещение для каждого полигона
        for poly in polygons:
            # Собираем вклады от всех источников света
            light_contributions = []
            for light in lights:
                light_color = light.get_light_color(poly)
                light_contributions.append(light_color)
            
            # Усредняем вклады от всех источников
            if light_contributions:
                mean_color = np.array(light_contributions).mean(axis=0)
            else:
                # Если нет источников света, используем базовый цвет полигона
                mean_color = poly[1].copy()
            
            # Ограничиваем значения цвета в диапазоне [0, 255]
            mean_color = np.clip(mean_color, 0, 255)
            new_colors.append(mean_color)
        
        # Сохраняем в кэш
        light_states = self._get_light_states(lights)
        obj_state = self._get_object_state(obj)
        self._cache[obj_id] = (new_colors, light_states, obj_state)
        
        return new_colors
    
    def invalidate_cache(self, obj_id: Optional[str] = None) -> None:
        """
        Инвалидирует кэш освещения.
        
        Args:
            obj_id: ID объекта для инвалидации. Если None, очищает весь кэш.
        """
        if obj_id is None:
            self._cache.clear()
        else:
            obj_id_str = str(obj_id)
            if obj_id_str in self._cache:
                del self._cache[obj_id_str]
    
    def clear_cache(self) -> None:
        """Очищает весь кэш освещения."""
        self._cache.clear()

