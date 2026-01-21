import time
from typing import Any, Callable

from pydantic import BaseModel
import tkinter as tk

from core import Scene, Object, BaseLight, Screen, Editor, Camera
from core.scripts.base_scripts import AppScript


class Settings(BaseModel):
    window_title: str = "Py3D Engine"
    bg_color: str = "aqua"
    screen_size: tuple[int, int] = (800, 600)
    show_fps: bool = True
    show_axes: bool = True
    fullscreen: bool = False


class FrameStats(BaseModel):
    scripts_time: float = 0
    render_time: float = 0
    draw_time: float = 0
    total_time: float = 0

    objects_count: int = 0
    lights_count: int = 0
    polygons_count: int = 0

    fps: float = 0


class App:
    def __init__(self,
                 camera: Camera = Camera(),
                 objects: list[Object] = None,
                 lights: list[BaseLight] = None,
                 app_scripts: list[AppScript] = None,
                 settings: Settings = None
                 ):

        self.settings = settings if settings is not None else Settings()

        # self.camera = camera
        # self.player.screen = np.array(self.settings.screen_size)

        self.root = tk.Tk()
        self.root.title(self.settings.window_title)
        self.root.config(cursor="none", bg='#2b2b2b')

        self.screen = Screen(self.root,
                             self.settings.screen_size[0],
                             self.settings.screen_size[1],
                             bg_color=self.settings.bg_color)

        self.scene = Scene(
            screen_size=self.settings.screen_size,
            camera=camera,
            # player=player,
            objects=objects if objects is not None else [],
            lights=lights if lights is not None else [],
        )

        self._app_scripts = app_scripts

        # Создаём редактор с объектами из сцены (изначально могут быть пустыми)
        self.editor = Editor(
            root=self.root,
            objects=self.scene.objects,
            canvas=self.screen.canvas,
            lights=self.scene.lights,
            camera=self.scene.camera,
        )
        self._editor_mode = False
        self._skip_mouse_event = False  # Флаг для пропуска первого события мыши после редактора
        self._motion_handlers = []  # Список обработчиков Motion из скриптов

        # Привязка клавиш
        self._bind_controls()

        if self._app_scripts:
            for script in self._app_scripts:
                script.init(self.scene, self._bind_with_motion_wrapper)

            self.editor.update_objects(self.scene.objects)
            self.editor.set_lights(self.scene.lights)

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

        # Пересоздаём canvas с новым размером
        self.screen.canvas.destroy()
        self.screen = Screen(self.root, new_size[0], new_size[1], bg_color=self.settings.bg_color)
        # Обновляем ссылку на screen в сцене
        self.scene.screen = self.screen
        self.editor.set_canvas(self.screen.canvas)
        self.editor.set_lights(self.scene.lights)
        self.editor.camera = self.scene.camera
        self.editor.update_objects(self.scene.objects)

    def _bind_controls(self) -> None:
        """Привязывает обработчики клавиш и мыши."""
        # Движение WASD
        self.root.bind("<p>", self._toggle_fullscreen)

        # Редактор
        self.root.bind("<Tab>", self._toggle_editor)
        self.root.bind("<Escape>", self._deselect_object)

        # Привязываем обертку для Motion событий перед инициализацией скриптов
        self.root.bind("<Motion>", self._handle_motion_event)

    def _bind_with_motion_wrapper(self, event_pattern: str, handler: Callable) -> None:
        """
        Обертка для root.bind, которая перехватывает Motion события.
        
        Args:
            event_pattern: Паттерн события (например, "<Motion>")
            handler: Обработчик события
        """
        if event_pattern == "<Motion>":
            # Сохраняем обработчик для вызова из _handle_motion_event
            self._motion_handlers.append(handler)
        else:
            # Для остальных событий привязываем напрямую
            self.root.bind(event_pattern, handler)

    def _is_cursor_over_editor(self, event: Any) -> bool:
        """
        Проверяет, находится ли курсор над панелями редактора.
        
        Args:
            event: Событие мыши tkinter
            
        Returns:
            True, если курсор над панелями редактора (hierarchy или inspector)
        """
        if not self._editor_mode or not self.editor.visible:
            return False

        # Получаем виджет под курсором используя координаты события
        # Используем x_root и y_root для получения абсолютных координат экрана
        x, y = event.x_root, event.y_root
        widget = self.root.winfo_containing(x, y)

        if widget is None:
            return False

        # Проверяем, является ли виджет частью панелей редактора
        # Проверяем hierarchy и inspector фреймы
        hierarchy_frame = self.editor.hierarchy.frame
        inspector_frame = self.editor.inspector.frame

        # Проверяем, является ли виджет дочерним элементом панелей редактора
        current = widget
        while current:
            if current == hierarchy_frame or current == inspector_frame:
                return True
            current = current.master

        return False

    def _handle_motion_event(self, event: Any) -> None:
        """
        Обработчик события Motion, который блокирует передачу события скриптам,
        если курсор находится над редактором и кнопка мыши зажата.
        
        Args:
            event: Событие движения мыши tkinter
        """
        # Проверяем, открыт ли редактор
        if not self._editor_mode:
            # Редактор закрыт - передаем все события скриптам
            for handler in self._motion_handlers:
                handler(event)
            return

        # Проверяем, находится ли курсор над редактором
        if not self._is_cursor_over_editor(event):
            # Курсор не над редактором - передаем события скриптам
            for handler in self._motion_handlers:
                handler(event)
            return

        # Курсор над редактором - проверяем, зажата ли кнопка мыши
        # event.state содержит флаги: 0x100 (Button1), 0x200 (Button2), 0x400 (Button3)
        mouse_button_pressed = (event.state & 0x100) or (event.state & 0x200) or (event.state & 0x400)

        if mouse_button_pressed:
            # Кнопка мыши зажата над редактором - блокируем события
            return
        else:
            # Кнопка мыши не зажата - передаем события скриптам
            for handler in self._motion_handlers:
                handler(event)

    def tick(self) -> FrameStats:
        stats = FrameStats()
        _frame_start = time.time()

        self.root.update()

        for script in self._app_scripts:
            script.run(self.scene)

        stats.scripts_time = time.time() - _frame_start

        frame_data = self.scene.render()
        stats.render_time = time.time() - stats.scripts_time

        self.screen.multi_draw(frame_data)
        stats.draw_time = time.time() - stats.render_time

        frame_time = time.time() - _frame_start
        fps = 1.0 / frame_time if frame_time > 0 else 0

        if self.settings.show_fps:
            self.screen.draw_fps(fps)

        if self.settings.show_axes:
            self.screen.draw_axes_gizmo(self.scene.camera.direction)

        # Подсказка про редактор
        if not self._editor_mode:
            self.screen.canvas.create_text(
                self.screen.screen[0] - 10, 10,
                text="Tab - Editor",
                fill='#888888',
                font=("Arial", 10),
                anchor="ne"
            )

        stats.total_time = frame_time
        stats.objects_count = len(self.scene.objects)
        stats.lights_count = len(self.scene.lights)
        stats.polygons_count = len(frame_data)

        stats.fps = fps

        return stats

    def run(self):
        while True:
            self.tick()
