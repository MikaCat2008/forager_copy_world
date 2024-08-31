from __future__ import annotations

import os
from typing import Optional, TYPE_CHECKING
from importlib.util import module_from_spec, spec_from_file_location

if TYPE_CHECKING:
    from kit.game import Game
    from kit.graphics import Camera


class Scene:
    camera: Optional[Camera]
    scene_manager: SceneManager

    def __init__(self, scene_manager: SceneManager) -> None:
        self.camera = None
        self.scene_manager = scene_manager

    def initialize(self) -> None:
        ...

    def update(self) -> None:
        ...

    def draw(self) -> None:
        self.game.screen.fill(self.camera.background_color)

    @property
    def game(self) -> Game:
        return self.scene_manager.game


class SceneManager:
    game: Game
    scenes: dict[str, Scene]
    current_scene: Optional[Scene]

    def __init__(self, game: Game) -> None:
        self.game = game
        self.scenes = {}

    def add(self, name: str, scene: Scene) -> Scene:
        self.scenes[name] = scene

        return scene

    def get(self, name: str) -> Optional[Scene]:
        return self.scenes.get(name)

    def load_scenes(self) -> None:
        for file in os.listdir("scenes/"):
            parts = file.split(".")

            if len(parts) != 2:
                continue

            file_name = parts[0]
            file_format = parts[1]
            
            if file_format != "py":
                continue

            spec = spec_from_file_location(file_name, f"scenes/{file}")

            if spec is None or spec.loader is None:
                continue

            module = module_from_spec(spec)

            spec.loader.exec_module(module)

            scene = getattr(module, "__scene__", None)
            
            if scene is None:
                continue

            self.add(file_name, scene(self))

    def init_scenes(self) -> None:
        for scene in self.scenes.values():
            scene.initialize()

    def set_current_scene(self, name: str) -> None:
        self.current_scene = self.get(name)

    def update(self) -> None:
        if self.current_scene is None:
            return

        self.current_scene.update()

    def draw(self) -> None:
        if self.current_scene is None:
            return None
        
        self.current_scene.draw()
