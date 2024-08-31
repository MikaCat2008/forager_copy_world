from resources import ResourcesManager
from inventory import InventoryController


class CraftingManager:
    resources_manager: ResourcesManager
 
    def __init__(self, resource_manager: ResourcesManager) -> None:
        self.resource_manager = resource_manager
  
    def avaliable_recipes(self, inventory: InventoryController) -> list[int]:
        items = inventory.todict()
        recipes = set()
        
        for item_info in self.resource_manager.items_info:
            recipe = item_info.recipe
        
            if recipe is None:
                continue
            
            for item_type, count in recipe.items():
                if items[item_type] < count:
                    break
            else:
                recipes.add(item_info.item_type)
        
        return list(recipes)
  
    def craft(self, item_type: int, inventory: InventoryController) -> None:
        item_info = self.resource_manager.items_info[item_type]
        recipe = item_info.recipe
        
        for _item_type, count in recipe.items():
            inventory.remove_item_type(count, _item_type)
        
        inventory.add_item_type(1, item_type)
