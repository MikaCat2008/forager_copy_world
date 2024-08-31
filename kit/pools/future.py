from typing import Any, Callable, Optional


class PoolFuture:
    done: bool
    result: Optional[Any]
    callbacks: list[Callable]

    def __init__(self) -> None:
        self.done = False
        self.result = None
        self.callbacks = []

    def add_callback(self, callback: Callable) -> None:
        self.callbacks.append(callback)

    def apply_callbacks(self) -> None:
        for callback in self.callbacks:
            callback(self)
