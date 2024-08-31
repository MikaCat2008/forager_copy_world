from __future__ import annotations

from typing import TYPE_CHECKING

from pygame.surface import Surface

from kit.graphics import Camera

from resources import ResourcesManager

if TYPE_CHECKING:
    from net_manager import ClientNetManager

from inventory import Inventory, InventoryController


class Player:
    position: tuple[int, int]
    entity_id: int
    player_id: int
    inventory: Inventory

    def __init__(
        self, 
        position: tuple[int, int], 
        entity_id: int, 
        player_id: int, 
        inventory: Inventory
    ) -> None:
        self.position = position
        self.entity_id = entity_id
        self.player_id = player_id
        self.inventory = inventory


class PlayerView:
    image: Surface
    controller: PlayerController
    resources_manager: ResourcesManager

    def __init__(self, controller: PlayerController, resources_manager: ResourcesManager) -> None:
        self.image = resources_manager.compiled_textures[1]
        self.controller = controller
        self.resources_manager = resources_manager

    def draw(self, camera: Camera) -> None:
        camera.blit(
            self.image, self.controller.model.player.position
        )

        inventory = self.controller.inventory.model.inventory

        selected_slot_id = inventory.selected_slot_id
        
        if selected_slot_id is None:
            return
        
        selected_slot = inventory.slots[selected_slot_id]

        if selected_slot.item_type is None:
            return
        
        item_info = self.resources_manager.items_info[selected_slot.item_type]

        position = self.controller.model.player.position

        camera.blit(
            self.resources_manager.textures[item_info.texture_id], 
            (position[0] + 26, position[1] + 24)
            # (position[0] + 16, position[1] + 20)
        )


class PlayerModel:
    player: Player
    controller: PlayerController
    
    def __init__(self, inventory: Inventory, controller: PlayerController) -> None:
        self.player = Player((0, 0), 0, 0, inventory)
        self.controller = controller


class PlayerController:
    view: PlayerView
    model: PlayerModel
    net_manager: ClientNetManager

    inventory: InventoryController

    def __init__(
        self, 
        net_manager: ClientNetManager, 
        resources_manager: ResourcesManager
    ) -> None:
        self.inventory = InventoryController(net_manager, resources_manager)
        
        self.view = PlayerView(self, resources_manager)
        self.model = PlayerModel(self.inventory.model.inventory, self)
        self.net_manager = net_manager

    def move(self, amount: tuple[int, int]) -> None:
        position = self.model.player.position
        new_position = position[0] + amount[0], position[1] + amount[1]

        self.set_position(new_position)

    def net_move(self) -> None:
        self.net_manager.move_player(
            self.model.player.position, self.model.player.player_id
        )

    def set_position(self, position: tuple[int, int]) -> None:
        self.model.player.position = position

    def set_entity_id(self, entity_id: int) -> None:
        self.model.player.entity_id = entity_id

    def set_player_id(self, player_id: int) -> None:
        self.model.player.player_id = player_id

    def set_inventory(self, inventory: InventoryController) -> None:
        self.inventory = inventory

    def draw(self, camera: Camera) -> None:
        self.view.draw(camera)
