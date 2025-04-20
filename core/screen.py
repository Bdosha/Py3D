import tkinter as tk

from .utils import *


class Screen:

    def __init__(self, window: tk.Tk, width: int, height: int):
        self.root = window
        self.screen = np.array([width, height])
        self.canvas = tk.Canvas(self.root, width=self.screen[0], heigh=self.screen[1], bg='#adfff6', cursor='none')
        self.canvas.pack()

    def draw(self, poly, base_color, intensity):
        if intensity is None:
            intensity = 1 - 1e-10
        # print(intensity)
        r = int(base_color[0] * intensity)
        g = int(base_color[1] * intensity)
        b = int(base_color[2] * intensity)
        color = f'#{r:02x}{g:02x}{b:02x}'
        # print(poly)
        self.canvas.create_polygon(to_float(poly), outline=color, fill=color)

    def clear(self):
        self.canvas.delete("all")

    def draw_fps(self, fps):
        self.canvas.create_text(
            0, 0,
            text=f"\n     FPS: {fps:.2f}",
            fill="red",
            font=("Arial", 20, "bold"),
            anchor="nw")

    def multy_draw(self, polys):
        self.canvas.delete("all")

        for poly, base_color, light in polys:
            if poly is None:
                continue

            self.draw(poly, base_color, light)
