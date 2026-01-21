from core import App
from levels.feature import colored_lighting, flashlight_demo, model_demo
from levels.benchmarks import performance_test
from levels.benchmarks.performance_test import get_benchmark_app
if __name__ == "__main__":
    index = input("Выбери демку:\n"
                  "1. Цветное освещение\n"
                  "2. Фонарик\n"
                  "3. Подгрузка моделей\n"
                  "4. Тест производительности\n- ")
    #
    # index = "2"
    if index == "1":
        app = colored_lighting()
    elif index == "2":
        app = flashlight_demo()
    elif index == "3":
        app = model_demo()
    if index == "4":
        performance_test()
        app = get_benchmark_app(120)
    else:
        app = App()
    app.run()
