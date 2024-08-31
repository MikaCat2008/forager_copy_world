from __future__ import annotations

from pygame.math import Vector2

from kit.input import Mouse
from kit.graphics import Camera
from kit.components.tile_map import TileMapComponent

from resources import ResourcesManager
from inventory import Slot, Inventory, InventoryController


class CraftingMenuModel:
    inventory: InventoryController
    controller: CraftingMenuController
    resources_manager: ResourcesManager

    recipes_inventory: Inventory

    def __init__(
        self, 
        inventory: InventoryController, 
        controller: CraftingMenuController,
        resources_manager: ResourcesManager
    ) -> None:
        self.inventory = inventory
        self.controller = controller
        self.resources_manager = resources_manager
        
        self.recipes_inventory = Inventory(10)

    def craft(self, item_type: int) -> None:
        item_info = self.resources_manager.items_info[item_type]
        recipe = item_info.recipe
        
        for recipe_item_type, count in recipe.items():
            self.inventory.remove_item_type(count, recipe_item_type)
        
        self.inventory.add_item_type(1, item_type)

    def get_avaliable_recipes(self) -> list[int]:
        items = self.inventory.total_items()
        recipes = set()
        
        for item_info in self.resources_manager.items_info:
            recipe = item_info.recipe
        
            if recipe is None:
                continue
            
            for item_type, count in recipe.items():
                if items.get(item_type, 0) < count:
                    break
            else:
                recipes.add(item_info.item_type)
        
        return list(recipes)

    def update(self) -> None:
        recipes = self.get_avaliable_recipes()

        data = [(1, item_type) for item_type in recipes]

        if self.recipes_inventory.to_data() == data:
            return
        
        self.controller.set_recipes_inventory(Inventory.from_data(data, 10))


class CraftingMenuView:
    camera: Camera
    controller: CraftingMenuController
    resources_manager: ResourcesManager

    tile_map: TileMapComponent

    def __init__(
        self, 
        camera: Camera,
        controller: CraftingMenuController, 
        resources_manager: ResourcesManager
    ) -> None:
        self.camera = camera
        self.controller = controller
        self.resources_manager = resources_manager

        self.tile_map = TileMapComponent(
            (1, controller.model.recipes_inventory.size), 
            resources_manager.textures
        )
        self.tile_map.data.add_layer(0)
        self.tile_map.data.add_layer(0)
        self.tile_map.data.add_layer(1)

        self.tile_map.position = Vector2(
            -Vector2(camera.scene.game.screen.get_size()) / 2 + Vector2(3, 5)
        )

        self.render_slots()

    def render_slots(self) -> None:
        for slot in self.controller.model.recipes_inventory.slots:
            self.render_slot(slot)

    def render_slot(self, slot: Slot) -> None:
        position = 0, slot.slot_id

        if slot.item_type is None:
            self.tile_map.data.remove_value(0, 0, position)
            self.tile_map.data.remove_value(0, 1, position)
            self.tile_map.data.remove_value(0, 2, position)
        else:
            item_info = self.resources_manager.items_info[slot.item_type]
            texture_id = item_info.texture_id

            self.tile_map.data.set_value(30, 0, 0, position)
            self.tile_map.data.set_value(texture_id, 0, 1, position)
            self.tile_map.data.set_value(str(slot.count), 0, 2, position)

    def update(self) -> None:
        if not Mouse.get_clicked(0):
            return 
        
        sw, sh = self.camera.scene.game.screen.get_size()
        mx, my = Mouse.get_pos()
        tx, ty = self.tile_map.position
        tile_size = self.tile_map.renderer.tile_size
        
        if not (0 < mx - tx - sw / 2 < tile_size):
            return

        slot_id = int(my - ty - sh / 2) // tile_size

        if slot_id >= self.controller.model.recipes_inventory.size:
            return

        slot = self.controller.model.recipes_inventory.slots[slot_id]

        if slot.item_type is None:
            return
        
        self.controller.model.craft(slot.item_type)
        self.render_slots()

    def draw(self, camera: Camera) -> None:
        self.tile_map.draw(camera, zoom=False, static=True)


class CraftingMenuController: 
    view: CraftingMenuView
    model: CraftingMenuModel
    
    def __init__(
        self, 
        camera: Camera, 
        inventory: InventoryController, 
        resources_manager: ResourcesManager
    ) -> None:
        self.model = CraftingMenuModel(inventory, self, resources_manager)
        self.view = CraftingMenuView(camera, self, resources_manager)

    def set_recipes_inventory(self, inventory: Inventory) -> None:
        self.model.recipes_inventory = inventory
        self.view.render_slots()

    def update(self) -> None:
        self.view.update()
        self.model.update()

    def draw(self, camera: Camera) -> None:
        self.view.draw(camera)
