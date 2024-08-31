from typing import ClassVar

import pygame as pg
from pygame.image import load as pg_load
from pygame.surface import Surface


class Content:
    images: ClassVar[dict[str, Surface]] = {}

    @classmethod
    def load_image(cls, path: str, save: bool = True) -> Surface:
        image = cls.images.get(path)

        if image is None:
            image = pg_load(path).convert_alpha()

            if save:
                cls.images[path] = image

        return image

    @classmethod
    def load_tileset(cls, path: str, tile_size: int, orders: list[tuple[int, int]]) -> list[Surface]:
        image = cls.load_image(path, save=False)
        empty = Surface((32, 32), pg.SRCALPHA)

        return [
            empty if (x, y) == (-1, -1) else
            image.subsurface(x * tile_size, y * tile_size, tile_size, tile_size) 
            for x, y in orders
        ]

    @classmethod
    def compile_texture(cls, orders: list[list[int]], textures: list[Surface], tile_size: int) -> Surface:
        size = len(orders[0]) * tile_size, len(orders) * tile_size
        surface = Surface(size, pg.SRCALPHA)

        for y, row in enumerate(orders):
            for x, texture_id in enumerate(row):
                surface.blit(textures[texture_id], (x * tile_size, y * tile_size))

        return surface
