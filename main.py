"""
Демонстрация 3D движка Py3D.

Пример использования движка с кубом, сферой и освещением.
Управление: WASD - движение, мышь - поворот, P - полноэкранный режим.
"""
import numpy as np

import core
import objects as obj


def main():
    """Точка входа в приложение."""

    # Создаём игрока (камеру от первого лица)
    player = core.Player(
        position=(-1, 0, 0),
        direction=(0, 1, 0)
    )

    # Источник света, привязанный к позиции игрока (фонарик)
    flashlight = core.Light(
        position=(0, 0, 0),
        direction=(0, 1, 0),
        fov=20,
        power=10
    )

    # Создаём объекты сцены
    cube = obj.Cube(
        position=(0, 10, 0),
        details=1,
        side=1,
        color=(255, 255, 255)
    )
    cube = obj.Model(model_path="objects/scene.gltf",
        position=(0, 10, 0),
        color=(255, 255, 255))

    # Куб с инвертированными нормалями (скайбокс)
    skybox = obj.Cube(
        position=(1, 20, 0),
        details=5,
        scaling=(1, 1, 1),
        color=(255, 255, 255),
        side=50,
        inverted=True
    )


    ground = obj.Surface(
        position=(0, 0, -5),
        details=10,
        scaling=(1, 1, 1),
        color=(255, 255, 255),
        side=40,
        inverted=True
    )
    # Список объектов для рендеринга
    objects = [cube, skybox]

    # Создаём сцену
    scene = core.Scene(
        player,
        screen_size=(800, 600),
        objects=objects,
        lights=[flashlight],
        show_fps=True,
        show_axes=True  # Индикатор осей координат
    )

    # Главный цикл рендеринга
    i = 1
    while True:
        # Обновляем позицию и направление "фонарика"
        flashlight.position = np.array(player.position.copy())
        flashlight.direction = player.direction.copy()

        cube.direction = np.array((i, i, i))
        i += 1
        # Рендерим кадр
        scene.render()


if __name__ == "__main__":
    main()
