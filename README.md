# Py3D

Простой 3D движок на Python с софтверным рендерингом через tkinter.

## Особенности

- **Софтверный рендеринг** — не требует GPU, работает везде где есть Python и tkinter
- **Перспективная проекция** — реалистичное отображение 3D объектов
- **Освещение** — направленные точечные источники света с затуханием и цветным освещением
- **Frustum и Backface Culling** — оптимизация отсечения невидимых полигонов
- **Управление от первого лица** — WASD + мышь
- **Редактор сцены** — встроенный GUI для управления объектами и источниками света
- **Система скриптов** — возможность создания динамических сцен через RenderScript

## Установка

```bash
pip install -r requirements.txt
```

Или вручную:

```bash
pip install numpy trimesh
```

> **Примечание:** `trimesh` требуется только для загрузки GLTF/GLB моделей. Если вы не планируете загружать модели, можно установить только `numpy`.

## Быстрый старт

### Базовый пример

```python
import core
from core import obj

# Создаём игрока
player = core.Player(position=(0, 0, 0), direction=(0, 1, 0))

# Создаём объекты
cube = obj.Cube(position=(0, 10, 0), side=2, color=(255, 0, 0))
sphere = obj.Sphere(position=(5, 10, 0), details=10, color=(0, 255, 0))

# Создаём источник света
light = core.Light(
    position=(10, 0, 10),
    color=(255, 255, 255),  # Цвет света (RGB)
    power=15
)

# Создаём сцену
scene = core.Scene(
    player,
    screen_size=(800, 600),
    objects=[cube, sphere],
    lights=[light],
    show_fps=True
)

# Главный цикл
while True:
    scene.render()
```

### Использование App и RenderScript

Для более сложных сцен с динамическим поведением используйте систему скриптов:

```python
import core
from core import obj
from core.app import App, RenderScript

class MyScript(RenderScript):
    def init(self, scene: core.Scene):
        # Инициализация при старте
        cube = obj.Cube(position=(0, 10, 0), side=2)
        scene.objects.append(cube)
        
    def run(self, scene: core.Scene):
        # Выполняется каждый кадр
        # Можно изменять объекты, источники света и т.д.
        pass

# Создаём приложение
scene = core.Scene(core.Player())
app = App(scene, MyScript())
app.run()
```

Примеры использования App можно найти в папке `levels/`.

## Управление

| Клавиша | Действие |
|---------|----------|
| W/S | Вперёд/Назад |
| A/D | Влево/Вправо |
| Space | Вверх |
| Z | Вниз |
| P | Полноэкранный режим |
| Tab | Переключить редактор сцены |
| Escape | Снять выделение объекта |
| Мышь | Поворот камеры |

## Архитектура

### Core (Ядро)

- `Camera` — проекция 3D→2D, culling
- `Light` — источники освещения
- `Object` — ABC для всех 3D объектов
- `Player` — управление камерой
- `Scene` — объединение компонентов, рендеринг
- `Screen` — вывод через tkinter Canvas
- `App` — обёртка для работы со скриптами рендеринга
- `RenderScript` — базовый класс для скриптов сцены
- `Editor` — GUI редактор для управления объектами и источниками света
- `LightingSystem` — система управления освещением с кэшированием

### Objects (Объекты)

| Класс | Описание |
|-------|----------|
| `Cube` | Куб с настраиваемой детализацией |
| `Sphere` | Сфера (UV-сфера) |
| `Surface` | Плоскость |
| `Graphic` | График функции z=f(x,y) |
| `ParametricSurface` | Тор, спираль, лента Мёбиуса и др. |
| `Model` | Загрузка GLTF/GLB моделей |

### Инверсия нормалей

Любой объект можно инвертировать (нормали внутрь) для создания скайбоксов:

```python
skybox = obj.Cube(
    position=(0, 0, 0),
    side=100,
    inverted=True  # Нормали направлены внутрь
)
```

## Примеры объектов

### Параметрические поверхности

```python
# Тор
torus = obj.ParametricSurface(
    position=(0, 20, 0),
    surface_type=obj.ParametricSurface.TORUS,
    details=20
)

# Лента Мёбиуса
mobius = obj.ParametricSurface(
    position=(0, 30, 0),
    surface_type=obj.ParametricSurface.MOBIUS,
    details=30
)
```

### График функции

```python
import numpy as np

def wave(x, y):
    return np.sin(x) * np.cos(y)

graph = obj.Graphic(
    position=(0, 20, 0),
    z_func=wave,
    details=50
)
```

### Загрузка модели

```python
model = obj.Model(
    model_path="model.gltf",
    position=(0, 10, 0),
    scaling=(0.1, 0.1, 0.1)
)
```

## Освещение

### Базовое освещение

```python
# Точечный направленный свет
light = core.Light(
    position=(10, 0, 10),
    direction=(0, 0, -1),
    color=(255, 255, 255),  # Белый свет
    fov=90,                 # Угол конуса света (в градусах)
    power=15                # Мощность
)

scene = core.Scene(
    player,
    screen_size=(800, 600),
    objects=[cube],
    lights=[light]
)
```

### Цветное освещение

Источники света поддерживают цветное освещение (RGB):

```python
# Красный свет
red_light = core.Light(
    position=(10, 0, 10),
    color=(255, 0, 0),
    power=15
)

# Зелёный свет
green_light = core.Light(
    position=(-10, 0, 10),
    color=(0, 255, 0),
    power=15
)

# Синий свет
blue_light = core.Light(
    position=(0, 0, 10),
    color=(0, 0, 255),
    power=15
)
```

## Редактор сцены

Встроенный редактор позволяет управлять объектами и источниками света в реальном времени:

- **Hierarchy** — список всех объектов и источников света на сцене
- **Inspector** — редактирование свойств выбранного элемента (позиция, поворот, масштаб, цвет)
- **Настройки освещения** — управление параметрами источников света

Откройте редактор нажатием `Tab` во время работы приложения.

## Структура проекта

```
Py3D/
├── core/
│   ├── __init__.py
│   ├── app.py              # App и RenderScript
│   ├── object.py           # Базовый класс объектов (ABC)
│   ├── scene.py            # Сцена и рендеринг
│   ├── screen.py           # Вывод на экран
│   ├── objects/
│   │   ├── __init__.py
│   │   ├── camera.py       # Камера и проекция
│   │   ├── light.py        # Источники света
│   │   ├── lighting.py     # Система освещения
│   │   ├── player.py       # Управление игроком
│   │   └── bodies/
│   │       ├── cube.py         # Куб
│   │       ├── sphere.py       # Сфера
│   │       ├── surface.py      # Плоскость
│   │       ├── graphics.py     # Графики и параметрические поверхности
│   │       ├── load_graphic.py # Генераторы полигонов
│   │       └── model.py        # Загрузчик GLTF
│   └── tools/
│       ├── __init__.py
│       ├── constants.py    # Константы движка
│       ├── editor.py       # Редактор сцены
│       ├── types.py        # Type aliases
│       └── utils.py        # Математические утилиты
├── levels/                 # Примеры сцен
│   ├── colored_lighting.py # Пример с цветным освещением
│   ├── spining_model.py    # Пример с вращающейся моделью
│   └── ...
├── main.py                 # Демо
└── README.md
```

## Примеры

В папке `levels/` находятся примеры использования движка:

- `colored_lighting.py` — демонстрация цветного освещения с движущимися источниками света
- `spining_model.py` — пример загрузки и анимации GLTF модели
- `old_flashlight.py` — пример использования фонарика

Запустите любой пример:

```bash
python levels/colored_lighting.py
```

## Лицензия

MIT
