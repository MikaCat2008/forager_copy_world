from typing import ClassVar, Optional

import pygame as pg
from pygame.rect import Rect
from pygame.math import Vector2
from pygame.surface import Surface
from pygame.transform import scale_by

from kit.math import clip, min_vector, max_vector, round_vector
from kit.input import Mouse, Keyboard
from kit.scene import Scene

from .color import (
    Color as Color, 
    random_color as random_color
)


class Camera:
    zoom: float
    scene: Scene
    position: Vector2

    min_zoom: ClassVar[float] = 0.25
    max_zoom: ClassVar[float] = 2.5
    zooming_speed: ClassVar[float] = 1.05

    def __init__(
        self, 
        scene: Scene, 
        zoom: float, 
        position: Vector2,
        background_color: Color = Color()
    ) -> None:
        self.zoom = zoom
        self.scene = scene
        self.position = position
        self.background_color = background_color

    def zoom_in(self) -> None:
        self.zoom = clip(self.zoom * self.zooming_speed, self.min_zoom, self.max_zoom)

    def zoom_out(self) -> None:
        self.zoom = clip(self.zoom / self.zooming_speed, self.min_zoom, self.max_zoom)

    def update(self, movement: bool = True) -> None:
        if movement:
            velocity = 0.40 / self.zoom * self.scene.game.delta

            if Keyboard.get_pressed(pg.K_LEFT):
                self.position.x -= velocity
            if Keyboard.get_pressed(pg.K_RIGHT):
                self.position.x += velocity
            if Keyboard.get_pressed(pg.K_UP):
                self.position.y -= velocity
            if Keyboard.get_pressed(pg.K_DOWN):
                self.position.y += velocity

        wheel = Mouse.get_wheel()

        if wheel > 0:
            self.zoom_in()
        if wheel < 0:
            self.zoom_out()

    def get_mouse_position(self) -> Vector2:
        mouse_pos = Vector2(Mouse.get_pos())
        mouse_pos -= Vector2(self.scene.game.screen.get_size()) / 2
        mouse_pos /= self.zoom
        mouse_pos += self.position

        return mouse_pos

    def blit(
        self, 
        surface: Surface, 
        pos: Optional[Vector2] = None, 
        zoom: bool = True,
        static: bool = False
    ) -> None:
        screen = self.scene.game.screen

        screen_size = Vector2(screen.get_size())
        offset = -screen_size / 2

        if zoom:
            offset /= self.zoom

        if not static:
            offset += self.position.copy()

        rect = Rect(pos, surface.get_size())

        min_pos = max_vector(Vector2(rect.topleft), round_vector(offset)) - Vector2(1)

        if zoom:
            max_pos = min_vector(Vector2(rect.bottomright), round_vector(screen_size / self.zoom + offset))
        else:
            max_pos = min_vector(Vector2(rect.bottomright), round_vector(screen_size + offset))

        size = Vector2(max_pos.x - min_pos.x, max_pos.y - min_pos.y) + Vector2(1)

        if size.x < 1 or size.y < 1:
            return

        if size.x > rect.w and size.y > rect.h:
            _surface = surface
        else:
            subrect = Rect(min_pos - Vector2(rect.topleft), size)
            subrect = subrect.clip(Vector2(), Vector2(rect.size))

            if subrect.x < 0 or subrect.y < 0 or subrect.w <= 1 or subrect.h <= 1:
                return
            
            _surface = surface.subsurface(subrect)

        if zoom:
            screen.blit(
                scale_by(_surface, (self.zoom, self.zoom)), (min_pos - offset) * self.zoom
            )
        else:
            screen.blit(_surface, min_pos - offset)
