from functools import cache

from pygame.font import Font, SysFont


@cache
def get_font(font_size: int) -> Font:
    return SysFont(None, font_size)
