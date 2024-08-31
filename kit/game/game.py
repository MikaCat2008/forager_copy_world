from typing import ClassVar, Optional

import pygame as pg
from pygame.time import Clock
from pygame.event import get as get_events
from pygame.display import flip
from pygame.surface import Surface

from kit.scene import SceneManager
from kit.input import Mouse, Keyboard


class Game:
    ticks: int
    delta: float
    clock: Clock

    screen: Optional[Surface]
    scene_manager: Optional[SceneManager] = None

    max_fps: ClassVar[int] = 60

    def __init__(self) -> None:
        self.ticks = 0
        self.delta = 0.001
        self.clock = Clock()
        
        self.screen = None
        self.scene_manager = None

    def initilize(self) -> None:
        ...

    def update(self) -> None:        
        Mouse.update()
        Keyboard.update()

        if self.scene_manager is not None:
            self.scene_manager.update()

        self.ticks += 1

    def draw(self) -> None:
        if self.screen is None or self.scene_manager is None:
            return

        self.scene_manager.draw()
        
        flip()

    def run(self) -> None:
        self.initilize()

        while 1:
            for event in get_events():
                if event.type == pg.QUIT:
                    exit()

                if event.type == pg.MOUSEWHEEL:
                    Mouse.set_wheel(event.y)

            self.delta = self.clock.tick(self.max_fps)

            self.update()
            self.draw()
