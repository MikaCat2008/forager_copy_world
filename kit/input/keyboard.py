from typing import ClassVar, Optional

from pygame import key


class Keyboard:
    current_state: ClassVar[Optional[key.ScancodeWrapper]] = None
    previous_state: ClassVar[Optional[key.ScancodeWrapper]] = None

    @classmethod
    def update(cls) -> None:
        cls.previous_state = cls.current_state
        cls.current_state = key.get_pressed()

    @classmethod
    def get_pressed(cls, key: int) -> bool:
        if cls.current_state is None:
            return False

        return cls.current_state[key]

    @classmethod
    def get_clicked(cls, key: int) -> bool:
        if cls.current_state is None or cls.previous_state is None:
            return False

        return cls.current_state[key] and not cls.previous_state[key]
