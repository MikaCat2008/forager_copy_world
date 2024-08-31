from typing import Optional

import pygame as pg
from pygame.math import Vector2
from pygame.surface import Surface

from kit.game import Entity
from kit.scene import Scene
from kit.graphics import Camera

from .component import Component


class Window(Entity):
    visible: bool
    components: list[Component]

    def __init__(
        self, 
        size: Vector2, 
        components: list[Component], 
        scene: Optional[Scene] = None, 
        position: Optional[Vector2] = None
    ) -> None:
        super().__init__(scene, position)
        
        self.image = Surface(size, pg.SRCALPHA)
        self.visible = True
        self.components = components

        for component in components:
            component.window = self

    def render(self) -> None:
        for component in self.components:
            component.render(self.image)

    def get_screen_position(self) -> Vector2:
        position = self.position.copy()
        position -= Vector2(self.image.get_size()) / 2
        position += Vector2(self.scene.game.screen.get_size()) / 2 
        
        return position

    def update(self) -> None:
        for component in self.components:
            component.update()

    def draw(self, camera: Camera) -> None:
        if not self.visible:
            return
        
        self.render()

        camera.blit(self.image, self.position - Vector2(self.image.get_size()) / 2, static=True)
