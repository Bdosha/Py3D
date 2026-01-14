import time
from abc import ABC, abstractmethod
from typing import Any

import numpy as np
from pydantic import BaseModel
import tkinter as tk

from core import Scene, Player, Object, Light, Screen, Editor


class Settings(BaseModel):
    window_title: str = "Py3D Engine"
    bg_color: str = "black"
    screen_size: tuple[int, int] = (800, 600)
    show_fps: bool = True
    show_axes: bool = True
    fullscreen: bool = False


class RenderScript(ABC):
    @abstractmethod
    def init(self, scene: Scene):
        """Метод будет выполняться в инициализации сцены, тут можно получить данные для сцены и реализации функционала"""

    @abstractmethod
    def run(self, scene: Scene):
        """Этот метод будет выполняться каждый кадр при вызове render в классе Scene.
        Может использовать любые публичные методы и поля сцены.

        Изменение сцены, ее объектов, размеров состояний и так далее"""


class EmptyScript(RenderScript):
    def init(self, scene: Scene):
        pass

    def run(self, scene: Scene):
        pass


class App:
    def __init__(self,
                 player: Player = Player(),
                 objects: list[Object] = None,
                 lights: list[Light] = None,
                 # scene: Scene,
                 render_script: RenderScript = None,
                 settings: Settings = None
                 ):

        self.settings = settings if settings is not None else Settings()

        self.player = player
        self.player.screen = np.array([self.settings.screen_size[0], self.settings.screen_size[1]])

        self.root = tk.Tk()
        self.root.title(self.settings.window_title)
        self.root.config(cursor="none", bg='#2b2b2b')

        self.screen = Screen(self.root,
                             self.settings.screen_size[0],
                             self.settings.screen_size[1],
                             bg_color=self.settings.bg_color)

        self.scene = Scene(
            screen=self.screen,
            player=player,
            objects=objects if objects is not None else [],
            lights=lights if lights is not None else [],
        )

        self.render_script = render_script if render_script is not None else EmptyScript()

        self._frame_start = time.time()

        self.editor = Editor(
            root=self.root,
            objects=objects,
            canvas=self.screen.canvas,
            lights=lights,
            player=self.player
        )
        self._editor_mode = False
        self._skip_mouse_event = False  # Флаг для пропуска первого события мыши после редактора

        # Привязка клавиш
        self._bind_controls()
        if render_script:
            self.render_script.init(self.scene)

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

    def _handle_movement(self, event: Any) -> None:
        """Обрабатывает движение (только если редактор не активен)."""
        if not self._editor_mode:
            self.player.move(event)

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
        self.settings.fullscreen = not self.settings.fullscreen
        self.root.attributes("-fullscreen", self.settings.fullscreen)

        # Определяем новый размер экрана
        if self.settings.fullscreen:
            new_size = (self.root.winfo_screenwidth(), self.root.winfo_screenheight())
        else:
            new_size = self.settings.screen_size

        # Обновляем размер экрана игрока
        self.player.screen = np.array([new_size[0], new_size[1]])

        # Пересоздаём canvas с новым размером
        self.screen.canvas.destroy()
        self.screen = Screen(self.root, new_size[0], new_size[1])
        self.editor.set_canvas(self.screen.canvas)
        self.editor.set_lights(self.scene.lights)
        self.editor.set_player(self.player)

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

    def run(self):
        while True:
            self._frame_start = time.time()

            self.root.update()

            self.render_script.run(self.scene)

            self.scene.render()

            if self.settings.show_fps:
                frame_time = time.time() - self._frame_start
                fps = 1.0 / frame_time if frame_time > 0 else 0
                self.screen.draw_fps(fps)

            if self.settings.show_axes:
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
