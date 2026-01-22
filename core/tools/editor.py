"""
Редактор сцены для 3D движка Py3D.

Предоставляет GUI интерфейс для управления объектами:
- Hierarchy: список объектов и источников света
- Inspector: свойства выбранного элемента
"""

import tkinter as tk
from typing import Optional, Callable, Any
import numpy as np

from core import Camera
from core.objects import Object
from core.objects.lights import BaseLight
import core.tools.constants as constants_module

# =============================================================================
# Стили тёмной темы
# =============================================================================

DARK_THEME = {
    'bg': '#2b2b2b',
    'bg_secondary': '#3c3c3c',
    'bg_hover': '#4a4a4a',
    'fg': '#cccccc',
    'fg_dim': '#888888',
    'accent': '#4a9eff',
    'border': '#555555',
    'input_bg': '#1e1e1e',
}

# Палитра готовых цветов
COLOR_PALETTE = [
    ('#ffffff', 'White'),
    ('#ff0000', 'Red'),
    ('#00ff00', 'Green'),
    ('#0000ff', 'Blue'),
    ('#ffff00', 'Yellow'),
    ('#ff00ff', 'Magenta'),
    ('#00ffff', 'Cyan'),
    ('#ff8800', 'Orange'),
    ('#88ff00', 'Lime'),
    ('#0088ff', 'Sky'),
    ('#ff0088', 'Pink'),
    ('#8800ff', 'Purple'),
    ('#888888', 'Gray'),
    ('#444444', 'Dark Gray'),
    ('#000000', 'Black'),
]


def hex_to_rgb(hex_color: str) -> tuple[int, ...]:
    """Конвертирует HEX цвет в RGB."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    """Конвертирует RGB в HEX."""
    return f'#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}'


class HierarchyPanel:
    """
    Панель иерархии объектов (левая панель).
    """

    def __init__(self, parent: tk.Frame, on_select: Callable[[str, int], None], width: int = 200):
        self.on_select = on_select
        self.selected_type: Optional[str] = None
        self.selected_index: Optional[int] = None
        self.buttons: dict[str, list[tk.Button]] = {'objects': [], 'lights': []}

        self.frame = tk.Frame(parent, width=width, bg=DARK_THEME['bg'])
        self.frame.pack_propagate(False)

        self._create_ui()

    def _create_ui(self):
        """Создаёт UI панели."""
        # Заголовок
        header = tk.Frame(self.frame, bg=DARK_THEME['bg_secondary'], height=40)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        title = tk.Label(
            header, text="📋 Hierarchy",
            bg=DARK_THEME['bg_secondary'], fg=DARK_THEME['fg'],
            font=("Arial", 12, "bold"), anchor="w", padx=10
        )
        title.pack(fill=tk.BOTH, expand=True, pady=8)

        tk.Frame(self.frame, bg=DARK_THEME['border'], height=1).pack(fill=tk.X)

        # Контейнер с прокруткой
        self.content = tk.Frame(self.frame, bg=DARK_THEME['bg'])
        self.content.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Секция Objects
        self.objects_section = tk.Frame(self.content, bg=DARK_THEME['bg'])
        self.objects_section.pack(fill=tk.X, pady=(0, 10))

        tk.Label(
            self.objects_section, text="▼ Objects",
            bg=DARK_THEME['bg'], fg=DARK_THEME['fg'],
            font=("Arial", 10, "bold"), anchor="w"
        ).pack(anchor="w")

        self.objects_list = tk.Frame(self.objects_section, bg=DARK_THEME['bg'])
        self.objects_list.pack(fill=tk.X, padx=(10, 0))

        # Секция Lights
        self.lights_section = tk.Frame(self.content, bg=DARK_THEME['bg'])
        self.lights_section.pack(fill=tk.X, pady=(0, 10))

        tk.Label(
            self.lights_section, text="▼ Lights",
            bg=DARK_THEME['bg'], fg='#ffcc00',
            font=("Arial", 10, "bold"), anchor="w"
        ).pack(anchor="w")

        self.lights_list = tk.Frame(self.lights_section, bg=DARK_THEME['bg'])
        self.lights_list.pack(fill=tk.X, padx=(10, 0))

        # Секция Camera
        self.camera_section = tk.Frame(self.content, bg=DARK_THEME['bg'])
        self.camera_section.pack(fill=tk.X)

        camera_btn = tk.Button(
            self.camera_section,
            text="📷 Camera",
            bg=DARK_THEME['bg_secondary'], fg=DARK_THEME['fg'],
            activebackground=DARK_THEME['accent'], activeforeground='white',
            relief=tk.FLAT, anchor="w", padx=10, pady=5,
            font=("Arial", 10, "bold"),
            command=lambda: self._on_click('camera', 0)
        )
        camera_btn.pack(fill=tk.X, pady=1)
        self.camera_btn = camera_btn

        # Секция Settings
        self.settings_section = tk.Frame(self.content, bg=DARK_THEME['bg'])
        self.settings_section.pack(fill=tk.X, pady=(10, 0))

        settings_btn = tk.Button(
            self.settings_section,
            text="⚙️ Settings",
            bg=DARK_THEME['bg_secondary'], fg='#ff6b6b',
            activebackground=DARK_THEME['accent'], activeforeground='white',
            relief=tk.FLAT, anchor="w", padx=10, pady=5,
            font=("Arial", 10, "bold"),
            command=lambda: self._on_click('settings', 0)
        )
        settings_btn.pack(fill=tk.X, pady=1)
        self.settings_btn = settings_btn

    def show(self):
        self.frame.pack(side=tk.LEFT, fill=tk.Y)

    def hide(self):
        self.frame.pack_forget()

    def update(self, objects: list[Object], lights: list[BaseLight]):
        """Обновляет списки объектов и источников света."""
        # Очищаем объекты
        for btn in self.buttons['objects']:
            btn.destroy()
        self.buttons['objects'].clear()

        # Проверяем, что objects не None
        if objects is None:
            objects = []

        for i, obj in enumerate(objects):
            btn = tk.Button(
                self.objects_list,
                text=f"  {obj.__class__.__name__} [{i}]",
                bg=DARK_THEME['bg_secondary'], fg=DARK_THEME['fg'],
                activebackground=DARK_THEME['accent'], activeforeground='white',
                relief=tk.FLAT, anchor="w", padx=10, pady=3,
                font=("Arial", 9),
                command=lambda idx=i: self._on_click('object', idx)
            )
            btn.pack(fill=tk.X, pady=1)
            self.buttons['objects'].append(btn)

        # Очищаем источники света
        for btn in self.buttons['lights']:
            btn.destroy()
        self.buttons['lights'].clear()

        # Проверяем, что lights не None
        if lights is None:
            lights = []

        for i, light in enumerate(lights):
            btn = tk.Button(
                self.lights_list,
                text=f"  💡 {light.__class__.__name__} [{i}]",
                bg=DARK_THEME['bg_secondary'], fg='#ffcc00',
                activebackground=DARK_THEME['accent'], activeforeground='white',
                relief=tk.FLAT, anchor="w", padx=10, pady=3,
                font=("Arial", 9),
                command=lambda idx=i: self._on_click('light', idx)
            )
            btn.pack(fill=tk.X, pady=1)
            self.buttons['lights'].append(btn)

        self._update_selection()

    def _on_click(self, item_type: str, index: int):
        self.selected_type = item_type
        self.selected_index = index
        self._update_selection()
        self.on_select(item_type, index)

    def _update_selection(self):
        # Сбрасываем все кнопки
        for btn in self.buttons['objects']:
            btn.configure(bg=DARK_THEME['bg_secondary'], fg=DARK_THEME['fg'])
        for btn in self.buttons['lights']:
            btn.configure(bg=DARK_THEME['bg_secondary'], fg='#ffcc00')
        self.camera_btn.configure(bg=DARK_THEME['bg_secondary'], fg=DARK_THEME['fg'])
        self.settings_btn.configure(bg=DARK_THEME['bg_secondary'], fg='#ff6b6b')

        # Выделяем выбранный
        if self.selected_type == 'object' and self.selected_index is not None:
            if 0 <= self.selected_index < len(self.buttons['objects']):
                self.buttons['objects'][self.selected_index].configure(
                    bg=DARK_THEME['accent'], fg='white'
                )
        elif self.selected_type == 'light' and self.selected_index is not None:
            if 0 <= self.selected_index < len(self.buttons['lights']):
                self.buttons['lights'][self.selected_index].configure(
                    bg=DARK_THEME['accent'], fg='white'
                )
        elif self.selected_type == 'camera':
            self.camera_btn.configure(bg=DARK_THEME['accent'], fg='white')
        elif self.selected_type == 'settings':
            self.settings_btn.configure(bg=DARK_THEME['accent'], fg='white')

    def deselect(self):
        self.selected_type = None
        self.selected_index = None
        self._update_selection()


class InspectorPanel:
    """
    Панель инспектора (правая панель).
    """

    def __init__(self, parent: tk.Frame, on_change: Callable[[], None], width: int = 280):
        self.on_change = on_change
        self.current_item: Any = None
        self.current_type: Optional[str] = None
        self.sliders: dict[str, tk.Scale] = {}

        self.frame = tk.Frame(parent, width=width, bg=DARK_THEME['bg'])
        self.frame.pack_propagate(False)

        self._create_ui()

    def _create_ui(self):
        header = tk.Frame(self.frame, bg=DARK_THEME['bg_secondary'], height=40)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(
            header, text="⚙️ Inspector",
            bg=DARK_THEME['bg_secondary'], fg=DARK_THEME['fg'],
            font=("Arial", 12, "bold"), anchor="w", padx=10
        ).pack(fill=tk.BOTH, expand=True, pady=8)

        tk.Frame(self.frame, bg=DARK_THEME['border'], height=1).pack(fill=tk.X)

        # Scrollable content
        self.canvas = tk.Canvas(self.frame, bg=DARK_THEME['bg'], highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self.frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.props_frame = tk.Frame(self.canvas, bg=DARK_THEME['bg'])

        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.canvas_window = self.canvas.create_window((0, 0), window=self.props_frame, anchor='nw')
        self.props_frame.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox('all')))
        self.canvas.bind('<Configure>', lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width))

        self._show_empty()

    def _show_empty(self):
        for w in self.props_frame.winfo_children():
            w.destroy()
        tk.Label(
            self.props_frame, text="Select an item\nto edit properties",
            bg=DARK_THEME['bg'], fg=DARK_THEME['fg_dim'],
            font=("Arial", 10), justify="center"
        ).pack(expand=True, pady=50)

    def show(self):
        self.frame.pack(side=tk.RIGHT, fill=tk.Y)

    def hide(self):
        self.frame.pack_forget()

    def set_object(self, obj: Optional[Object]):
        """Показывает свойства объекта."""
        self.current_item = obj
        self.current_type = 'object'
        self._clear()

        if obj is None:
            self._show_empty()
            return

        self._add_title(obj.__class__.__name__, DARK_THEME['accent'])
        self._add_section("Transform")
        self._add_vector3("Position", obj.position, self._on_obj_position, (-100, 100))
        # direction в Object - это углы Эйлера в градусах
        self._add_vector3("Rotation", obj.direction, self._on_obj_rotation, (-180, 180))
        self._add_vector3("Scale", obj.scaling, self._on_obj_scale, (0.1, 10))

        self._add_section("Appearance")
        if hasattr(obj, 'color'):
            self._add_color_palette("Color", obj.color)

    def set_light(self, light: Optional[BaseLight]):
        """Показывает свойства источника света."""
        self.current_item = light
        self.current_type = 'light'
        self._clear()

        if light is None:
            self._show_empty()
            return

        self._add_title(f"💡 {light.__class__.__name__}", '#ffcc00')
        self._add_section("Transform")
        self._add_vector3("Position", light.position, self._on_light_position, (-100, 100))
        self._add_vector3("Direction", light.direction, self._on_light_direction, (-1, 1), resolution=0.01)

        self._add_section("Properties")
        self._add_slider("Power", light._power * 10, self._on_light_power, (1, 500))
        if hasattr(light, '_half_fov_cos'):
            fov_deg = 2 * np.degrees(np.arccos(np.clip(light._half_fov_cos, -1, 1)))
            self._add_slider("FOV", fov_deg, self._on_light_fov, (10, 180))

    def set_camera(self, camera: Camera):
        """Показывает свойства камеры."""
        self.current_item = camera
        self.current_type = 'camera'
        self._clear()

        self._add_title("📷 Camera", '#88ccff')
        self._add_section("Transform")
        self._add_vector3("Position", camera.position, self._on_camera_position, (-100, 100))
        self._add_vector3("Direction", camera.direction, self._on_camera_direction, (-1, 1), resolution=0.01)

        self._add_section("Properties")
        self._add_slider("FOV", camera.fov, self._on_camera_fov, (30, 120))

    def set_settings(self):
        """Показывает настройки глобальных констант."""
        self.current_item = None
        self.current_type = 'settings'
        self._clear()

        self._add_title("⚙️ Global Settings", '#ff6b6b')

        # Рендеринг
        self._add_section("Rendering")
        self._add_slider("Projection Scale", constants_module.PROJECTION_SCALE,
                         self._on_projection_scale, (500, 5000))
        self._add_slider("Near Plane", constants_module.NEAR_PLANE,
                         self._on_near_plane, (0.01, 1.0), resolution=0.01)

        # Управление
        self._add_section("Controls")
        self._add_slider("Mouse Sensitivity", constants_module.MOUSE_SENSITIVITY,
                         self._on_mouse_sensitivity, (100, 2000))
        self._add_slider("Move Speed", constants_module.MOVE_SPEED,
                         self._on_move_speed, (0.01, 1.0), resolution=0.01)
        self._add_slider("Vertical Speed", constants_module.VERTICAL_SPEED,
                         self._on_vertical_speed, (0.01, 0.5), resolution=0.01)

        # Освещение
        self._add_section("Lighting")
        self._add_slider("Min Light Power", constants_module.MIN_LIGHT_POWER,
                         self._on_min_light_power, (0.1, 2.0), resolution=0.1)
        self._add_slider("Default Light FOV", constants_module.DEFAULT_LIGHT_FOV,
                         self._on_default_light_fov, (10, 90))
        self._add_slider("Light Falloff", constants_module.LIGHT_FALLOFF_MULTIPLIER,
                         self._on_light_falloff, (1, 50))

    def _clear(self):
        for w in self.props_frame.winfo_children():
            w.destroy()
        self.sliders.clear()

    def _add_title(self, text: str, color: str):
        tk.Label(
            self.props_frame, text=text,
            bg=DARK_THEME['bg'], fg=color,
            font=("Arial", 14, "bold")
        ).pack(anchor="w", padx=10, pady=(10, 5))

    def _add_section(self, title: str):
        frame = tk.Frame(self.props_frame, bg=DARK_THEME['bg'])
        frame.pack(fill=tk.X, padx=10, pady=(15, 5))

        tk.Label(
            frame, text=f"▼ {title}",
            bg=DARK_THEME['bg'], fg=DARK_THEME['fg'],
            font=("Arial", 10, "bold")
        ).pack(anchor="w")
        tk.Frame(frame, bg=DARK_THEME['border'], height=1).pack(fill=tk.X, pady=(3, 0))

    def _add_vector3(self, name: str, values, callback, range_: tuple, resolution: float = 0.1):
        frame = tk.Frame(self.props_frame, bg=DARK_THEME['bg'])
        frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(
            frame, text=name, bg=DARK_THEME['bg'], fg=DARK_THEME['fg_dim'],
            font=("Arial", 9), width=10, anchor="w"
        ).pack(side=tk.LEFT)

        sliders_frame = tk.Frame(frame, bg=DARK_THEME['bg'])
        sliders_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        colors = ['#ff6b6b', '#51cf66', '#339af0']
        axes = ['X', 'Y', 'Z']

        for i, (axis, color) in enumerate(zip(axes, colors)):
            row = tk.Frame(sliders_frame, bg=DARK_THEME['bg'])
            row.pack(fill=tk.X, pady=1)

            tk.Label(
                row, text=axis, bg=DARK_THEME['bg'], fg=color,
                font=("Arial", 8, "bold"), width=2
            ).pack(side=tk.LEFT)

            slider = tk.Scale(
                row,
                from_=range_[0],
                to=range_[1],
                resolution=resolution,
                orient=tk.HORIZONTAL,
                bg=DARK_THEME['bg'],
                fg=DARK_THEME['fg'],
                troughcolor=DARK_THEME['input_bg'],
                activebackground=color,
                highlightthickness=0,
                length=140,
                showvalue=True,
                command=lambda v, idx=i, cb=callback: cb(idx, float(v))
            )
            slider.set(float(values[i]) if i < len(values) else 0)
            slider.pack(side=tk.LEFT, fill=tk.X, expand=True)
            self.sliders[f"{name}_{axis}"] = slider

    def _add_slider(self, name: str, value: float, callback, range_: tuple, resolution: float = 1.0):
        frame = tk.Frame(self.props_frame, bg=DARK_THEME['bg'])
        frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(
            frame, text=name, bg=DARK_THEME['bg'], fg=DARK_THEME['fg_dim'],
            font=("Arial", 9), width=10, anchor="w"
        ).pack(side=tk.LEFT)

        slider = tk.Scale(
            frame,
            from_=range_[0],
            to=range_[1],
            resolution=resolution,
            orient=tk.HORIZONTAL,
            bg=DARK_THEME['bg'],
            fg=DARK_THEME['fg'],
            troughcolor=DARK_THEME['input_bg'],
            activebackground=DARK_THEME['accent'],
            highlightthickness=0,
            length=160,
            showvalue=True,
            command=lambda v: callback(float(v))
        )
        slider.set(value)
        slider.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.sliders[name] = slider

    def _add_color_palette(self, name: str, current_color: tuple):
        frame = tk.Frame(self.props_frame, bg=DARK_THEME['bg'])
        frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(
            frame, text=name, bg=DARK_THEME['bg'], fg=DARK_THEME['fg_dim'],
            font=("Arial", 9), anchor="w"
        ).pack(anchor="w")

        palette_frame = tk.Frame(frame, bg=DARK_THEME['bg'])
        palette_frame.pack(fill=tk.X, pady=5)

        current_hex = rgb_to_hex(current_color)

        for i, (hex_color, color_name) in enumerate(COLOR_PALETTE):
            # Используем Canvas вместо Button для корректного отображения цвета на macOS
            size = 30
            border = 3 if hex_color == current_hex else 1
            border_color = '#ffffff' if hex_color == current_hex else DARK_THEME['border']

            canvas = tk.Canvas(
                palette_frame,
                width=size, height=size,
                bg=DARK_THEME['bg'],
                highlightthickness=border,
                highlightbackground=border_color
            )
            canvas.grid(row=i // 5, column=i % 5, padx=2, pady=2)

            # Рисуем цветной прямоугольник
            canvas.create_rectangle(0, 0, size, size, fill=hex_color, outline='')

            # Привязываем клик
            canvas.bind('<Button-1>', lambda e, c=hex_color: self._on_color_select(c))

    # === Object callbacks ===
    def _on_obj_position(self, axis: int, value: float):
        if self.current_item and self.current_type == 'object':
            # Используем сеттер для правильного обновления состояния
            pos = list(self.current_item.position)
            pos[axis] = value
            self.current_item.position = tuple(pos)
            self.on_change()

    def _on_obj_rotation(self, axis: int, value: float):
        if self.current_item and self.current_type == 'object':
            # Получаем все значения из слайдеров
            rotation = [self.sliders.get(f"Rotation_{ax}", tk.Scale()).get() for ax in ['X', 'Y', 'Z']]
            self.current_item.direction = tuple(rotation)
            self.on_change()

    def _on_obj_scale(self, axis: int, value: float):
        if self.current_item and self.current_type == 'object':
            # Используем сеттер для правильного обновления состояния
            scale = list(self.current_item.scaling)
            scale[axis] = value
            self.current_item.scaling = tuple(scale)
            self.on_change()

    def _on_color_select(self, hex_color: str):
        if self.current_item and self.current_type == 'object' and hasattr(self.current_item, 'color'):
            rgb = hex_to_rgb(hex_color)
            # Устанавливаем цвет объекта (это обновит базовый цвет)
            self.current_item.color = np.array(rgb, dtype=np.float32)
            # Инвалидируем кэш освещения, так как базовый цвет изменился
            self.current_item.invalidate_lighting_cache()
            self.set_object(self.current_item)  # Refresh palette
            self.on_change()

    # === Light callbacks ===
    def _on_light_position(self, axis: int, value: float):
        if self.current_item and self.current_type == 'light':
            # Используем сеттер для правильного обновления состояния
            pos = list(self.current_item.position)
            pos[axis] = value
            self.current_item.position = tuple(pos)
            self.on_change()

    def _on_light_direction(self, axis: int, value: float):
        if self.current_item and self.current_type == 'light':
            # Используем сеттер для правильного обновления состояния
            direction = list(self.current_item.direction)
            direction[axis] = value
            # Нормализуем направление перед установкой
            direction_arr = np.array(direction)
            length = np.linalg.norm(direction_arr)
            if length > 0:
                direction_arr = direction_arr / length
            self.current_item.direction = tuple(direction_arr)
            self.on_change()

    def _on_light_fov(self, value: float):
        if self.current_item and self.current_type == 'light':
            if hasattr(self.current_item, 'fov'):
                self.current_item.fov = value
            elif hasattr(self.current_item, '_half_fov_cos'):
                self.current_item._half_fov_cos = np.cos(np.radians(value / 2))
            self.current_item.set_moved(True)
            self.on_change()

    def _on_light_power(self, value: float):
        if self.current_item and self.current_type == 'light':
            # Обновляем power и помечаем свет как перемещенный для пересчета освещения
            self.current_item._power = value / 10
            self.current_item.set_moved(True)
            self.on_change()

    # === Camera callbacks ===
    def _on_camera_position(self, axis: int, value: float):
        if self.current_item and self.current_type == 'camera':
            # Используем сеттер для правильного обновления состояния
            pos = list(self.current_item.position)
            pos[axis] = value
            self.current_item.position = tuple(pos)
            self.on_change()

    def _on_camera_direction(self, axis: int, value: float):
        if self.current_item and self.current_type == 'camera':
            # Используем сеттер для правильного обновления состояния
            direction = list(self.current_item.direction)
            direction[axis] = value
            # Нормализуем направление перед установкой
            direction_arr = np.array(direction)
            length = np.linalg.norm(direction_arr)
            if length > 0:
                direction_arr = direction_arr / length
            self.current_item.direction = tuple(direction_arr)
            self.on_change()

    def _on_camera_fov(self, value: float):
        if self.current_item and self.current_type == 'camera':
            self.current_item._half_fov_cos = value
            self.current_item.fov = value
            self.on_change()

    # === Settings callbacks ===
    def _on_projection_scale(self, value: float):
        setattr(constants_module, 'PROJECTION_SCALE', int(value))
        self.on_change()

    def _on_near_plane(self, value: float):
        setattr(constants_module, 'NEAR_PLANE', value)
        self.on_change()

    def _on_mouse_sensitivity(self, value: float):
        setattr(constants_module, 'MOUSE_SENSITIVITY', int(value))
        self.on_change()

    def _on_move_speed(self, value: float):
        setattr(constants_module, 'MOVE_SPEED', value)
        self.on_change()

    def _on_vertical_speed(self, value: float):
        setattr(constants_module, 'VERTICAL_SPEED', value)
        self.on_change()

    def _on_min_light_power(self, value: float):
        setattr(constants_module, 'MIN_LIGHT_POWER', value)
        self.on_change()

    def _on_default_light_fov(self, value: float):
        setattr(constants_module, 'DEFAULT_LIGHT_FOV', value)
        self.on_change()

    def _on_light_falloff(self, value: float):
        setattr(constants_module, 'LIGHT_FALLOFF_MULTIPLIER', int(value))
        self.on_change()


class Editor:
    """
    Главный класс редактора.
    """

    def __init__(self, root: tk.Tk, objects: list[Object], canvas: tk.Canvas,
                 lights: list[BaseLight] | None = None, camera: Camera = None):
        self.root = root
        self.objects = objects if objects is not None else []
        self.lights = lights if lights is not None else []
        self.camera = camera
        self.canvas = canvas
        self.visible = False

        self.hierarchy = HierarchyPanel(root, self._on_select)
        self.inspector = InspectorPanel(root, self._on_change)

    def set_canvas(self, canvas: tk.Canvas):
        self.canvas = canvas

    def set_lights(self, lights: list[BaseLight] | None) -> None:
        self.lights = lights if lights is not None else []
        if self.visible:
            self.hierarchy.update(self.objects, self.lights)

    def toggle(self):
        self.visible = not self.visible
        if self.visible:
            self._show()
        else:
            self._hide()

    def _show(self):
        self.canvas.pack_forget()
        self.hierarchy.show()
        self.inspector.show()
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.hierarchy.update(self.objects, self.lights)

    def _hide(self):
        self.hierarchy.hide()
        self.inspector.hide()
        self.canvas.pack_forget()
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.hierarchy.deselect()
        self.inspector._show_empty()

    def _on_select(self, item_type: str, index: int):
        if item_type == 'object' and 0 <= index < len(self.objects):
            self.inspector.set_object(self.objects[index])
        elif item_type == 'light' and 0 <= index < len(self.lights):
            self.inspector.set_light(self.lights[index])
        elif item_type == 'camera' and self.camera:
            self.inspector.set_camera(self.camera)
        elif item_type == 'settings':
            self.inspector.set_settings()

    def _on_change(self):
        pass

    def update_objects(self, objects: list[Object]):
        self.objects = objects if objects is not None else []
        if self.visible:
            self.hierarchy.update(self.objects, self.lights)

    def deselect(self):
        self.hierarchy.deselect()
        self.inspector._show_empty()
