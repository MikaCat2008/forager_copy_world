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


class PlayerMove(Update):
    update_type = 2

    position: tuple[int, int]
    player_id: int


class InventoryUpdate(Update):
    update_type = 3

    player_id: int
    inventory: InventoryNetModel


class StructureDamage(Update):
    update_type = 4

    power: int
    position: tuple[int, int]
    player_id: int
 
 
class StructureDestroy(Update):
    update_type = 5

    position: tuple[int, int]


class StructurePlace(Update):
    update_type = 6

    position: tuple[int, int]
    structure_type: int


class UpdatesFactory:
    data: dict[int, type[Update]]

    def __init__(self) -> None:
        self.data = {
            0: Callback,
            1: PlayerJoin,
            2: PlayerMove,
            3: InventoryUpdate,
            4: StructureDamage,
            5: StructureDestroy,
            6: StructurePlace
        }

    def from_dict(self, update_dict: dict) -> Update:        
        factory = self.data[update_dict["type"]]
        
        return factory.model_validate(update_dict["data"])
