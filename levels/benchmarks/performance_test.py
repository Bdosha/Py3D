from typing import Callable, override
from datetime import datetime
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

import core
from core import obj, Scene
from core.app import AppScript, App, FrameStats
from core.app import Settings


def generate_report(stats_history: list[FrameStats]):
    """Генерирует отчет с метриками и графиками."""
    if not stats_history:
        return

    # Создаем папку для результатов
    results_dir = Path(__file__).parent / "results"
    results_dir.mkdir(exist_ok=True)

    # Генерируем имя файла с timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    graph_path = results_dir / f"performance_{timestamp}.png"

    # Извлекаем данные
    fps = [s.fps for s in stats_history]
    polygons = [s.polygons_count for s in stats_history]
    # render_time в app.py вычисляется неправильно, используем total_time
    render_time = [s.total_time for s in stats_history]
    frames = list(range(len(stats_history)))

    # Вычисляем статистику
    stats = {
        'fps_avg': np.mean(fps),
        'fps_min': np.min(fps),
        'fps_max': np.max(fps),
        'polygons_avg': np.mean(polygons),
        'polygons_max': np.max(polygons),
        'render_time_avg': np.mean(render_time),
        'render_time_max': np.max(render_time),
        'total_frames': len(stats_history),
        'final_polygons': polygons[-1] if polygons else 0,
    }

    # Вывод в консоль
    print("\n" + "=" * 50)
    print("БЕНЧМАРК ПРОИЗВОДИТЕЛЬНОСТИ РЕНДЕРИНГА")
    print("=" * 50)
    print(f"\nВсего кадров: {stats['total_frames']}")
    print(f"Финальное количество полигонов: {stats['final_polygons']}")
    print(f"\nFPS:")
    print(f"  Среднее: {stats['fps_avg']:.2f}")
    print(f"  Минимум: {stats['fps_min']:.2f}")
    print(f"  Максимум: {stats['fps_max']:.2f}")
    print(f"\nПолигоны:")
    print(f"  Среднее: {stats['polygons_avg']:.0f}")
    print(f"  Максимум: {stats['polygons_max']}")
    print(f"\nВремя рендеринга:")
    print(f"  Среднее: {stats['render_time_avg']:.4f} сек")
    print(f"  Максимум: {stats['render_time_max']:.4f} сек")
    print("=" * 50 + "\n")

    # Один график
    fig, axes = plt.subplots(3, 1, figsize=(10, 12))
    axes[0].plot(frames, fps, 'b-', linewidth=1)
    axes[0].set_title('FPS по кадрам')
    axes[0].set_xlabel('Кадр')
    axes[0].set_ylabel('FPS')
    axes[0].grid(True, alpha=0.3)

    axes[1].plot(frames, polygons, 'g-', linewidth=1)
    axes[1].set_title('Количество полигонов по кадрам')
    axes[1].set_xlabel('Кадр')
    axes[1].set_ylabel('Полигоны')
    axes[1].grid(True, alpha=0.3)

    axes[2].plot(frames, render_time, 'r-', linewidth=1)
    axes[2].set_title('Время рендеринга по кадрам')
    axes[2].set_xlabel('Кадр')
    axes[2].set_ylabel('Время (сек)')
    axes[2].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(graph_path, dpi=150)
    plt.close()
    print(f"График сохранен: {graph_path}")


class BenchmarkScript(AppScript):
    def __init__(self, count_per_frame: int = 5):
        self.cube: obj.Cube = None
        self.count_per_frame = count_per_frame
        self._i = 0

    @override
    def init(self, scene: Scene, root_bind_func: Callable[[str, Callable], None] = None):
        # Фонарик на позиции камеры
        scene.lights.append(
            core.SpotLight(
                position=scene.camera.position,
                direction=scene.camera.direction,
                fov=10,
                power=2
            )
        )

        # Куб прямо перед камерой
        self.cube = obj.Cube(
            position=(0.1, 5, 0),
            side=1,
            details=1,
            color=(255, 255, 255)
        )
        scene.objects.append(self.cube)

    def run(self, scene: Scene):
        # Поворот куба каждый кадр
        self.cube.direction = [self._i + 1, self._i + 1, self._i + 1]

        # Увеличение детализации каждые 5 кадров
        if self._i % self.count_per_frame == 0 and self._i > 0:
            self.cube.details = self.cube.details + 1

        self._i += 1


def get_benchmark_app(count_per_frame: int = 5):
    return App(
        app_scripts=[BenchmarkScript(count_per_frame=count_per_frame)],
        settings=Settings(show_fps=True, show_axes=False)
    )


def performance_test():
    """Запуск бенчмарка."""

    app = get_benchmark_app()

    stats_history = []

    try:
        while True:
            stats = app.tick()
            stats_history.append(stats)

            # Остановка при FPS < 10
            if stats.fps < 15:
                break
    finally:
        app.root.destroy()

    # Генерация отчета
    generate_report(stats_history[5:])


if __name__ == '__main__':
    performance_test()
