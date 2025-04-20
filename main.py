import numpy as np

import core
import objects as obj

player = core.Player(position=(-1, 0, 0), direction=(0, 1, -0))

light = core.Light((20, 0, 20), (0, 0.3, -1), 120, power=20)
light2 = core.Light((0, 0, 0), (0, 1, 0), 20, 10)

cube = obj.Cube(position=(0, 10, 0), details=1, side=1, color=(255, 255, 255))

rcube = obj.RCube(position=(1, 40, 0), details=5, scaling=(0.3, 1, 0.3), color=(255, 255, 255), side=100)

sphere = obj.Sphere(position=(1, 30, 0), details=10, scaling=(2, 1, 2), color=(255, 255, 255))

surface = obj.Surface(side=20, position=(1, 30, -3), details=8, rotate=(0, 180, 0))


def func(x, y):
    return np.cos(x)


graph = obj.Graphic(position=(0, 30, 0), details=50, scaling=(1, 1, 1), rotate=(0, 0, 0), z_func=func)
lab = obj.Lab(position=(0, 50, 0), details=10, scaling=(1, 1, 1), rotate=(0, 0, 0), graph=1)
# objects = [obj.Lab(position=(i * 12, 60, 0), details=10, scaling=(1, 1, 1), rotate=(0, 0, 0), graph=i) for i in range(5)]
objects = [cube, rcube]
# objects = [cube, surface]
# objects = [obj.Lab(position=(12 - i * 10, 50, 0), details=20, scaling=(1, 1, 1), rotate=(0, 0, 0), graph=i) for i in range( 4)]
scene = core.Scene(player,
                   (800, 600),
                   objects=objects,

                   lights=[
                       # light,
                       light2
                   ],
                   show_fps=True
                   )

i = 0
while True:
    scene.lights[0].position = scene.player.position
    scene.lights[0].direction = scene.player.direction


    i -= 5

    scene.render()

