from typing import Optional

from pygame.surface import Surface

from kit.content import Content


class ItemInfo:
    name: str
    item_type: int
    texture_id: int

    recipe: Optional[dict[int, int]]
    axe_power: int
    pickaxe_power: int
    place_structure: int

    def __init__(
        self, 
        name: str, 
        item_type: int,
        texture_id: int,
        recipe: Optional[dict[int]] = None,
        axe_power: int = 0,
        pickaxe_power: int = 0,
        place_structure: int = 0
    ) -> None:
        self.name = name
        self.item_type = item_type
        self.texture_id = texture_id
        
        self.recipe = recipe
        self.axe_power = axe_power
        self.pickaxe_power = pickaxe_power
        self.place_structure = place_structure


class StructureInfo:
    structure_type: int
    drop_items: Optional[dict[int, int]]
    min_axe_power: Optional[int]
    min_pickaxe_power: Optional[int]

    def __init__(
        self, 
        structure_type: int,
        drop_items: Optional[dict[int, int]] = None,
        min_axe_power: int = 0,
        min_pickaxe_power: int = 0
    ) -> None:
        self.structure_type = structure_type
        self.drop_items = drop_items
        self.min_axe_power = min_axe_power
        self.min_pickaxe_power = min_pickaxe_power


class ResourcesManager:
    textures: list[Surface]
    items_info: list[ItemInfo]
    
    def __init__(self) -> None:
        self.textures = Content.load_tileset(
            "textures/tileset.png", 32, [
                ( 0,  0), ( 1,  0), ( 2,  0), ( 3,  0), # 3
                ( 0,  1), ( 1,  1), ( 2,  1), ( 3,  1), # 7
                ( 0,  2), ( 1,  2), ( 2,  2), ( 3,  2), # 11
                ( 0,  3), ( 1,  3), ( 2,  3), ( 3,  3), # 15

                ( 4,  0), ( 4,  1), ( 4,  2), ( 4,  3), # 16
                ( 5,  0), ( 5,  1), ( 5,  2), ( 5,  3), # 20
                ( 6,  0), ( 6,  1), ( 6,  2), ( 6,  3), # 24

                ( 7,  0), ( 7,  1), ( 7,  2), ( 7,  3), # 28
                ( 8,  0), ( 8,  1), ( 9,  0), ( 9,  1), # 32
 
                ( 8,  2), ( 9,  2), (10,  2), (-1, -1), # 36
                ( 8,  3), ( 9,  3), (10,  3), (-1, -1), # 40
                (-1, -1), (-1, -1), (-1, -1), (-1, -1), # 44
                (-1, -1), (-1, -1), (-1, -1), (-1, -1), # 48
                (-1, -1), (-1, -1), (-1, -1), (-1, -1), # 52
            ]
        )
        self.compiled_textures = [
            Content.compile_texture([
                [28], [29]
            ], self.textures, 32),
            Content.compile_texture([
                [32, 34], [33, 35]
            ], self.textures, 32)
        ]

        self.blocks_rules = {
            1: [
                15, 14,  3,  2, 12, 13,  0,  1, 
                11, 10,  7,  6,  8,  9,  4,  5
            ]
        }
        self.structures_rules = {
            1: [[17], [16]],
            2: [[19], [18]],
            3: [[20]],
            4: [[21]],
            5: [[22]],
            6: [[23]],
            7: [[24]],
            8: [[25]],
            9: [[26]],
            10: [[27]]
        }

        self.items_info = [
            ItemInfo(
                name="Wood", 
                item_type=0, 
                texture_id=36
            ),
            ItemInfo(
                name="Stone", 
                item_type=1, 
                texture_id=40
            ),
            ItemInfo(
                name="Wooden pickaxe", 
                item_type=2, 
                texture_id=37, 
                recipe={ 0: 12 },
                pickaxe_power=1
            ),
            ItemInfo(
                name="Wooden axe", 
                item_type=3, 
                texture_id=38, 
                recipe={ 0: 10 },
                axe_power=2
            ),
            ItemInfo(
                name="Stone pickaxe", 
                item_type=4, 
                texture_id=41, 
                recipe={ 0: 4, 1: 12 },
                pickaxe_power=2
            ),
            ItemInfo(
                name="Stone axe", 
                item_type=5, 
                texture_id=42, 
                recipe={ 0: 4, 1: 10 },
                axe_power=3
            ),
            ItemInfo(
                name="Bridge",
                item_type=6,
                texture_id=27,
                recipe={ 0: 20 },
                place_structure=10
            )
        ]
        self.structures_info = [None,
            StructureInfo(
                structure_type=1,
                drop_items={ 0: 2 },
                min_axe_power=1
            ),
            StructureInfo(
                structure_type=2,
                drop_items={ 0: 3 },
                min_axe_power=1
            ),
            StructureInfo(
                structure_type=3
            ),
            StructureInfo(
                structure_type=4
            ),
            StructureInfo(
                structure_type=5
            ),
            StructureInfo(
                structure_type=6
            ),
            StructureInfo(
                structure_type=7,
                drop_items={ 1: 1 },
                min_pickaxe_power=1
            ),
            StructureInfo(
                structure_type=8,
                drop_items={ 1: 2 },
                min_pickaxe_power=1
            ),
            StructureInfo(
                structure_type=9,
                drop_items={ 0: 4 },
                min_axe_power=2
            ),
            StructureInfo(
                structure_type=10,
                drop_items={ 0: 20 },
                min_axe_power=1
            )
        ]
