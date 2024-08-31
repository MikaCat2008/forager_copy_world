from typing import Callable, Optional

from pygame.math import Vector2
from pygame.surface import Surface

from kit.input import Mouse
from kit.graphics import Color

from .label import Label
from .image import Image


class TextButton(Label):
    def __init__(
        self, 
        text: str, 
        position: Vector2, 
        color: Optional[Color] = None, 
        on_hover: Optional[Callable] = None,
        on_click: Optional[Callable] = None,
        font_size: int = 42
    ) -> None:
        super().__init__(text, position, color, font_size)

        if on_hover:
            self.on_hover = on_hover

        if on_click:
            self.on_click = on_click

    def update(self) -> None:
        if self.rect is None:
            return
        
        if self.rect.collidepoint(Mouse.get_pos() - self.window.get_screen_position()):
            self.on_hover()

            if Mouse.get_clicked(0):
                self.on_click()

    def on_hover(self) -> None:
        ...

    def on_click(self) -> None:
        ...


class ImageButton(Image):
    def __init__(
        self, 
        image: Surface, 
        position: Vector2, 
        on_hover: Optional[Callable] = None,
        on_click: Optional[Callable] = None,
    ) -> None:
        super().__init__(image, position)

        if on_hover:
            self.on_hover = on_hover

        if on_click:
            self.on_click = on_click

    def update(self) -> None:
        if self.rect is None:
            return
        
        if self.rect.collidepoint(Mouse.get_pos() - self.window.get_screen_position()):
            self.on_hover()

            if Mouse.get_clicked(0):
                self.on_click()

    def on_hover(self) -> None:
        ...

    def on_click(self) -> None:
        ...
