"""
Демонстрация 3D движка Py3D.

Пример использования движка с кубом, сферой и освещением.
Управление: WASD - движение, мышь - поворот, P - полноэкранный режим.
"""

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
    
    # Куб с инвертированными нормалями (скайбокс)
    skybox = obj.Cube(
        position=(1, 40, 0),
        details=5,
        scaling=(0.3, 1, 0.3),
        color=(255, 255, 255),
        side=100,
        inverted=True  # Вместо RCube теперь используем inverted=True
    )
    
    # Список объектов для рендеринга
    objects = [cube, skybox]
    
    # Создаём сцену
    scene = core.Scene(
        player,
        screen_size=(800, 600),
        objects=objects,
        lights=[flashlight],
        show_fps=True
    )
    
    # Главный цикл рендеринга
    while True:
        # Обновляем позицию и направление "фонарика"
        scene.lights[0].position = scene.player.position.copy()
        scene.lights[0].direction = scene.player.direction.copy()
        
        # Рендерим кадр
        scene.render()


if __name__ == "__main__":
    main()
