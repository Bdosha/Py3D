"""
Игрок (контроллер камеры от первого лица).

Обрабатывает ввод с клавиатуры и мыши для перемещения
и поворота камеры в 3D пространстве.
"""

import numpy as np
from typing import Any

from .camera import Camera
from .types import Vector2
from .constants import (
    DEFAULT_FOV,
    DEFAULT_POSITION,
    DEFAULT_DIRECTION,
    UP_VECTOR
)
from . import constants, Object, Polygon
from .utils import set_ort, get_len


class Player(Object):
    """
    Контроллер камеры от первого лица.
    
    Управляет камерой через WASD (движение), Space/Z (вверх/вниз) и движение мыши (поворот).
    
    Attributes:
        camera: Камера, привязанная к игроку.
        position: Текущая позиция игрока.
        direction: Направление взгляда.
        FOV: Угол обзора.
        _screen: Размер экрана (для расчёта поворота мышью).
    """

    def __init__(
        self,
        position: tuple[float, float, float] = DEFAULT_POSITION,
        direction: tuple[float, float, float] = DEFAULT_DIRECTION,
        fov: float = DEFAULT_FOV
    ) -> None:
        """
        Создаёт игрока с камерой.
        
        Args:
            position: Начальная позиция.
            direction: Начальное направление взгляда.
            fov: Угол обзора камеры.
        """

        # Защита от нулевого направления
        if all(d == 0 for d in direction):
            direction = DEFAULT_DIRECTION
        super().__init__(
            position=position,
            direction=direction,
        )
        self.FOV: float = fov

        # Камера синхронизирована с игроком
        self.camera = Camera(position, direction, fov)

        # Для отслеживания движения мыши
        self._last_cursor: Vector2 = np.array([0.0, 0.0])
        self._screen: Vector2 = np.array([800.0, 600.0])  # Размер по умолчанию

    @property
    def screen(self) -> Vector2:
        """Размер экрана для расчёта поворота мышью."""
        return self._screen

    @screen.setter
    def screen(self, value: Vector2) -> None:
        """Устанавливает размер экрана."""
        self._screen = np.array(value, dtype=np.float32)

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
            forward = self.direction.copy()
            forward[2] = 0  # Убираем вертикальную составляющую
            direction_sign = 1 if key == 'w' else -1
            movement = set_ort(forward) * direction_sign

        elif key in ('a', 'd'):
            # Движение влево/вправо (страфинг)
            right = np.cross(self.direction, up)
            direction_sign = 1 if key == 'd' else -1
            movement = set_ort(right) * direction_sign

        elif key == ' ':
            # Движение вверх
            movement = up * constants.VERTICAL_SPEED / constants.MOVE_SPEED

        elif key == 'z':
            # Движение вниз
            movement = -up * constants.VERTICAL_SPEED / constants.MOVE_SPEED

        # Применяем движение
        self.position += set_ort(movement) * constants.MOVE_SPEED
        self._sync_camera()

    def turn(self, event: Any) -> None:
        """
        Обрабатывает движение мыши для поворота камеры.
        
        Использует дельту движения мыши для плавного поворота.
        
        Args:
            event: Событие движения мыши tkinter.
        """
        # Позиция курсора относительно центра экрана
        cursor = np.array([event.x, event.y], dtype=np.float32) - self._screen / 2
        cursor[1] *= -1  # Инвертируем Y

        # event.state == 0 означает просто движение без нажатия кнопки
        if event.state == 0:
            self._last_cursor = cursor
            return

        # Вычисляем дельту движения
        delta = cursor - self._last_cursor
        self._last_cursor = cursor

        # Строим локальный базис камеры для поворота
        up = np.array(UP_VECTOR, dtype=np.float32)
        right = np.cross(self.direction, up)
        camera_up = np.cross(right, self.direction)

        # Нормализуем базисные векторы
        right_len = get_len(right)
        up_len = get_len(camera_up)

        if right_len > 0:
            right /= right_len
        if up_len > 0:
            camera_up /= up_len

        # Вычисляем поворот на основе движения мыши
        # Чувствительность зависит от скорости движения
        sensitivity = constants.MOUSE_SENSITIVITY / (np.sum(np.abs(delta / 10)) + 1e-4)
        rotation = (right * delta[0] + camera_up * delta[1]) / sensitivity

        # Применяем поворот
        self.direction += rotation
        self.direction = set_ort(self.direction)
        
        # Ограничиваем вертикальный угол (pitch) чтобы избежать gimbal lock
        # Не даём смотреть ровно вверх или вниз (максимум ~85 градусов)
        max_pitch = 0.95  # cos(~18°) от горизонта, т.е. ~72° от вертикали
        if abs(self.direction[2]) > max_pitch:
            # Сохраняем горизонтальное направление, ограничиваем вертикальное
            self.direction[2] = max_pitch if self.direction[2] > 0 else -max_pitch
            self.direction = set_ort(self.direction)

        self._sync_camera()

    def _sync_camera(self) -> None:
        """Синхронизирует камеру с позицией и направлением игрока."""
        self.camera.set_position(self.position, self.direction, self.FOV)

    def _generate_polygons(self) -> list[Polygon]:
        return []
    # Алиас для обратной совместимости
    go = move
