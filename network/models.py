from typing import Optional
from pydantic import BaseModel


class ChunkNetModel(BaseModel):
    blocks: list[list[int]]
    position: tuple[int, int]
    structures: list[list[int]]


class EntityNetModel(BaseModel):
    position: tuple[int, int]
    entity_id: int


class InventoryNetModel(BaseModel):
    data: list[tuple[int, Optional[int]]]
    selected_slot_id: Optional[int]


class PlayerNetModel(EntityNetModel):
    player_id: int
    inventory: InventoryNetModel
