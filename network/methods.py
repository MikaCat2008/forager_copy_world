from typing import Any, ClassVar, Optional
from pydantic import BaseModel

from network.models import (
    ChunkNetModel, 
    PlayerNetModel, 
    InventoryNetModel
)


class Method(BaseModel):
    method_type: ClassVar[int]
    return_type: ClassVar[Any] = None


class JoinServer(Method):
    method_type = 0
    return_type = Optional[PlayerNetModel]


class LoadChunk(Method):
    method_type = 1
    return_type = ChunkNetModel
    
    position: tuple[int, int]


class MovePlayer(Method):
    method_type = 2
    
    position: tuple[int, int]
    player_id: int


class UpdateInventory(Method):
    method_type = 3
    
    player_id: int
    inventory_data: list[tuple[int, Optional[int]]]
    selected_slot_id: Optional[int]


class DamageStructure(Method):
    method_type = 4
    
    power: int
    position: tuple[int, int]
    player_id: int
 
 
class DestroyStructure(Method):
    method_type = 5
    
    position: tuple[int, int]


class GetPlayers(Method):
    method_type = 6
    return_type = list[PlayerNetModel]


class MethodsFactory:
    data: dict[int, type[Method]]

    def __init__(self) -> None:
        self.data = {
            0: JoinServer,
            1: LoadChunk,
            2: MovePlayer,
            3: UpdateInventory,
            4: DamageStructure,
            5: DestroyStructure,
            6: GetPlayers
        }

    def from_dict(self, method_dict: dict) -> Method:
        factory = self.data[method_dict["type"]]
        
        return factory.model_validate(method_dict["data"])

