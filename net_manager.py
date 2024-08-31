from __future__ import annotations

from typing import Optional

from network.client import ClientDispatcher
from network.models import (
    ChunkNetModel,
    EntityNetModel,
    PlayerNetModel,
    InventoryNetModel
)

from client import Client
from resources import ResourcesManager

from world import Chunk, Layer
from player import PlayerController
from inventory import Inventory, InventoryController


class NetModelAdapter:
    net_manager: ClientNetManager
    resources_manager: ResourcesManager

    def __init__(
        self, 
        net_manager: ClientNetManager, 
        resources_manager: ResourcesManager
    ) -> None:
        self.net_manager = net_manager
        self.resources_manager = resources_manager

    def adapt_chunk(self, chunk_net_model: ChunkNetModel) -> Chunk:
        chunk = Chunk(
            Layer(chunk_net_model.blocks), 
            chunk_net_model.position, 
            Layer(chunk_net_model.structures)
        )
        
        return chunk

    def adapt_player(self, player_net_model: PlayerNetModel) -> PlayerController:
        player = PlayerController(self.net_manager, self.resources_manager)

        inventory = self.adapt_inventory(player_net_model.inventory)

        player.set_position(player_net_model.position)
        player.set_entity_id(player_net_model.entity_id)
        player.set_player_id(player_net_model.player_id)
        player.set_inventory(inventory)

        return player
    
    def adapt_inventory(self, inventory_net_mode: InventoryNetModel) -> InventoryController:
        inventory = InventoryController(self.net_manager, self.resources_manager)
        inventory.set_inventory(
            Inventory.from_data(inventory_net_mode.data)
        )
        inventory.set_selected_slot_id(inventory_net_mode.selected_slot_id)

        return inventory


class ClientNetManager:
    client: Client
    dispatcher: ClientDispatcher
    net_model_adapter: NetModelAdapter
    
    def __init__(
        self, 
        client: Client, 
        dispatcher: ClientDispatcher, 
        resources_manager: ResourcesManager
    ) -> None:
        self.client = client
        self.dispatcher = dispatcher
        self.net_model_adapter = NetModelAdapter(self, resources_manager)

    def join_server(self) -> PlayerController:
        player_net_model = self.client.join_server()
        
        return self.net_model_adapter.adapt_player(player_net_model)

    def load_chunk(self, position: tuple[int, int]) -> Optional[Chunk]:
        chunk_net_model = self.client.load_chunk(position)

        if chunk_net_model is None:
            return None

        return self.net_model_adapter.adapt_chunk(chunk_net_model)

    def move_player(self, position: tuple[int, int], player_id: int) -> None:
        self.client.move_player(position, player_id)

    def update_inventory(
        self, 
        player_id: int,
        inventory_data: list[tuple[int, Optional[int]]], 
        selected_slot_id: Optional[int]
    ) -> None:
        self.client.update_inventory(player_id, inventory_data, selected_slot_id)

    def get_players(self) -> list[PlayerController]:
        player_net_models = self.client.get_players()
        
        return [
            self.net_model_adapter.adapt_player(player_net_model) 
            for player_net_model in player_net_models
        ]
