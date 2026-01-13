"""
Демонстрация 3D движка Py3D.

Пример использования движка с кубом, сферой и освещением.
Управление: WASD - движение, мышь - поворот, P - полноэкранный режим.
"""

from levels import colored_lighting, flashlight_demo, model_demo



if __name__ == "__main__":

    app = model_demo()
    app.run()