from core.object import Object
from core.utils import *


class Surface(Object):
    def get_color(self, poly):
        return self.color

    def __init__(self, position=(0, 0, 0), side=10, rotate=(0, 0, 0), details=1, scaling=(1, 1, 1),
                 color=(255, 255, 255), duo=False):
        self.position = np.array(position, dtype=np.float32)
        self.side = side
        self.Mx, self.My, self.Mz = create_matrix(rotate)
        self.details = details
        self.scale = np.array(scaling, dtype=np.float32) + 10 ** -10
        self.color = color
        half_side = side / 2

        temp = np.linspace(-half_side, half_side, details)
        self.polys = []

        for i in range(1, details):
            for j in range(1, details):
                first_poly = np.array([[temp[i - 1], temp[j - 1], 0],
                                       [temp[i], temp[j - 1], 0],
                                       [temp[i - 1], temp[j], 0]])
                self.polys.append(first_poly.copy())
                if duo:
                    self.polys.append(-swap(first_poly))

                # new_poly = swap(first_poly)
                new_poly = np.array([[temp[i], temp[j], 0],
                                     [temp[i-1], temp[j], 0],
                                     [temp[i], temp[j-1], 0]])
                # new_poly[0] += (new_poly[2] - new_poly[0]) + (new_poly[1] - new_poly[0])
                self.polys.append(new_poly)
                if duo:
                    self.polys.append(-swap(new_poly))

        for i in range(len(self.polys)):
            self.polys[i] = (self.polys[i], self.color)
