from pygame.rect import Rect
from pygame.math import Vector2
from pygame.surface import Surface

from .component import Component


class Image(Component):
    rect: Rect
    image: Surface
    position: Vector2

    def __init__(
        self, 
        image: Surface, 
        position: Vector2, 
    ) -> None:
        super().__init__()

        image_size = Vector2(image.get_size())

        self.rect = Rect(position, image_size)
        self.image = image
        self.position = position - image_size / 2

    def render(self, image: Surface) -> None:
        image.blit(self.image, self.rect)
