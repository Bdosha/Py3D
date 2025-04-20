import numpy as np


def to_radians(degrees):
    return (degrees * np.pi / 180) % (2 * np.pi)


def get_len(vector):
    return np.sqrt(sum(vector ** 2))


def get_dist(dot1, dot2):
    return get_len(dot1 - dot2)


def set_len(vector, length):
    if get_len(vector) == 0:
        return vector
    return vector * length / get_len(vector)


def set_ort(vector):
    return set_len(vector, 1)


def create_matrix(rotate):
    rotate = np.radians(rotate)
    cos = np.cos(rotate)
    sin = np.sin(rotate)

    Mx = np.array([
        [1, 0, 0],
        [0, cos[0], -sin[0]],
        [0, sin[0], cos[0]]
    ])

    My = np.array([
        [cos[1], 0, sin[1]],
        [0, 1, 0],
        [-sin[1], 0, cos[1]]
    ])

    Mz = np.array([
        [cos[2], -sin[2], 0],
        [sin[2], cos[2], 0],
        [0, 0, 1]
    ])

    return Mx, My, Mz


def get_angle(vector1, vector2):
    return np.acos(np.dot(set_ort(vector1), set_ort(vector2)))


def angle_between_vectors(a, b):
    # Вычисляем скалярное произведение векторов
    dot_product = np.dot(a, b)

    # Находим нормы (длины) векторов
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)

    # Вычисляем косинус угла и ограничиваем значение для избежания ошибок округления
    cos_theta = dot_product / (norm_a * norm_b)
    cos_theta = np.clip(cos_theta, -1.0, 1.0)

    # Находим угол в радианах через арккосинус
    theta = np.arccos(cos_theta)

    return theta


def to_new_system(Mx, My, Mz, position, vectors):
    return vectors @ Mx @ My @ Mz + position


def swap(poly):
    temp = poly.copy()
    temp[1], temp[2] = temp[2].copy(), temp[1].copy()
    return temp


def to_float(poly):
    return [(float(i[0]), float(i[1])) for i in list(poly)]


def bind(root, camera):
    root.bind('<w>', camera.go)
    root.bind('<s>', camera.go)
    root.bind('<d>', camera.go)
    root.bind('<a>', camera.go)

    root.bind('<space>', camera.go)
    root.bind('<z>', camera.go)

    root.bind('<Up>', camera.turn)
    root.bind('<Down>', camera.turn)
    root.bind('<Right>', camera.turn)
    root.bind('<Left>', camera.turn)


    root.bind("<Motion>", camera.turn)

def mean(arr):
    return sum(arr) / len(arr)
