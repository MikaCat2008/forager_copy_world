from typing import Any, Type, ClassVar
from threading import Lock, Event, Thread
from multiprocessing.queues import Queue

from .entity import PoolEntity


class PoolManager:
    lock: Lock
    results: list[tuple[int, Any]]

    input_queue: Queue
    output_queue: Queue
    output_event: Event
    fast_input_queue: Queue
    fast_output_queue: Queue

    entities: ClassVar[dict[int, PoolEntity]] = {}

    def __init__(
        self, input_queue: Queue, 
        output_queue: Queue, output_event: Event,
        fast_input_queue: Queue, fast_output_queue: Queue
    ) -> None:
        self.lock = Lock()
        self.results = []

        self.input_queue = input_queue
        self.output_queue = output_queue
        self.output_event = output_event
        self.fast_input_queue = fast_input_queue
        self.fast_output_queue = fast_output_queue

        threads = [
            Thread(target=self.process_input),
            Thread(target=self.process_output),
            Thread(target=self.process_fast_input)
        ]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

    def process_input(self) -> None:
        while True:
            input_list = self.input_queue.get()

            for future_id, function, args in input_list:
                result = function(*self.decode_args(args))

                with self.lock:
                    self.results.append((future_id, result))

    def process_output(self) -> None:
        while True:
            self.output_event.wait()
            self.output_event.clear()

            self.lock.acquire()

            self.output_queue.put(self.results)
            self.results.clear()

            self.lock.release()

    def process_fast_input(self) -> None:
        while True:
            function, args = self.fast_input_queue.get()

            result = function(*self.decode_args(args))

            self.fast_output_queue.put(result)

    @classmethod
    def is_alive(cls, link_id: int) -> bool:
        return link_id in cls.entities

    @classmethod
    def get_entity(cls, link_id: int) -> object:
        return cls.entities.get(link_id)

    @classmethod
    def create_entity(cls, _cls: Type, link_id: int, *args: Any) -> None:
        cls.entities[link_id] = _cls(*args)

    @classmethod
    def call_entity_method(cls, link_id: int, method_name: str, *args: Any) -> Any:
        entity = cls.entities.get(link_id)

        if entity is None:
            return

        method = getattr(entity, method_name)

        return method(*args)
    
    @classmethod
    def delete_entity(cls, link_id: int) -> None:
        entity = cls.entities.get(link_id)
        
        if entity is None:
            return

        entity.delete()
        del cls.entities[link_id]

    @classmethod
    def decode_args(cls, args: tuple) -> list:
        decoded_args = [None] * len(args)

        for i, arg in enumerate(args):
            decoded_arg = arg

            if (
                isinstance(arg, tuple) and len(arg) == 2 and \
                arg[0] == "link" and isinstance(arg[1], int)
            ):
                decoded_arg = cls.get_entity(arg[1])

            decoded_args[i] = decoded_arg

        return decoded_args
