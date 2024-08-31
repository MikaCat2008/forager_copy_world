from typing import Optional

from pygame.surface import Surface

from kit.content import Content


class ItemInfo:
    name: str
    recipe: Optional[dict[int, int]]
    item_type: int
    texture_id: int
    
    def __init__(
        self, 
        name: str, 
        item_type: int,
        texture_id: int,
        recipe: Optional[dict[int]] = None
    ) -> None:
        self.name = name
        self.recipe = recipe
        self.item_type = item_type
        self.texture_id = texture_id


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
        self.sctructures_rules = {
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
            ItemInfo("Wood", 0, 36),
            ItemInfo("Stone", 1, 40),
            ItemInfo(
                "Wooden pickaxe", 2, 37, { 0: 12 }
            ),
            ItemInfo(
                "Wooden axe", 3, 38, { 0: 10 }
            ),
            ItemInfo(
                "Stone pickaxe", 4, 41, { 0: 4, 1: 12 }
            ),
            ItemInfo(
                "Stone axe", 5, 42, { 0: 4, 1: 10 }
            )
        ]
