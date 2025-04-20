import time
import tkinter as tk

from .player import Player
from .screen import Screen
from .utils import *


class Scene:
    def __init__(self, player: Player, screen: (int, int), objects: list, lights=(), show_fps=False, fullscreen=False):
        self.root = tk.Tk()
        # self.root.resizable(False, False)
        self.root.config(cursor="none", )
        self.start = time.time()
        player.screen = np.array([screen[0], screen[1]])
        player.last = player.screen / 2
        self.player = player
        self.objects = objects
        self.screen = Screen(self.root, screen[0], screen[1])
        self.old_screen = screen
        self.lights = lights
        self.show_fps = show_fps
        self.bind()

        self.fullscreen = fullscreen
        self.root.attributes("-fullscreen", fullscreen)

    def set_fullscreen(self, event):
        self.fullscreen = not self.fullscreen
        print(self.fullscreen)
        self.root.attributes("-fullscreen", self.fullscreen)

        size = [self.old_screen, (self.root.winfo_screenwidth(), self.root.winfo_screenheight())][self.fullscreen]
        print(size)
        self.player.screen = np.array([size[0], size[1]])

        self.screen.canvas.destroy()
        self.screen = Screen(self.root, size[0], size[1])

    def bind(self):
        self.root.bind('<w>', self.player.go)
        self.root.bind('<s>', self.player.go)
        self.root.bind('<d>', self.player.go)
        self.root.bind('<a>', self.player.go)

        self.root.bind('<space>', self.player.go)
        self.root.bind('<z>', self.player.go)

        self.root.bind('<Up>', self.player.turn)
        self.root.bind('<Down>', self.player.turn)
        self.root.bind('<Right>', self.player.turn)
        self.root.bind('<Left>', self.player.turn)

        self.root.bind("<Motion>", self.player.turn)
        self.root.bind("<p>", self.set_fullscreen)

    def sort_polys(self, polys):
        distances = [np.linalg.norm(np.mean(poly[0], axis=0) - self.player.position) for poly in polys]

        sorted_indices = np.argsort(distances)[::-1]

        return [polys[i] for i in sorted_indices]

    def tags(self):
        for obj in self.objects:
            pass

    def render(self):
        self.start = time.time()
        self.screen.root.update()
        self.screen.clear()

        to_draw = []
        all_polys = []
        for obj in self.objects:
            all_polys += obj.to_draw(self.player.camera.is_visible)
        all_polys = self.sort_polys(all_polys)

        for poly in all_polys:
            to_draw.append([self.player.camera.to_canvas(poly[0], self.screen.screen), poly[1]])

            if to_draw[-1]:
                if not self.lights:
                    to_draw[-1].append(None)
                    continue
                to_draw[-1].append(0)
                for light in self.lights:
                    to_draw[-1][-1] += light.get_color(poly[0])
                    to_draw[-1][-1] = min(1, to_draw[-1][-1])

        self.screen.multy_draw(to_draw)
        if self.show_fps:
            self.screen.draw_fps(1 / (time.time() - self.start))
