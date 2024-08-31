import threading as thr, multiprocessing as mp
from queue import Queue
from typing import Any, Type, Callable
from multiprocessing.pool import Pool

from .link import PoolLink
from .future import PoolFuture
from ._manager import PoolManager as _PoolManager


class PoolManager:
    pool: Pool
    input_queue: Queue
    output_queue: Queue
    output_event: thr.Event
    fast_input_queue: Queue
    fast_output_queue: Queue

    next_link_id: int
    next_future_id: int

    futures: dict[int, PoolFuture]
    input_list: list[tuple[int, Callable, tuple]]

    def __init__(self) -> None:        
        manager = mp.Manager()

        self.pool = mp.Pool(1)
        self.input_queue = manager.Queue()
        self.output_queue = manager.Queue()
        self.output_event = manager.Event()
        self.fast_input_queue = manager.Queue()
        self.fast_output_queue = manager.Queue()

        self.next_link_id = 0
        self.next_future_id = 0

        self.futures = {}
        self.input_list = []

    def link(self, cls: Type, *args: Any, _async=True) -> PoolLink:
        link_id = self.next_link_id
        
        self.next_link_id += 1
        self.apply(
            _PoolManager.create_entity, cls, link_id, 
            *PoolLink.encode_args(args), _async=_async
        )
        
        return PoolLink(link_id, self)

    def apply(self, function: Callable, *args: Any, _async=True) -> Any | PoolFuture:
        if _async:
            future_id = self.next_future_id
            future = PoolFuture()
    
            self.futures[future_id] = future
            self.input_list.append((future_id, function, args))
            self.next_future_id += 1

            return future
        else:
            self.fast_input_queue.put((function, args))

            return self.fast_output_queue.get()

    def send_input(self) -> None:
        if len(self.input_list) == 0:
            return

        self.input_queue.put(self.input_list)
        self.input_list.clear()

    def update_futures(self) -> None:
        self.output_event.set()

        for future_id, result in self.output_queue.get():
            future = self.futures[future_id]
 
            future.done = True
            future.result = result
            future.apply_callbacks()

            del self.futures[future_id]

    def start(self) -> None:
        self.pool.apply_async(_PoolManager, (
            self.input_queue, self.output_queue, self.output_event, 
            self.fast_input_queue, self.fast_output_queue
        ))

    def update(self) -> None:
        self.update_futures()
        self.send_input()

    def close(self) -> None:
        self.pool.close()
