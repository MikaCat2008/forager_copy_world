from __future__ import annotations

from typing import Any, TYPE_CHECKING

from .future import PoolFuture
from ._manager import PoolManager as _PoolManager

if TYPE_CHECKING:
    from .manager import PoolManager


class PoolLink:
    link_id: int
    manager: PoolManager

    def __init__(self, link_id: int, manager: PoolManager) -> None:
        self.link_id = link_id
        self.manager = manager

    def call_method(self, method_name: str, *args: Any, _async=True) -> PoolFuture:
        return self.manager.apply(
            _PoolManager.call_entity_method, self.link_id, 
            method_name, *self.encode_args(args), _async=_async
        )
    
    def is_alive(self, _async=True) -> PoolFuture:
        return self.manager.apply(_PoolManager.is_alive, self.link_id, _async=_async)

    def delete(self, _async=True) -> PoolFuture:
        return self.manager.apply(_PoolManager.delete_entity, self.link_id, _async=_async)
    
    @classmethod
    def encode_args(cls, args: tuple) -> list:
        encoded_args = [None] * len(args)
        
        for i, arg in enumerate(args):
            encoded_arg = arg

            if isinstance(arg, PoolLink):
                encoded_arg = "link", arg.link_id
            
            encoded_args[i] = encoded_arg

        return encoded_args
