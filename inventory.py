from __future__ import annotations

# import json
from typing import Optional, TYPE_CHECKING
from collections import defaultdict

from pygame.math import Vector2

from kit.graphics import Camera
from kit.components.tile_map import TileMapComponent

from resources import ResourcesManager

if TYPE_CHECKING:
    from net_manager import ClientNetManager


class Slot:
    count: int
    slot_id: int
    item_type: Optional[int]
    
    def __init__(self, slot_id: int) -> None:
        self.count = 0
        self.slot_id = slot_id
        self.item_type = None


class Inventory:
    size: int
    slots: list[Slot]
    selected_slot_id: Optional[int]
 
    def __init__(self, size: int) -> None:
        self.size = size
        self.slots = [Slot(i) for i in range(size)]
        self.selected_slot_id = None

    def to_data(self) -> list[tuple[int, Optional[int]]]:
        return [
            (slot.count, slot.item_type) for slot in self.slots
        ]

    @classmethod
    def from_data(cls, data: list[tuple[int, Optional[int]]], size: Optional[int] = None) -> Inventory:
        if size:
            inventory = cls(size)
        else:
            inventory = cls(len(data))

        for slot, (count, item_type) in zip(inventory.slots, data):
            slot.count = count
            slot.item_type = item_type
        
        return inventory
    

class InventoryModel:
    controller: InventoryController
    
    inventory: Inventory
    
    def __init__(self, controller: InventoryController) -> None:
        self.controller = controller
        
        self.inventory = Inventory(10)
 
    def add_item_type(self, count: int, item_type: int) -> Slot:
        empty_slot = None
        
        for slot in self.inventory.slots:
            if slot.item_type is None:
                if empty_slot is None:
                    empty_slot = slot
                
                continue
            
            if slot.item_type == item_type:
                slot.count += count
                
                return slot
            
        if empty_slot is None:
            raise ValueError
            
        empty_slot.count = count
        empty_slot.item_type = item_type
        
        return empty_slot
  
    def remove_item_type(self, count: int, item_type: int) -> Slot:
        for slot in self.inventory.slots:
            if slot.item_type == item_type:
                slot.count -= count
                
                if slot.count == 0:
                    slot.item_type = None
                
                return slot
            
        raise ValueError


class InventoryView:
    controller: InventoryController
    resource_manager: ResourcesManager

    tile_map: TileMapComponent
    
    def __init__(
        self, 
        controller: InventoryController,
        resources_manager: ResourcesManager
    ) -> None:
        self.controller = controller
        self.resource_manager = resources_manager

        self.tile_map = TileMapComponent(
            (controller.model.inventory.size, 1), 
            resources_manager.textures
        )
        self.tile_map.data.add_layer(0)
        self.tile_map.data.add_layer(0)
        self.tile_map.data.add_layer(1)

        self.render_slots()

    def render_slots(self) -> None:
        for slot in self.controller.model.inventory.slots:
            self.render_slot(slot)
            self.tile_map.data.set_value(30, 0, 0, (slot.slot_id, 0))
    
    def render_slot(self, slot: Slot) -> None:
        slot_id = slot.slot_id
        position = slot_id, 0

        if slot.item_type is None:
            self.tile_map.data.set_value("", 0, 2, position)
            self.tile_map.data.remove_value(0, 1, position)
        else:
            item_info = self.resource_manager.items_info[slot.item_type]
            texture_id = item_info.texture_id

            self.tile_map.data.set_value(texture_id, 0, 1, position)
            self.tile_map.data.set_value(str(slot.count), 0, 2, position)
    
        if slot_id == self.controller.model.inventory.selected_slot_id:
            self.tile_map.data.set_value(31, 0, 0, position)
        else:
            self.tile_map.data.set_value(30, 0, 0, position)

    def draw(self, camera: Camera) -> None:
        _, sh = Vector2(camera.scene.game.screen.get_size())
        tile_size = self.tile_map.renderer.tile_size

        self.tile_map.position = Vector2(
            -self.tile_map.size[0] / 2 * tile_size, 
            sh / 2 - tile_size
        )

        self.tile_map.draw(camera, zoom=False, static=True)
 
  
class InventoryController:
    view: InventoryView
    model: InventoryModel
    net_manager: ClientNetManager
    
    def __init__(self, net_manager: ClientNetManager, resources_manager: ResourcesManager) -> None:
        self.model = InventoryModel(self)
        self.view = InventoryView(self, resources_manager)
        self.net_manager = net_manager

    def add_item_type(self, count: int, item_type: int) -> None:
        slot = self.model.add_item_type(count, item_type)
    
        if slot is not None:
            self.view.render_slot(slot)
    
    def remove_item_type(self, count: int, item_type: int) -> None:
        slot = self.model.remove_item_type(count, item_type)
        
        if slot is not None:
            self.view.render_slot(slot)
    
    def set_inventory(self, inventory: Inventory) -> None:
        self.model.inventory = inventory
        self.view.render_slots()

    def set_selected_slot_id(self, slot_id: int) -> None:
        prev_selected_slot_id = self.model.inventory.selected_slot_id
        
        if slot_id == prev_selected_slot_id:
            self.model.inventory.selected_slot_id = None
        else:
            self.model.inventory.selected_slot_id = slot_id

        if slot_id is not None:
            self.view.render_slot(self.model.inventory.slots[slot_id])

        if prev_selected_slot_id is not None:
            self.view.render_slot(self.model.inventory.slots[prev_selected_slot_id])

    def get_selected_slot(self) -> Optional[Slot]:
        selected_slot_id = self.model.inventory.selected_slot_id

        if selected_slot_id is None:
            return
        
        return self.model.inventory.slots[selected_slot_id]

    def total_items(self) -> dict[int, int]:
        items = defaultdict(int)
        
        for slot in self.model.inventory.slots:
            if slot.item_type is not None:
                items[slot.item_type] += slot.count
        
        return dict(items)
    
    def net_update(self, player_id: int) -> None:
        self.net_manager.update_inventory(
            player_id,
            self.model.inventory.to_data(), 
            self.model.inventory.selected_slot_id
        )

    def draw(self, camera: Camera) -> None:
        self.view.draw(camera)
