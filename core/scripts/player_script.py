"""
Игрок (контроллер камеры от первого лица).

Обрабатывает ввод с клавиатуры и мыши для перемещения
и поворота камеры в 3D пространстве.
"""

import numpy as np
from typing import Any, override, Callable

from core.objects.camera import Camera
from core.tools.types import Vector2
from core.tools.constants import (
    UP_VECTOR
)
from core.tools import constants
from core.tools.utils import set_ort, get_len


class Player:
    """
    Контроллер камеры от первого лица.

    Управляет камерой через WASD (движение), Space/Z (вверх/вниз) и движение мыши (поворот).

    Attributes:
        camera: Камера, привязанная к игроку.
    """

    def __init__(self, camera: Camera = None) -> None:
        """
        Создаёт контроллер камеры от первого лица.

        Args:
            camera: Камера для управления. Если None, должна быть установлена позже.
        """
        self.camera = camera
        # Для отслеживания движения мыши
        self._last_cursor: None | Vector2 = None

    @property
    def last(self) -> Vector2:
        """Последняя позиция курсора."""
        return self._last_cursor

    @last.setter
    def last(self, value: Vector2) -> None:
        """Устанавливает последнюю позицию курсора."""
        self._last_cursor = np.array(value, dtype=np.float32)

    def move(self, event: Any) -> None:
        """
        Обрабатывает нажатие клавиш движения.

        Управление:
        - W: вперёд
        - S: назад
        - A: влево
        - D: вправо
        - Space: вверх
        - Z: вниз

        Args:
            event: Событие клавиатуры tkinter.
        """
        up = np.array(UP_VECTOR, dtype=np.float32)
        movement = np.zeros(3, dtype=np.float32)

        key = event.char.lower() if hasattr(event, 'char') else ''

        if key in ('w', 's'):
            # Движение вперёд/назад (без вертикальной составляющей)
            forward = self.camera.direction.copy()
            forward[2] = 0  # Убираем вертикальную составляющую
            direction_sign = 1 if key == 'w' else -1
            movement = set_ort(forward) * direction_sign

        elif key in ('a', 'd'):
            # Движение влево/вправо (страфинг)
            right = np.cross(self.camera.direction, up)
            direction_sign = 1 if key == 'd' else -1
            movement = set_ort(right) * direction_sign

        elif key == ' ':
            # Движение вверх
            movement = up * constants.VERTICAL_SPEED / constants.MOVE_SPEED

        elif key == 'z':
            # Движение вниз
            movement = -up * constants.VERTICAL_SPEED / constants.MOVE_SPEED

        # Применяем движение (используем присваивание через сеттер, а не +=)
        new_position = (
            self.camera.position +
            set_ort(movement) * constants.MOVE_SPEED
        )
        self.camera.position = new_position

    def turn(self, event: Any) -> None:
        """
        Обрабатывает движение мыши для поворота камеры.

        Использует дельту движения мыши для плавного поворота.

        Args:
            event: Событие движения мыши tkinter.
        """
        # Позиция курсора относительно центра экрана
        cursor = np.array([event.x, event.y], dtype=np.float32)  # - self._screen / 2
        cursor[1] *= -1  # Инвертируем Y

        # event.state == 0 означает просто движение без нажатия кнопки
        if event.state == 0 or self._last_cursor is None:
            self._last_cursor = cursor
            return

        # Вычисляем дельту движения
        delta = cursor - self._last_cursor
        self._last_cursor = cursor

        # Строим локальный базис камеры для поворота
        up = np.array(UP_VECTOR, dtype=np.float32)
        right = np.cross(self.camera.direction, up)
        camera_up = np.cross(right, self.camera.direction)

        # Нормализуем базисные векторы
        right_len = get_len(right)
        up_len = get_len(camera_up)

        if right_len > 0:
            right /= right_len
        if up_len > 0:
            camera_up /= up_len

        # Вычисляем поворот на основе движения мыши
        # Чувствительность зависит от скорости движения
        sensitivity = constants.MOUSE_SENSITIVITY / (
            np.sum(np.abs(delta / 10)) + 1e-4
        )
        rotation = (right * delta[0] + camera_up * delta[1]) / sensitivity

        # Применяем поворот (используем присваивание через сеттер, а не +=)
        new_direction = self.camera.direction + rotation
        self.camera.direction = set_ort(new_direction)

        # Ограничиваем вертикальный угол (pitch) чтобы избежать gimbal lock
        # Не даём смотреть ровно вверх или вниз (максимум ~85 градусов)
        max_pitch = 0.95  # cos(~18°) от горизонта, т.е. ~72° от вертикали
        current_direction = self.camera.direction.copy()
        if abs(current_direction[2]) > max_pitch:
            # Сохраняем горизонтальное направление, ограничиваем вертикальное
            current_direction[2] = max_pitch if current_direction[2] > 0 else -max_pitch
            self.camera.direction = set_ort(current_direction)


from core import Scene
from core.scripts.base_script import AppScript


class PlayerScript(AppScript):
    """
    Скрипт управления камерой от первого лица.
    
    Предоставляет управление камерой через WASD (движение),
    Space/Z (вверх/вниз) и движение мыши (поворот).
    """
    
    def __init__(self, fov: float = 90):
        """
        Создаёт скрипт управления камерой.
        
        Args:
            fov: Угол обзора камеры в градусах (по умолчанию 90).
        """
        self.fov = fov
        self.player = None

    @override
    def init(self, scene: Scene, root_bind_func: Callable[[str, Callable], None] = None):
        """
        Инициализирует управление камерой.
        
        Устанавливает FOV камеры и привязывает обработчики
        для клавиатуры (WASD, Space, Z) и мыши (Motion).
        
        Args:
            scene: Сцена с камерой для управления.
            root_bind_func: Функция для привязки обработчиков событий.
        """
        scene.camera.fov = self.fov
        self.player = Player(scene.camera)

        # Движение WASD
        for key in ['w', 's', 'a', 'd']:
            root_bind_func(f'<{key}>', self.player.move)

        # Вверх/вниз
        root_bind_func('<space>', self.player.move)
        root_bind_func('<z>', self.player.move)

        # Поворот мышью
        root_bind_func("<Motion>", self.player.turn)

    @override
    def run(self, scene: Scene):
        """
        Обновление скрипта каждый кадр.
        
        В данном скрипте ничего не выполняется каждый кадр,
        так как управление обрабатывается через события.
        
        Args:
            scene: Сцена (не используется в данном скрипте).
        """
        pass
