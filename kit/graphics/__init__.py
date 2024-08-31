import numpy as np

from pygame.surface import Surface
from pygame.surfarray import pixels3d

from .color import (
    Color as Color, 
    random_color as random_color
)
from .camera import Camera as Camera


def blit_points(surface: Surface, color: Color, points: np.ndarray) -> None:
    pixel_array = pixels3d(surface)
    pixel_array[points[:, 0], points[:, 1]] = color

    del pixel_array
