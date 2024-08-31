from typing import Any, ClassVar
from pydantic import BaseModel

from .models import (
    ChunkNetModel,
    EntityNetModel,
    PlayerNetModel,
    InventoryNetModel
)


class Update(BaseModel):
    update_type: ClassVar[int]


class Callback(Update):
    update_type = 0

    result: Any
    callback_id: int


class PlayerJoin(Update):
    update_type = 1

    player: PlayerNetModel


class ChunkLoad(Update):
    update_type = 2
    
    chunk: ChunkNetModel


class EntitySpawn(Update):
    update_type = 3

    entity: EntityNetModel


class PlayerMove(Update):
    update_type = 4

    position: tuple[int, int]
    player_id: int


class InventoryUpdate(Update):
    update_type = 5

    player_id: int
    inventory: InventoryNetModel


class StructureDamage(Update):
    update_type = 6

    power: int
    position: tuple[int, int]
    player_id: int
 
 
class StructureDestroy(Update):
    update_type = 7

    position: tuple[int, int]


class UpdatesFactory:
    data: dict[int, type[Update]]

    def __init__(self) -> None:
        self.data = {
            0: Callback,
            1: PlayerJoin,
            2: ChunkLoad,
            3: EntitySpawn,
            4: PlayerMove,
            5: InventoryUpdate,
            6: StructureDamage,
            7: StructureDestroy,
        }

    def from_dict(self, update_dict: dict) -> Update:        
        factory = self.data[update_dict["type"]]
        
        return factory.model_validate(update_dict["data"])
