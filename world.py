from __future__ import annotations

import random
from copy import deepcopy
from typing import Any, Callable, Optional, TYPE_CHECKING
from threading import Thread

from pygame.math import Vector2

from kit.math import vector2tuple
from kit.graphics import Camera
from kit.components.tile_map import TileMapComponent

from resources import ResourcesManager

if TYPE_CHECKING:
    from net_manager import ClientNetManager

Position = tuple[int, int]

CHUNK_SIZE = 16
DIRECTIONS4 = [ 
    (-1, 0), (0, 1), (1, 0), (0, -1) 
]
DIRECTIONS8 = [
    (0, 1), (1, 1), (1, 0), (1, -1),
    (0, -1), (-1, -1), (-1, 0), (-1, 1)
]


def start_thread(function: Callable, *args: Any) -> None:
    thread = Thread(target=function, args=args)
    thread.daemon = True
    thread.start()


class Layer:
    data: list[list[int]]

    def __init__(self, data: list[list[int]]) -> None:
        self.data = data

    @classmethod
    def filled(cls, value: int, size: Optional[tuple[int, int]] = None) -> Layer:
        if size:
            width, height = size
        else:
            width, height = CHUNK_SIZE, CHUNK_SIZE

        return Layer([ [value] * width for _ in range(height) ])

    def __getitem__(self, position: Position) -> None:
        x, y = position

        return self.data[y][x]

    def __setitem__(self, position: Position, value: int) -> None:
        x, y = position
        
        self.data[y][x] = value


class Chunk:
    blocks: Layer
    position: Position
    structures: Layer
    
    def __init__(self, blocks: Layer, position: Position, structures: Layer) -> None:
        self.blocks = blocks
        self.position = position
        self.structures = structures

    @staticmethod
    def get_chunk_position(position: Position) -> tuple[int, int]:
        return position[0] // CHUNK_SIZE, position[1] // CHUNK_SIZE
    
    @staticmethod
    def get_element_position(position: Position) -> tuple[int, int]:
        return position[0] % CHUNK_SIZE, position[1] % CHUNK_SIZE


class WorldData:
    chunks: dict[Position, Chunk]

    def __init__(self) -> None:
        self.chunks = {}

    def set_block_type(self, position: Position, block_type: int) -> None:
        chunk, element_position = self.get_chunk_by_element_position(position)

        chunk.blocks[element_position] = block_type

    def get_block_type(self, position: Position) -> int:
        chunk, element_position = self.get_chunk_by_element_position(position)

        return chunk.blocks[element_position]

    def set_structure_type(self, position: Position, structure_type: int) -> None:
        chunk, element_position = self.get_chunk_by_element_position(position)

        chunk.structures[element_position] = structure_type

    def get_structure_type(self, position: Position) -> int:
        chunk, element_position = self.get_chunk_by_element_position(position)

        return chunk.structures[element_position]

    def load_chunks(self, chunks: Chunk) -> None:
        for chunk in chunks:
            self.chunks[chunk.position] = chunk

    def unload_chunks(self, *positions: Position) -> None:
        for position in positions:
            del self.chunks[position]

    def get_chunk_by_element_position(self, position: Position) -> tuple[Chunk, Position]:
        chunk_position = Chunk.get_chunk_position(position)
        element_position = Chunk.get_element_position(position)

        return self.chunks[chunk_position], element_position

    def copy_data(self, size: tuple[int, int], position: Position) -> tuple[Layer, Layer]:
        blocks = [ [0] * size[0] for _ in range(size[1]) ]
        structures = [ [0] * size[0] for _ in range(size[1]) ]

        for cx in range(size[0] // CHUNK_SIZE):
            for cy in range(size[1] // CHUNK_SIZE):
                chunk_position = cx + position[0], cy + position[1]

                if chunk_position not in self.chunks:
                    continue

                chunk = self.chunks[chunk_position]

                for x in range(CHUNK_SIZE):
                    dx = x + cx * CHUNK_SIZE

                    for y in range(CHUNK_SIZE):
                        dy = y + cy * CHUNK_SIZE
                        
                        blocks[dy][dx] = chunk.blocks.data[y][x]
                        structures[dy][dx] = chunk.structures.data[y][x]

        return Layer(blocks), Layer(structures)
    
    def is_position_inside(self, position: Position) -> bool:
        chunk_position = Chunk.get_chunk_position(position)
        
        return chunk_position in self.chunks


class WorldModel:
    controller: WorldController

    data: WorldData

    def __init__(self, controller: WorldController) -> None:
        self.controller = controller

        self.data = WorldData()

    def set_block_type(self, position: tuple[int, int], block_type: int) -> None:
        self.data.set_block_type(position, block_type)

    def set_structure_type(self, position: tuple[int, int], structure_type: int) -> None:
        self.data.set_structure_type(position, structure_type)


class BlocksManager:
    size: tuple[int, int]
    tile_map: TileMapComponent

    blocks: Layer
    blocks_rules: dict[int, list[int]]

    def __init__(self, tile_map: TileMapComponent, resources_manager: ResourcesManager) -> None:
        self.size = tile_map.size
        self.tile_map = tile_map
        
        self.blocks = Layer.filled(0, size=self.size)
        self.blocks_rules = resources_manager.blocks_rules

    def update_block_texture(self, position: tuple[int, int]) -> None:
        x, y = position
        tile = self.tile_map.data.get_tile(position)
        block_type = self.blocks.data[y][x]

        if block_type == 0:
            return tile.remove_value(0, 0)

        variation = 0

        for i, (dx, dy) in enumerate(DIRECTIONS4):
            tx, ty = x + dx, y + dy
            
            if tx < 0 or ty < 0 or tx >= self.size[0] or ty >= self.size[1]:
                continue

            if self.blocks.data[ty][tx] == block_type:
                variation |= 2 ** i

        tile.set_value(self.blocks_rules[block_type][variation], 0, 0)
    
    def set_block_type(self, position: tuple[int, int], block_type: int) -> None:
        x, y = position

        self.blocks[position] = block_type
        self.update_block_texture(position)

        for dx, dy in DIRECTIONS4:
            nx, ny = x + dx, y + dy

            if nx < 0 or ny < 0 or nx >= self.size[0] or ny >= self.size[1]:
                continue

            self.update_block_texture((nx, ny))


class StructuresManager:
    size: tuple[int, int]
    tile_map: TileMapComponent

    structures: Layer
    structures_rules: dict[int, list[int]]

    def __init__(self, tile_map: TileMapComponent, resources_manager: ResourcesManager) -> None:
        self.size = tile_map.size
        self.tile_map = tile_map
        
        self.structures = Layer.filled(0, size=self.size)
        self.structures_rules = resources_manager.sctructures_rules

    def set_structure_type(self, position: tuple[int, int], structure_type: int) -> None:
        prev_structure_type = self.structures[position]
        
        if structure_type == prev_structure_type:
            return

        if structure_type == 0:
            self.remove_structure_type(position, prev_structure_type)
        else:
            self.blit_structure_type(position, structure_type)

        self.structures[position] = structure_type

    def blit_structure_type(self, position: tuple[int, int], structure_type: int) -> None:
        x, y = position
        structure = self.structures_rules[structure_type]

        for oy, row in enumerate(structure):
            ty = y - oy

            if ty < 0:
                break
            
            for ox, texture_id in enumerate(row):
                tx = x + ox

                if tx >= self.size[0]:
                    continue

                tile = self.tile_map.data.get_tile((tx, ty))
                tile.set_value(texture_id, oy, 1)

    def remove_structure_type(self, position: tuple[int, int], structure_type: int) -> None:
        x, y = position
        structure = self.structures_rules[structure_type]

        for oy, row in enumerate(structure):
            ty = y - oy

            if ty < 0:
                break
            
            for ox, _ in enumerate(row):
                tx = x + ox

                if tx >= self.size[0]:
                    continue

                tile = self.tile_map.data.get_tile((tx, ty))
                tile.remove_value(oy, 1)


class WorldView:
    controller: WorldController
    resources_manager: ResourcesManager

    tile_map: TileMapComponent
    position: Position
    
    blocks_manager: BlocksManager
    structures_manager: StructuresManager

    def __init__(self, controller: WorldController, resources_manager: ResourcesManager) -> None:
        self.controller = controller
        self.resources_manager = resources_manager

        self.tile_map = TileMapComponent(
            (96, 64), controller.resources_manager.textures
        )
        self.tile_map.data.add_layer(0)
        self.tile_map.data.add_layer(0)
        self.position = 0, 0

        self.blocks_manager = BlocksManager(self.tile_map, resources_manager)
        self.structures_manager = StructuresManager(self.tile_map, resources_manager)

    def set_block_type(self, position: tuple[int, int], block_type: int) -> None:
        self.blocks_manager.set_block_type(position, block_type)

    def set_structure_type(self, position: tuple[int, int], structure_type: int) -> None:
        self.structures_manager.set_structure_type(position, structure_type)

    def get_render_chunks(self) -> list[Chunk]:
        wx, wy = self.position
        chunks = []
        world_chunks = self.controller.model.data.chunks

        for x in range(6):
            cx = x + wx

            for y in range(4):
                position = cx, y + wy

                if position in world_chunks:
                    chunks.append(world_chunks[position])
                else:
                    start_thread(self.controller.net_load_chunk, position)

        return chunks

    def render_chunks(self, chunks: list[Chunk]) -> None:
        wx, wy = self.position
        
        for chunk in chunks:
            cx, cy = chunk.position
            cx -= wx
            cy -= wy

            if cx >= self.tile_map.size[0] // CHUNK_SIZE or cy >= self.tile_map.size[1] // CHUNK_SIZE:
                continue

            for y, row in enumerate(chunk.blocks.data):
                ty = cy * CHUNK_SIZE + y
                
                for x, block_type in enumerate(row):
                    tx = cx * CHUNK_SIZE + x

                    if block_type != 0:
                        self.set_block_type((tx, ty), block_type)

            for y, row in enumerate(chunk.structures.data):
                ty = cy * CHUNK_SIZE + y
                
                for x, structure_type in enumerate(row):
                    tx = cx * CHUNK_SIZE + x

                    if structure_type != 0:
                        self.set_structure_type((tx, ty), structure_type)

    def offset(self, offset: tuple[int, int]) -> None:
        self.position = offset
        self.tile_map.position = Vector2(offset) * CHUNK_SIZE * self.tile_map.renderer.tile_size

        chunks = self.get_render_chunks()

        self.tile_map.data.clear()
        self.blocks_manager.blocks = Layer.filled(0, size=self.tile_map.size)
        self.structures_manager.structures = Layer.filled(0, size=self.tile_map.size)

        self.render_chunks(chunks)

    def draw(self, camera: Camera) -> None:
        self.tile_map.draw(camera)


class WorldController:
    net_manager: ClientNetManager
    resources_manager: ResourcesManager

    view: WorldView
    model: WorldModel

    def __init__(self, net_manager: ClientNetManager, resources_manager: ResourcesManager) -> None:
        self.net_manager = net_manager
        self.resources_manager = resources_manager

        self.view = WorldView(self, resources_manager)
        self.model = WorldModel(self)

    def load_chunks(self, chunks: list[Chunk]) -> None:
        self.model.data.load_chunks(chunks)
        self.view.render_chunks(chunks)

    def set_block_type(self, position: tuple[int, int], block_type: int) -> None:
        self.view.set_block_type(position, block_type)
        self.model.set_block_type(position, block_type)

    def set_structure_type(self, position: tuple[int, int], structure_type: int) -> None:
        self.view.set_structure_type(position, structure_type)
        self.model.set_structure_type(position, structure_type)

    def net_load_chunk(self, position: tuple[int, int]) -> None:
        chunk = self.net_manager.load_chunk(position)

        if chunk is None:
            return

        with self.net_manager.client.lock:
            self.load_chunks([chunk])

    def draw(self, camera: Camera) -> None:
        self.view.draw(camera)


class WorldGenerationManager:
    controller: WorldController

    def __init__(self, controller: WorldController) -> None:
        self.controller = controller

    def count_neighbours(self, blocks: list[list[int]], position: tuple[int, int]) -> int:
        x, y = position
        count = 0
        
        for dx, dy in DIRECTIONS8:
            nx, ny = x + dx, y + dy
            
            if nx < 0 or ny < 0 or nx >= len(blocks[0]) or ny >= len(blocks):
                continue
                
            count += blocks[ny][nx]
        
        return count

    def generate_chunks(self, size: tuple[int, int]) -> None:
        blocks = [
            [
                1 if random.random() < 0.5 else 0 
                for _ in range(size[0] * CHUNK_SIZE)
            ] 
            for _ in range(size[1] * CHUNK_SIZE)
        ]
        structures = [[0] * size[0] * CHUNK_SIZE for _ in range(size[1] * CHUNK_SIZE)]

        for _ in range(4):
            new_blocks = deepcopy(blocks)
            
            for y in range(len(blocks)):
                for x in range(len(blocks[0])):
                    count = self.count_neighbours(blocks, (x, y))
                
                    if blocks[y][x]:
                        new_blocks[y][x] = int(count >= 4)
                    else:
                        new_blocks[y][x] = int(count >= 5)
                
            blocks = new_blocks

        for y, row in enumerate(blocks):
            for x, block in enumerate(row):
                if not block:
                    continue
                
                if random.random() > 0.25:
                    continue

                structures[y][x] = random.randint(1, 9)

        chunks = [
            Chunk(Layer.filled(0), (x, y), Layer.filled(1))
            for x in range(size[0])
            for y in range(size[1])
        ]

        for chunk in chunks:
            cx, cy = chunk.position

            for x in range(CHUNK_SIZE):
                bx = cx * CHUNK_SIZE + x

                for y in range(CHUNK_SIZE):
                    by = cy * CHUNK_SIZE + y

                    chunk.blocks[x, y] = blocks[by][bx]
                    chunk.structures[x, y] = structures[by][bx]

        self.controller.load_chunks(chunks)
