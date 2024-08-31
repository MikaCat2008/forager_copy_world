from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from kit.graphics import Camera

if TYPE_CHECKING:
    from .window import Window


class Component:
    window: Optional[Window]

    def __init__(self) -> None:
        self.window = None

    def update(self) -> None:
        ...
    
    def render(self, camera: Camera) -> None:
        ...
