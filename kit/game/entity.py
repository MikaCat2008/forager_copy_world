from typing import Optional

from pygame.math import Vector2
from pygame.surface import Surface

from kit.scene import Scene
from kit.graphics import Camera


class Entity:
    scene: Optional[Scene] = None
    image: Optional[Surface] = None
    position: Vector2

    def __init__(self, scene: Optional[Scene] = None, position: Optional[Vector2] = None) -> None:
        self.scene = scene
        self.position = position or Vector2()
    
    def update(self) -> None:
        ...
    
    def draw(self, camera: Camera) -> None:
        if self.image is None:
            return
        
        camera.blit(self.image, self.position)
