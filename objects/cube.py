from core_engine.object import Object
from core_engine.utils import *


class Cube(Object):
    def get_color(self, poly):
        return self.color

    def __init__(self, position=(0, 0, 0), side=10, rotate=(0, 0, 0), details=1, scaling=(1, 1, 1),
                 color=(255, 255, 255)):
        self.position = np.array(position, dtype=np.float32)
        self.side = side
        self.Mx, self.My, self.Mz = create_matrix(rotate)
        details += 1
        self.details = details
        self.scale = np.array(scaling, dtype=np.float32) + 10 ** -10
        self.color = color
        half_side = side / 2

        temp = np.linspace(-half_side, half_side, details )
        self.polys = []

        for i in range(1, details):
            for j in range(1, details):
                first_poly = np.array([[temp[i - 1], temp[j - 1], half_side],
                                       [temp[i - 1], temp[j], half_side],
                                       [temp[i], temp[j - 1], half_side]])
                self.polys.append(first_poly.copy())
                self.polys.append(-swap(first_poly))
                new_poly = np.array([[temp[i], temp[j], half_side],
                                     [temp[i], temp[j - 1], half_side],
                                     [temp[i - 1], temp[j], half_side]])

                self.polys.append(new_poly)
                self.polys.append(-swap(new_poly))
                self.polys.append(self.rotate_to(first_poly, (0, 90, 0)))
                self.polys.append(self.rotate_to(new_poly, (0, 90, 0)))
                self.polys.append(self.rotate_to(first_poly, (0, -90, 0)))
                self.polys.append(self.rotate_to(new_poly, (0, -90, 0)))
                self.polys.append(self.rotate_to(first_poly, (90, 0, 0)))
                self.polys.append(self.rotate_to(new_poly, (90, 0, 0)))
                self.polys.append(self.rotate_to(first_poly, (-90, 0, 0)))
                self.polys.append(self.rotate_to(new_poly, (-90, 0, 0)))

        for i in range(len(self.polys)):
            self.polys[i] = (self.polys[i], self.color)
