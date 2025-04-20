import trimesh

from core_engine.object import Object
from core_engine.utils import *


def load_polygons_from_gltf(file_path):
    loaded = trimesh.load(file_path)

    polygons = []

    if isinstance(loaded, trimesh.Scene):
        for geometry in loaded.geometry.values():
            if isinstance(geometry, trimesh.Trimesh):
                for face in geometry.faces:
                    polygon = np.array([
                        geometry.vertices[face[0]],
                        geometry.vertices[face[1]],
                        geometry.vertices[face[2]]
                    ])
                    polygons.append(polygon)
    elif isinstance(loaded, trimesh.Trimesh):
        for face in loaded.faces:
            polygon = np.array([
                loaded.vertices[face[0]],
                loaded.vertices[face[1]],
                loaded.vertices[face[2]]
            ])
            polygons.append(polygon)
    else:
        raise ValueError("Загруженный файл не содержит поддерживаемых мешей.")

    return polygons


class Model(Object):
    def __init__(self, position, rotate, model: str, scaling: np.array):
        self.position = np.array(position, dtype=np.float32)
        self.Mx, self.My, self.Mz = create_matrix(rotate)
        self.scale = np.array(scaling) + 10 ** -10
        self.polys = load_polygons_from_gltf(model)

        for i in range(len(self.polys)):
            self.polys[i] = swap(self.polys[i])
