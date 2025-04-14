import tkinter as tk

import numpy as np

import core_engine as core
import objects as obj

root = tk.Tk()

root.resizable(False, False)
root.config(cursor="none")
screen = core.Screen(root, 800, 600)

player = core.Player(screen, position=(25.2, 0, 0))

core.bind(root, player)

light = core.Light((20, 0, 20), (0, 0.3, -1), 120, power=20)
light2 = core.Light((0, 0, 0), (0, 1, 0), 20, 20)

cube = obj.Cube(position=(25, 10, 0), details=1, side=1, color=(255, 255, 255))

rcube = obj.RCube(position=(25, 60, 0), details=5, scaling=(0.3, 1, 0.3), color=(255, 255, 255), side=200)

sphere = obj.Sphere(position=(1, 40, 0), details=10, scaling=(2, 1, 2), color=(255, 255, 255))

surface = obj.Surface(side=10, position=(0, 10, 0), details=16, rotate=(90, 0, 0))


def func(x, y):
    return np.cos(x)


graph = obj.Graphic(position=(0, 30, 0), details=50, scaling=(1, 1, 1), rotate=(0, 0, 0), z_func=func)
lab = obj.Lab(position=(0, 50, 0), details=10, scaling=(1, 1, 1), rotate=(0, 0, 0), graph=1)
# objects = [obj.Lab(position=(i * 12, 60, 0), details=10, scaling=(1, 1, 1), rotate=(0, 0, 0), graph=i) for i in range(5)]
objects = [rcube, cube]
scene = core.Scene(player,
                   screen,
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

    cube.to_rotate((i, i, i))

    i += 0.5

    scene.render()

# TODO Цвет Размеры, источники света Точность света ООП ФПС График Лаба


# TODO затухание света
