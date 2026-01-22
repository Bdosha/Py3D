"""
Главный файл для запуска демонстраций Py3D.

Выберите демонстрацию, раскомментировав соответствующий код.
"""

from core import App
from levels.feature import colored_lighting, flashlight_demo, model_demo
from levels.benchmarks import performance_test
from levels.benchmarks.performance_test import get_benchmark_app
from levels import main_demo

if __name__ == "__main__":
    index = input("Выбери демку:\n"
                  "1. Цветное освещение\n"
                  "2. Фонарик\n"
                  "3. Подгрузка моделей\n"
                  "4. Тест производительности\n"
                  "5. Финальная демка\n- ")
    #
    # index = "5"
    
    if index == "1":
        app = colored_lighting()
    elif index == "2":
        app = flashlight_demo()
    elif index == "3":
        app = model_demo()
    elif index == "4":
        performance_test()
        app = get_benchmark_app(120)
    elif index == "5":
        app = main_demo()
    else:
        app = App()
    
    app.run()
