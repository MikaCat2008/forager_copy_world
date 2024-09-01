from typing import Optional

from network.client import BaseClient
from network.models import (
    ChunkNetModel, 
    EntityNetModel, 
    PlayerNetModel, 
    InventoryNetModel 
)
from network.methods import (
    JoinServer, 
    LoadChunk,
    MovePlayer,
    UpdateInventory,
    DamageStructure,
    DestroyStructure,
    GetPlayers,
    PlaceStructure
)


class Client(BaseClient):
    def join_server(self) -> PlayerNetModel:
        return self(
            JoinServer()
        )
  
    def load_chunk(self, position: tuple[int, int]) -> Optional[ChunkNetModel]:
        return self(
            LoadChunk(
                position=position
            )
        )
    
    def move_player(self, position: tuple[int, int], player_id: int) -> None:
        return self(
            MovePlayer(
                position=position,
                player_id=player_id
            )
        )
    
    def update_inventory(
        self, 
        player_id: int, 
        inventory_data: list[tuple[int, Optional[int]]],
        selected_slot_id: Optional[int]
    ) -> None:
        return self(
            UpdateInventory(
                player_id=player_id,
                inventory_data=inventory_data,
                selected_slot_id=selected_slot_id
            )
        )
    
    def damage_structure(self, power: int, position: tuple[int, int], player_id: int) -> None:
        return self(
            DamageStructure(
                power=power,
                position=position,
                player_id=player_id
            )
        )
    
    def destroy_structure(self, position: tuple[int, int]) -> None:
        return self(
            DestroyStructure(
                position=position
            )
        )
    
    def get_players(self) -> list[PlayerNetModel]:
        return self(
            GetPlayers()
        )

    def place_structure(self, position: tuple[int, int], structure_type: int) -> None:
        return self(
            PlaceStructure(
                position=position,
                structure_type=structure_type
            )
        )
