from scipy.linalg import signm

from .camera import Camera
from .utils import *


class Player:
    def __init__(self, screen, position=(0, 0, 0), direction=(0, 1, 0), FOV=90):
        if all([i == 0 for i in direction]):
            direction = (0, 1, 0)
        self.screen = np.array([screen.width, screen.height])
        self.camera = Camera(position, direction, FOV)
        self.position = np.array(position, dtype=np.float32)
        self.direction = set_ort(np.array(direction, dtype=np.float32))
        self.FOV = FOV
        self.last = np.array([0, 0])
        self.warping = False

    def go(self, event):
        print(event.char)
        if event.char in ["w", "s"]:
            addable = self.direction.copy()
            addable[2] = 0
            addable *= [1, -1][event.char == 's']

        elif event.char in ["a", "d"]:
            addable = np.cross(self.direction, np.array([0, 0, 1])) * [1, -1][event.char == 'a']

        else:
            addable = np.array([0, 0, 1]) * 0.8 * [1, -1][event.char != ' ']

        self.position += set_ort(addable) / 10
        self.camera.move_to(self.position, self.direction, self.FOV)

    def turn(self, event):
        print(event.state)
        cursor = np.array([event.x, event.y]) - self.screen / 2
        cursor[1] *= -1
        if abs(cursor[0]) > self.screen[0] / 2 or abs(cursor[1]) > self.screen[1] / 2 or event.state == 0:
            self.last = cursor

            return

        delta = (cursor - self.last)
        self.last = cursor
        a = np.cross(self.direction, np.array([0, 0, 1]))
        b = np.cross(a, self.direction)
        a /= get_len(a)
        b /= get_len(b)
        turning = (a * delta[0] + b * delta[1]) / (700 / sum(abs(delta / 10)))
        self.direction += turning

        self.direction /= np.sqrt((self.direction ** 2).sum())
        self.camera.move_to(self.position, self.direction, self.FOV)
