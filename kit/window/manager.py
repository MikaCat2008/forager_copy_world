from kit.graphics import Camera

from .window import Window


class WindowManager:
    windows: list[Window]

    def __init__(self) -> None:
        self.windows = []

    def add_windows(self, *windows: Window) -> None:
        self.windows.extend(windows)

    def update(self) -> None:
        for window in self.windows:
            window.update()

    def draw(self, camera: Camera) -> None:
        for window in self.windows:
            window.draw(camera)
