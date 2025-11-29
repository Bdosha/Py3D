import matplotlib.pyplot as plt
import numpy as np

import core.utils as utils


def get_color(poly, h):
    return (utils.mean(poly[:, 2]) + h) / 2 / h * 255


def get_colors(poly, h):
    return get_color(poly, h), 255 - get_color(poly, h), get_color(poly, h)


def spiral(A, B, U, V):
    X = (A + B * np.cos(V)) * np.cos(U)
    Y = (A + B * np.sin(V)) * np.sin(U)
    Z = B * np.sin(V) + A * U
    return X, Y, Z


def meb(A, B, U, V):
    X = (A + V * np.cos(U / 2)) * np.cos(U)
    Y = (A + V * np.cos(U / 2)) * np.sin(U)
    Z = B * np.sin(U / 2) * V
    return X, Y, Z


def tor(A, B, U, V):
    X = (A + B * np.cos(V)) * np.cos(U)
    Y = (A + B * np.cos(V)) * np.sin(U)
    Z = B * np.sin(V)
    return X, Y, Z


def screw(A, B, U, V):
    X = A * U * np.cos(U)
    Y = B * U * np.sin(U)
    Z = V
    return X, Y, Z


def sea(A, B, U, V):
    X = A * np.exp(B * V) * np.cos(V) * (1 + np.cos(U))
    Y = A * np.exp(B * V) * np.cos(V) * (1 + np.cos(U))
    Z = A * np.exp(B * V) * np.sin(U)


    return X, Y, Z


def get_info_lab(num):
    info = ([-2 * np.pi, np.pi * 2, -np.pi, np.pi, spiral, 1.5],
            [0, np.pi * 2, -0.5, 0.5, meb, 4],
            [0, np.pi * 2, 0, np.pi * 2, tor, 3],
            [0, np.pi * 4, -2, 2, screw, 0.7],
            [0, np.pi * 2, 0, np.pi * 6, sea, 1.5 * 1e-8])
    return info[num]


def load_lab(alpha, beta, details, lab):
    info = get_info_lab(lab)

    U, V = np.meshgrid(np.linspace(info[0], info[1], details), np.linspace(info[2], info[3], details), indexing='ij')
    X, Y, Z = info[4](alpha, beta, U, V)

    # X = (alpha + beta * np.cos(V)) * np.cos(U)
    # Y = (alpha + beta * np.cos(V)) * np.sin(U)
    # Z = beta * np.sin(V) + alpha * U

    return [(poly[0] * info[5], poly[1]) for poly in create_graphic(X, Y, Z, max(Z.max(), abs(-Z.min())), details)]


def load_graphic(func, details, far):
    u = np.linspace(-far, far, details)
    x, y = np.meshgrid(u, u, indexing='ij')
    z = func(x, y)
    # print(x, y, z)
    return create_graphic(x, y, z, far, details)


def create_graphic(x, y, z, far, details):
    z = np.clip(z, -far, far)

    tris1 = np.empty((details - 1, details - 1, 3, 3))
    tris2 = np.empty((details - 1, details - 1, 3, 3))

    tris1[:, :, 0] = np.stack([x[1:, 1:], y[1:, 1:], z[1:, 1:]], axis=-1)
    tris1[:, :, 1] = np.stack([x[:-1, 1:], y[:-1, 1:], z[:-1, 1:]], axis=-1)
    tris1[:, :, 2] = np.stack([x[1:, :-1], y[1:, :-1], z[1:, :-1]], axis=-1)

    tris2[:, :, 0] = np.stack([x[:-1, :-1], y[:-1, :-1], z[:-1, :-1]], axis=-1)
    tris2[:, :, 1] = np.stack([x[1:, :-1], y[1:, :-1], z[1:, :-1]], axis=-1)
    tris2[:, :, 2] = np.stack([x[:-1, 1:], y[:-1, 1:], z[:-1, 1:]], axis=-1)

    all_tris = np.vstack([
        tris1.reshape(-1, 3, 3),
        tris2.reshape(-1, 3, 3),
        np.flip(tris1, axis=2).reshape(-1, 3, 3),
        np.flip(tris2, axis=2).reshape(-1, 3, 3)
    ])

    return [(tri, (get_colors(tri, far))) for tri in all_tris if
            abs(tri[0, 2]) != far or abs(tri[1, 2]) != far or abs(tri[2, 2]) != far]


if __name__ == '__main__':
    # Фиксируем alpha и beta для одного графика
    alpha = 1
    beta = 1
    n = 300
    u = np.linspace(0, 4 * np.pi, n)
    v = np.linspace(0, 2 * np.pi, n)
    U, V = np.meshgrid(u, v)
    # # U,V = u,v
    # X = alpha * U * np.cos(U)
    # Y = beta * U * np.sin(U)
    # Z = V

    X = (alpha + beta * np.cos(V)) * np.cos(U)
    Y = (alpha + beta * np.cos(V)) * np.sin(U)
    Z = beta * np.sin(V) + alpha * u

    print(X, Y, Z, sep='\n')

    # print(load_graphic(1,2,5))
    #
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    surf = ax.plot_surface(X, Y, Z, cmap='viridis', alpha=0.8)

    #
    # def update(frame):
    #     ax.view_init(elev=30, azim=frame)  # elev = угол наклона, azim = азимут
    #     return surf,
    #
    #
    # # Создаем анимацию
    # ani = FuncAnimation(
    #    fig,
    #    update,
    #    frames=np.arange(0, 360, 1),  # Полный оборот (0° до 360°)
    #    interval=50,  # Задержка между кадрами (мс)
    #    blit=True
    # )
    ax.view_init(elev=20, azim=50)  # elev = угол наклона, azim = азимут

    plt.show()
