from .utils import *
class Object:
    def to_system(self, angle):
        return to_new_system(self.Mx, self.My, self.Mz, self.position, angle)

    def rotate_to(self, angle, rotate):
        Xb, Yb, Zb = create_matrix(rotate)

        return to_new_system(Xb, Yb, Zb, np.array([0, 0, 0]), angle)

    def move_to(self, position):
        self.position = position

    def to_rotate(self, rotate):
        self.Mx, self.My, self.Mz = create_matrix(rotate)

    def to_draw(self, check):
        polys = []
        for i in range(len(self.polys)):
            # print(check(self.polys[i]))
            temp = self.to_system(self.polys[i][0] * self.scale)
            if check(temp):
                # polys.append((temp, (self.get_color(temp))))
                polys.append((temp, self.polys[i][1]))

        return polys
