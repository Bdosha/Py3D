"""
Демонстрация 3D движка Py3D.

Пример использования движка с кубом, сферой и освещением.
Управление: WASD - движение, мышь - поворот, P - полноэкранный режим.
"""
from core import App
from levels import colored_lighting, flashlight_demo, model_demo



if __name__ == "__main__":
    index = input("Выбери демку:\n"
                  "1. Цветное освещение\n"
                  "2. Фонарик\n"
                  "3. Подгрузка моделей\n- ")
    if index == "1":
        app = colored_lighting()
    elif index == "2":
        app = flashlight_demo()
    elif index == "3":
        app = model_demo()
    else:
        app = App()
    app.run()