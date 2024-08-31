import json
from typing import Callable

from network import Update, UpdatesFactory

from .client import BaseClient


class ClientDispatcher:
    client: BaseClient
    updates_factory: UpdatesFactory
    
    def __init__(self, client: BaseClient) -> None:
        self.client = client
        self.updates_factory = UpdatesFactory()
        self.updates_handlers = {
            0: client.resolve
        }

    def on(self, update_type: type[Update]) -> Callable:
        def _(function: Callable) -> None:
            self.updates_handlers[update_type.update_type] = function
        
        return _

    def process_update(self, update: Update) -> None:
        function = self.updates_handlers.get(update.update_type)

        if function is not None:
            function(update)

    def process_data(self, data: dict) -> None:
        update = self.updates_factory.from_dict(data)

        self.process_update(update)

    def run(self) -> None:
        all_data = b""

        while True:
            all_data += self.client.sock.recv(1024)
            
            while True:
                if all_data.count(b"\n") == 0:
                    break

                data, _, all_data = all_data.partition(b"\n")

                self.process_data(json.loads(data))
