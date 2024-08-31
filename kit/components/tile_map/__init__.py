from __future__ import annotations

import time
from typing import Optional
from functools import cache

import pygame as pg
from pygame.draw import rect as draw_rect
from pygame.math import Vector2
from pygame.font import Font, SysFont
from pygame.surface import Surface

from kit.graphics import Color, Camera

Position = tuple[int, int]  


@cache
def get_font(font_size: int) -> Font:
    return SysFont("Arial", font_size)


class TileLayer:
    data: dict[int, object]
    layer_type: int

    def __init__(self) -> None:
        self.data = {}

    def set_value(self, value: object, z_index: int) -> None:
        self.data[z_index] = value

    def remove_value(self, z_index: int) -> None:
        del self.data[z_index]


class TextureTileLayer(TileLayer):
    layer_type = 0


class TextTileLayer(TileLayer):
    layer_type = 1


class Tile:
    layers: list[TileLayer]
    changed: bool

    def __init__(self, layer_types: Optional[list[int]] = None) -> None:
        self.layers = []
        self.changed = False

        for layer_type in [] or layer_types:
            self.add_layer(layer_type)

    def add_layer(self, layer_type: int) -> None:
        if layer_type == 0:
            layer = TextureTileLayer()
        elif layer_type == 1:
            layer = TextTileLayer()
        
        self.layers.append(layer)
        self.changed = True

    def get_value(self, z_index: int, layer_id: int) -> int:
        return self.layers[layer_id].get_value(z_index)

    def set_value(self, value: object, z_index: int, layer_id: int) -> None:     
        self.layers[layer_id].set_value(value, z_index)
        self.changed = True

    def remove_value(self, z_index: int, layer_id: int) -> None:
        layer = self.layers[layer_id]
        
        if z_index not in layer.data:
            return 
        
        layer.remove_value(z_index)
        self.changed = True


class TileMapData:
    size: tuple[int, int]
    tiles: list[list[Tile]]
    layers: list[int]
    component: TileMapComponent

    def __init__(self, size: tuple[int, int], component: TileMapComponent) -> None:
        self.size = size
        self.layers = []

        self.tiles = self.create_tiles()
        self.component = component

    def create_tiles(self) -> list[list[Tile]]:
        return [[ Tile(self.layers) for _ in range(self.size[0]) ] for _ in range(self.size[1]) ]
    
    def add_layer(self, layer_type: int) -> None:
        self.layers.append(layer_type)

        for row in self.tiles:
            for tile in row:
                tile.add_layer(layer_type)

    def fill_layer(self, value: int, layer_id: int) -> None:
        for row in self.tiles:
            for tile in row:
                tile.set_value(value, 0, layer_id)

    def get_tile(self, position: Position) -> Tile:
        return self.tiles[position[1]][position[0]]

    def set_value(self, value: int, z_index: int, layer_id: int, position: Position) -> None:
        tile = self.get_tile(position)
        tile.set_value(value, z_index, layer_id)

    def remove_texture_id(self, z_index: int, layer_id: int, position: Position) -> None:
        tile = self.get_tile(position)
        tile.remove_value(z_index, layer_id)

    def clear(self) -> None:
        self.tiles = self.create_tiles()


class TileMapRenderer:
    surface: Surface
    tile_size: int
    component: TileMapComponent

    def __init__(self, textures: list[Surface], tile_size: int, component: TileMapComponent) -> None:
        self.textures = textures
        self.tile_size = tile_size
        self.component = component

        self.surface = self.create_surface()

    def create_surface(self) -> Surface:
        return Surface(self.by_tile_size(self.component.size), pg.SRCALPHA)

    def render(self) -> None:
        for y, tiles_row in enumerate(self.component.data.tiles):
            for x, tile in enumerate(tiles_row):
                if not tile.changed:
                    continue

                tile.changed = False

                self.render_tile((x, y), tile)

    def render_tile(self, position: Position, tile: Tile) -> None:
        position = self.by_tile_size(position)
        
        draw_rect(
            self.surface, (0, 0, 0, 0), 
            (position, self.by_tile_size((1, 1)))
        )

        for layer in tile.layers:
            data = layer.data

            for z_index in sorted(data.keys()):
                match layer.layer_type:
                    case 0:
                        value: int = data[z_index]

                        surface = self.textures[value]
                    case 1:
                        font = get_font(14)
                        value: str = data[z_index]

                        text = font.render(value, None, Color(255))
                        height = text.get_size()[1]

                        surface = Surface(self.by_tile_size((1, 1)), pg.SRCALPHA)
                        surface.blit(text, Vector2(3, self.tile_size - height - 3))

                self.surface.blit(surface, position)

    def by_tile_size(self, value: tuple[int, int]) -> tuple[int, int]:
        return value[0] * self.tile_size, value[1] * self.tile_size


class TileMapComponent:
    size: tuple[int, int]
    data: TileMapData
    position: Vector2
    renderer: TileMapRenderer

    def __init__(
        self, 
        size: tuple[int, int], 
        textures: list[Surface], 
        position: Optional[Vector2] = None
    ) -> None:
        self.size = size
        self.data = TileMapData(size, self)
        self.position = position or Vector2()
        self.renderer = TileMapRenderer(textures, 32, self)

    def draw(self, camera: Camera, zoom: bool = True, static: bool = False) -> None:
        self.renderer.render()

        # draw_rect(self.renderer.surface, (255, 0, 0), self.renderer.surface.get_rect(), 2)
        camera.blit(self.renderer.surface, self.position, zoom=zoom, static=static)
