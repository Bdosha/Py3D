from core_engine.object import Object
from core_engine.utils import *
from .load_graphic import get_colors, load_lab, load_graphic


class Lab(Object):
    def get_color(self, poly):
        return get_colors(poly, max(poly[:, 2].max(), abs(poly[:, 2].min())))

    def __init__(self, position, rotate, graph, details: int, scaling=(1, 1, 1)):
        self.position = np.array(position, dtype=np.float32)
        self.Mx, self.My, self.Mz = create_matrix(rotate)
        self.details = details
        self.scale = np.array(scaling, dtype=np.float32) + 10 ** -10
        self.polys = load_lab(1, 1, details, graph)


class Graphic(Object):
    def get_color(self, poly):
        return get_colors(poly, max(poly[:, 2].max(), -poly[:, 2].min()))

    def __init__(self, position, rotate, z_func, details: int, scaling=(1, 1, 1)):
        self.position = np.array(position, dtype=np.float32)
        self.Mx, self.My, self.Mz = create_matrix(rotate)
        self.details = details
        self.scale = np.array(scaling, dtype=np.float32) + 1e-10
        self.polys = load_graphic(z_func, details, 5)
