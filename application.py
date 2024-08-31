import pygame as pg
from pygame.display import set_mode

pg.init()
pg.font.init()

from kit.game import Game
from kit.scene import SceneManager


class Application(Game):
    max_fps = 120

    def __init__(self) -> None:
        super().__init__()

        self.screen = set_mode((1504, 768))
        # self.screen = set_mode((1504 / 2, 768 / 2))
        self.scene_manager = SceneManager(self)
        
        self.scene_manager.load_scenes()
        self.scene_manager.init_scenes()
        self.scene_manager.set_current_scene("scene1")
