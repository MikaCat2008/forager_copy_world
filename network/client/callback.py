from typing import Any
from threading import Event


class Callback(Event):
    result: Any
    callback_id: int
    
    def __init__(self, callback_id: int) -> None:
        super().__init__()
        
        self.result = None
        self.callback_id = callback_id
    
    def set_result(self, result: Any) -> None:
        self.result = result
        self.set()
    
    def wait_result(self) -> None:
        self.wait()
        
        return self.result
