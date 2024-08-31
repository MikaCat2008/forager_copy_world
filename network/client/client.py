import time, json, socket
from typing import Any
from threading import Lock

from pydantic import TypeAdapter

from network.methods import Method

from .callback import Callback


class BaseClient:
    lock: Lock
    sock: socket.socket
    callbacks: dict[int, Callback]
    callbacks_next_id: int
 
    def __init__(self) -> None:
        self.lock = Lock()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(("25.51.236.41", 8080))

        self.callbacks = {}
        self.callbacks_next_id = 0
 
    def resolve(self, callback: Callback) -> None:
        result = callback.result
        callback_id = callback.callback_id

        with self.lock:
            self.callbacks[callback_id].set_result(result)
            del self.callbacks[callback_id]
    
    def __call__(self, method: Method) -> Any:
        with self.lock:
            callback_id = self.callbacks_next_id
            self.callbacks_next_id += 1
            
            callback = Callback(callback_id)
            self.callbacks[callback_id] = callback

            self.sock.sendall(
                json.dumps({
                    "id": callback_id,
                    "type": method.method_type,
                    "data": method.model_dump()
                }).encode() + b"\n"
            )

            time.sleep(0.01)

        if method.return_type is None:
            return
        
        result = callback.wait_result()

        return TypeAdapter(method.return_type).validate_python(result)
