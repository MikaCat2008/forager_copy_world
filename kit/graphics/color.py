from random import randint

from pygame.math import Vector3


class Color(Vector3):
    BLACK = Vector3(0, 0, 0)
    WHITE = Vector3(255, 255, 255)

    
def random_color(min_color: int = 0, max_color = 255) -> Color:
    r = randint(min_color, max_color)
    g = randint(min_color, max_color)
    b = randint(min_color, max_color)
    
    return Color(r, g, b)
