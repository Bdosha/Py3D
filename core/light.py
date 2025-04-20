from .utils import *


class Light:
    def __init__(self, position: tuple[float, float, float], direction: tuple[float, float, float], FOV=90, power=1):
        self.position = np.array(position, dtype=np.float32)
        self.direction = set_ort(np.array(direction, dtype=np.float32))
        self.FOV = to_radians(FOV)
        self.power = max(8, power) / 10

    def get_color(self, poly):
        a, b, c = poly
        center = (a + b + c) / 3
        cross = set_ort(np.cross(b - a, c - a))
        vec = set_ort(center - self.position)

        ans = np.dot(cross, vec)

        if get_angle(vec, self.direction) > self.FOV / 2:
            ans = (ans / get_angle(vec, self.direction) * self.FOV / 2) ** self.power

        return max(0, ans * ((self.power * 15) / get_len(center - self.position)))
