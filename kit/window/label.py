from typing import Optional

from pygame.rect import Rect
from pygame.math import Vector2
from pygame.surface import Surface

from kit.graphics import Color

from .font import get_font
from .component import Component


class Label(Component):
    rect: Optional[Rect]
    image: Optional[Surface]
    position: Vector2

    def __init__(
        self, 
        text: str, 
        position: Vector2, 
        color: Optional[Color] = None, 
        font_size: int = 32
    ) -> None:
        super().__init__()

        font = get_font(font_size)
        self.image = font.render(text, None, color or Color())
        image_size = Vector2(self.image.get_size())

        self.position = position - image_size / 2
        self.rect = Rect(self.position, self.image.get_size())

    def render(self, image: Surface) -> None:
        image.blit(self.image, self.rect)
