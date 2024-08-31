from typing import ClassVar, Optional

from pygame import mouse


class MouseState:
    wheel: int
    pressed: tuple[bool, bool, bool]
    
    def __init__(self, wheel: int, pressed: tuple[bool, bool, bool]) -> None:
        self.wheel = wheel
        self.pressed = pressed


class Mouse:
    current_state: ClassVar[Optional[MouseState]] = None
    previous_state: ClassVar[Optional[MouseState]] = None

    _wheel: ClassVar[int] = 0

    @classmethod
    def update(cls) -> None:
        previous_state = cls.current_state
        
        cls.current_state = MouseState(cls._wheel, mouse.get_pressed())
        cls._wheel = 0

        if previous_state is None:
            cls.previous_state = cls.current_state
        else:
            cls.previous_state = previous_state        

    @classmethod
    def get_pressed(cls, key: int) -> bool:
        if cls.current_state is None:
            return False
        
        return cls.current_state.pressed[key]

    @classmethod
    def get_clicked(cls, key: int) -> Optional[bool]:
        if cls.current_state is None or cls.previous_state is None:
            return False
        
        return cls.current_state.pressed[key] and not cls.previous_state.pressed[key]

    @classmethod
    def get_wheel(cls) -> int:
        if cls.current_state is None:
            return 0
        
        return cls.current_state.wheel

    @classmethod
    def set_wheel(cls, value: int) -> None:
        cls._wheel = value

    @classmethod
    def get_pos(cls) -> tuple[int, int]:
        return mouse.get_pos()
