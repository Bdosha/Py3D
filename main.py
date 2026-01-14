from core import App
from levels import colored_lighting, flashlight_demo, model_demo

if __name__ == "__main__":
    index = input("Выбери демку:\n"
                  "1. Цветное освещение\n"
                  "2. Фонарик\n"
                  "3. Подгрузка моделей\n- ")
    #
    # index = "2"
    if index == "1":
        app = colored_lighting()
    elif index == "2":
        app = flashlight_demo()
    elif index == "3":
        app = model_demo()
    else:
        app = App()
    app.run()

