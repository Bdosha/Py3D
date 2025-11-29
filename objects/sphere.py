from core.object import Object
from core.utils import *


class Sphere(Object):
    def get_color(self, poly):
        return self.color

    def __init__(self, position=(0, 0, 0), rotate=(0, 0, 0), details=8, scaling=(1, 1, 1),
                 color=(255, 255, 255)):
        self.position = np.array(position, dtype=np.float32)
        self.Mx, self.My, self.Mz = create_matrix(rotate)
        self.details = max(details, 3)
        self.scale = np.array(scaling, dtype=np.float32) * 5 + 10 ** -10
        self.color = color

        self.polys = []

        vertices = []
        phi_steps = 2 *  self.details
        theta_steps =  self.details

        for i in range(theta_steps + 1):
            theta = i * np.pi / theta_steps
            sin_theta = np.sin(theta)
            cos_theta = np.cos(theta)

            for j in range(phi_steps):
                phi = j * 2 * np.pi / phi_steps
                sin_phi = np.sin(phi)
                cos_phi = np.cos(phi)

                x = sin_theta * cos_phi
                y = sin_theta * sin_phi
                z = cos_theta
                vertices.append(np.array([x, y, z]))

        # Генерация треугольников
        for i in range(theta_steps):
            for j in range(phi_steps):
                next_j = (j + 1) % phi_steps

                # Индексы вершин текущего и следующего кольца
                i0 = i * phi_steps + j
                i1 = i * phi_steps + next_j
                i2 = (i + 1) * phi_steps + j
                i3 = (i + 1) * phi_steps + next_j

                if i != 0:  # Верхние треугольники
                    self.polys.append((
                        np.array([vertices[i0], vertices[i1], vertices[i2]]),
                        self.color
                    ))
                if i != theta_steps - 1:  # Нижние треугольники
                    self.polys.append((
                        np.array([vertices[i1], vertices[i3], vertices[i2]]),
                        self.color
                    ))
