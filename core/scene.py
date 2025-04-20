import time

from .player import Player
from .screen import Screen
from .utils import *


class Scene:
    def __init__(self, player: Player, screen: Screen, objects: list, lights=(), show_fps=False):
        self.start = time.time()
        self.player = player
        self.objects = objects
        self.screen = screen
        self.lights = lights
        self.show_fps = show_fps

    def sort_polys(self, polys):
        distances = [np.linalg.norm(np.mean(poly[0], axis=0) - self.player.position) for poly in polys]

        sorted_indices = np.argsort(distances)[::-1]

        return [polys[i] for i in sorted_indices]

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
