from pygame.surface import Surface

from kit.graphics import Color

from .component import Component


class Background(Component):
    color: Color
    
    def __init__(self, color: Color) -> None:
        super().__init__()

        self.color = color

    def render(self, image: Surface) -> None:
        image.fill(self.color)
