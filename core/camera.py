import numpy

from .utils import *


class Camera:
    def __init__(self, position=(0, 0, 0), direction=(0, 1, 0), FOV=90):
        self.move_to(position, direction, FOV)

    def move_to(self, position=(0, 0, 0), direction=(0, 1, 0), FOV=90):
        if all([i == 0 for i in direction]):
            direction = (0, 1, 0)

        self.FOV = to_radians(180 - FOV)
        self.focus = 1
        self.position = np.array(position, dtype=np.float32)
        self.direction = set_ort(np.array(direction, dtype=np.float32))
        self.view_dot = self.position + self.direction * (self.focus / 2 * np.tan(self.FOV / 2))

    def is_visible(self, poly):
        a, b, c = poly
        center = (a + b + c) / 3

        vec = center - self.position
        # print(vec, self.direction)
        if get_angle(vec, self.direction) > self.FOV / 2:
            return False
        cross = set_ort(np.cross(b - a, c - a))

        if np.dot(cross, vec) < 0:
            return False
        return True

    def to_screen(self, dot: np.array):
        a = np.cross(self.direction, np.array([0, 0, 1]))
        b = np.cross(a, self.direction)
        M = np.array([a, b, self.direction]).T
        P = self.view_dot.T

        try:
            ans = np.linalg.inv(M)
        except numpy.linalg.LinAlgError:
            ans = np.linalg.inv(M + 1e-5)

        return (ans @ (dot.T - P.T))[:2] * (2500 / self.focus)

    def get_camera_u(self, objc: np.array, screen: np.array):
        obj = objc - self.position

        A = np.array([self.direction,
                      [obj[1], -obj[0], 0],
                      [obj[2], 0, -obj[0]]])

        b = np.array([[(self.view_dot * self.direction).sum()],
                      [obj[1] * self.position[0] - obj[0] * self.position[1]],
                      [obj[2] * self.position[0] - obj[0] * self.position[2]]])
        try:
            x = np.linalg.solve(A, b).T[0]
        except np.linalg.LinAlgError:
            x = np.linalg.solve(A + 10e-10, b + 10e-10).T[0]

        to_screen = self.to_screen(x)
        to_screen[1] *= -1
        return to_screen + (screen / 2)

    def to_canvas(self, poly, screen):
        return [self.get_camera_u(poly[i], screen) for i in range(3)]

