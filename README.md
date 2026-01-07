# Py3D

Простой 3D движок на Python с софтверным рендерингом через tkinter.

## Особенности

- **Софтверный рендеринг** — не требует GPU, работает везде где есть Python и tkinter
- **Перспективная проекция** — реалистичное отображение 3D объектов
- **Освещение** — направленные точечные источники света с затуханием
- **Frustum и Backface Culling** — оптимизация отсечения невидимых полигонов
- **Управление от первого лица** — WASD + мышь

## Установка

```bash
pip install numpy trimesh
```

## Быстрый старт

```python
import core
import objects as obj

# Создаём игрока
player = core.Player(position=(0, 0, 0), direction=(0, 1, 0))

# Создаём объекты
cube = obj.Cube(position=(0, 10, 0), side=2, color=(255, 0, 0))
sphere = obj.Sphere(position=(5, 10, 0), details=10, color=(0, 255, 0))

# Создаём сцену
scene = core.Scene(
    player,
    screen_size=(800, 600),
    objects=[cube, sphere],
    show_fps=True
)

# Главный цикл
while True:
    scene.render()
```

## Управление

| Клавиша | Действие |
|---------|----------|
| W/S | Вперёд/Назад |
| A/D | Влево/Вправо |
| Space | Вверх |
| Z | Вниз |
| P | Полноэкранный режим |
| Мышь | Поворот камеры |

## Архитектура

### Core (Ядро)

- `Camera` — проекция 3D→2D, culling
- `Light` — источники освещения
- `Object` — ABC для всех 3D объектов
- `Player` — управление камерой
- `Scene` — объединение компонентов, рендеринг
- `Screen` — вывод через tkinter Canvas

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

```python
# Точечный направленный свет
light = core.Light(
    position=(10, 0, 10),
    direction=(0, 0, -1),
    fov=90,      # Угол конуса света
    power=15     # Мощность
)

scene = core.Scene(
    player,
    screen_size=(800, 600),
    objects=[cube],
    lights=[light]
)
```

## Структура проекта

```
Py3D/
├── core/
│   ├── __init__.py
│   ├── camera.py       # Камера и проекция
│   ├── constants.py    # Константы движка
│   ├── light.py        # Источники света
│   ├── object.py       # Базовый класс объектов (ABC)
│   ├── player.py       # Управление игроком
│   ├── scene.py        # Сцена и рендеринг
│   ├── screen.py       # Вывод на экран
│   ├── types.py        # Type aliases
│   └── utils.py        # Математические утилиты
├── objects/
│   ├── __init__.py
│   ├── cube.py         # Куб
│   ├── sphere.py       # Сфера
│   ├── surface.py      # Плоскость
│   ├── graphics.py     # Графики и параметрические поверхности
│   ├── load_graphic.py # Генераторы полигонов
│   └── model.py        # Загрузчик GLTF
├── main.py             # Демо
└── README.md
```

## Лицензия

MIT
