from __future__ import annotations

# import json
import time, random
from typing import Any, Callable, Optional
from threading import Thread

import pygame as pg
from pygame.math import Vector2
from pygame.display import set_caption

from kit.math import vector2tuple
from kit.scene import Scene
from kit.input import Mouse, Keyboard
from kit.graphics import Color, Camera

from network.client import ClientDispatcher
from network.models import (
    ChunkNetModel,
    EntityNetModel,
    PlayerNetModel,
    InventoryNetModel
)
from network.updates import (
    PlayerJoin,
    PlayerMove,
    InventoryUpdate,
    StructureDamage,
    StructureDestroy,
    StructurePlace
)

from client import Client

from resources import ResourcesManager
from net_manager import ClientNetManager

from world import Chunk, Layer, WorldController, CHUNK_SIZE, start_thread
from player import PlayerController
from crafting import CraftingMenuController
from inventory import Inventory, InventoryController


class PlacingManager:
    world: WorldController
    camera: Camera
    player: PlayerController
    net_manager: ClientNetManager
    resources_manager: ResourcesManager

    def __init__(
        self,
        world: WorldController,
        camera: Camera,
        player: PlayerController,
        net_manager: ClientNetManager,
        resources_manager: ResourcesManager
    ) -> None:
        self.world = world
        self.camera = camera
        self.player = player
        self.net_manager = net_manager
        self.resources_manager = resources_manager
    
    def update(self) -> None:
        cursor_position = vector2tuple(self.camera.get_mouse_position() // 32)
    
        if not Mouse.get_clicked(2):
            return
        
        if not self.world.model.data.is_position_inside(cursor_position):
            return
         
        structure_type = self.world.get_structure_type(cursor_position)
        
        if structure_type != 0:
            return
        
        slot = self.player.inventory.get_selected_slot()
        
        if slot is None or slot.item_type is None:
            return
        
        item_info = self.resources_manager.items_info[slot.item_type]

        if not item_info.place_structure:
            return
        
        self.player.inventory.remove_item_type(1, slot.item_type)

        start_thread(self.world.net_place_structure, cursor_position, item_info.place_structure)


class DestroyingManager:
    world: WorldController
    camera: Camera
    player: PlayerController
    net_manager: ClientNetManager
    resources_manager: ResourcesManager

    def __init__(
        self,
        world: WorldController,
        camera: Camera,
        player: PlayerController,
        net_manager: ClientNetManager,
        resources_manager: ResourcesManager
    ) -> None:
        self.world = world
        self.camera = camera
        self.player = player
        self.net_manager = net_manager
        self.resources_manager = resources_manager
    
    def update(self) -> None:
        cursor_position = vector2tuple(self.camera.get_mouse_position() // 32)
    
        if not Mouse.get_clicked(0):
            return
        
        if not self.world.model.data.is_position_inside(cursor_position):
            return
         
        structure_type = self.world.get_structure_type(cursor_position)
        
        if structure_type == 0:
            return
            
        slot = self.player.inventory.get_selected_slot()
        
        if slot is None or slot.item_type is None:
            axe_power = 1
            pickaxe_power = 0
        else:
            item_info = self.resources_manager.items_info[slot.item_type]

            axe_power = item_info.axe_power
            pickaxe_power = item_info.pickaxe_power

        structure_info = self.resources_manager.structures_info[structure_type]

        if axe_power < structure_info.min_axe_power:
            return

        if pickaxe_power < structure_info.min_pickaxe_power:
            return
        
        if structure_info.drop_items:
            for item_type, count in structure_info.drop_items.items():
                self.player.inventory.add_item_type(count, item_type)

        start_thread(self.world.net_destroy_structure, cursor_position)


class Scene1(Scene):
    client: Client
    dispatcher: ClientDispatcher

    world: WorldController
    player: Optional[PlayerController]
    players: list[PlayerController]

    def initialize(self) -> None:
        super().initialize()
        
        self.camera = Camera(self, 1, Vector2(), background_color=Color(76, 96, 213))
        
        resources_manager = ResourcesManager()

        self.client = Client()
        self.dispatcher = ClientDispatcher(self.client)
        self.net_manager = ClientNetManager(
            self.client, self.dispatcher, resources_manager
        )
        self.world = WorldController(self.net_manager, resources_manager)
        self.player = None
        self.players = []

        @self.dispatcher.on(PlayerJoin)
        def on_player_join(update: PlayerJoin) -> None:
            player = self.net_manager.net_model_adapter.adapt_player(update.player)

            self.players.append(player)

        @self.dispatcher.on(PlayerMove)
        def on_player_move(update: PlayerMove) -> None:
            if self.player is not None and update.player_id == self.player.model.player.player_id:
                return

            if not self.players:
                return

            player = [
                player for player in self.players if player.model.player.player_id == update.player_id
            ][0]

            player.set_position(update.position)

        @self.dispatcher.on(InventoryUpdate)
        def on_inventory_update(update: InventoryUpdate) -> None:
            if self.player is not None and update.player_id == self.player.model.player.player_id:
                return
            
            if not self.players:
                return

            player = [
                player for player in self.players if player.model.player.player_id == update.player_id
            ][0]

            inventory = self.net_manager.net_model_adapter.adapt_inventory(update.inventory)

            player.set_inventory(inventory)

        @self.dispatcher.on(StructureDestroy)
        def on_structure_destroy(update: StructureDestroy) -> None:
            self.world.set_structure_type(update.position, 0)

        @self.dispatcher.on(StructurePlace)
        def on_structure_place(update: StructurePlace) -> None:
            self.world.set_structure_type(update.position, update.structure_type)

        start_thread(self.dispatcher.run)

        self.players += self.net_manager.get_players()
        self.player = self.net_manager.join_server()

        self.player = [
            player for player in self.players
            if player.model.player.player_id == self.player.model.player.player_id
        ][0]

        self.crafting_menu = CraftingMenuController(
            self.camera, self.player.inventory, resources_manager
        )
        self.placing_manager = PlacingManager(
            self.world, 
            self.camera, 
            self.player, 
            self.net_manager, 
            resources_manager
        )
        self.destroying_manager = DestroyingManager(
            self.world, 
            self.camera, 
            self.player, 
            self.net_manager, 
            resources_manager
        )

        for position in [(x, y) for x in range(8) for y in range(6)]:
            start_thread(self.world.net_load_chunk, position)

    def update(self) -> None:
        self.camera.update(False)

        move = Vector2()
        velocity = 0.25 * self.game.delta

        if Keyboard.get_pressed(pg.K_a):
            move.x -= velocity
        if Keyboard.get_pressed(pg.K_d):
            move.x += velocity
        if Keyboard.get_pressed(pg.K_w):
            move.y -= velocity
        if Keyboard.get_pressed(pg.K_s):
            move.y += velocity

        if move.x or move.y:
            self.player.move(vector2tuple(move))
        
        self.camera.position = Vector2(self.player.model.player.position) 
        self.camera.position += Vector2(self.player.view.image.get_size()) / 2

        if Keyboard.get_clicked(pg.K_1):
            self.player.inventory.set_selected_slot_id(0)
        if Keyboard.get_clicked(pg.K_2):
            self.player.inventory.set_selected_slot_id(1)
        if Keyboard.get_clicked(pg.K_3):
            self.player.inventory.set_selected_slot_id(2)
        if Keyboard.get_clicked(pg.K_4):
            self.player.inventory.set_selected_slot_id(3)
        if Keyboard.get_clicked(pg.K_5):
            self.player.inventory.set_selected_slot_id(4)
        if Keyboard.get_clicked(pg.K_6):
            self.player.inventory.set_selected_slot_id(5)
        if Keyboard.get_clicked(pg.K_7):
            self.player.inventory.set_selected_slot_id(6)
        if Keyboard.get_clicked(pg.K_8):
            self.player.inventory.set_selected_slot_id(7)
        if Keyboard.get_clicked(pg.K_9):
            self.player.inventory.set_selected_slot_id(8)
        if Keyboard.get_clicked(pg.K_0):
            self.player.inventory.set_selected_slot_id(9)

        position = self.camera.position // self.world.view.tile_map.renderer.tile_size // CHUNK_SIZE
        position -= Vector2(3, 2)

        if position != self.world.view.position:
            self.world.view.offset(vector2tuple(position))

        self.crafting_menu.update()
        self.placing_manager.update()
        self.destroying_manager.update()

        if self.game.ticks % 5 == 0:
            start_thread(self.player.net_move)
            
        if self.game.ticks % 20 == 0:
            start_thread(self.player.inventory.net_update, self.player.model.player.player_id)

    def draw(self) -> None:
        super().draw()

        self.world.draw(self.camera)

        for player in self.players:
            player.draw(self.camera)

        self.player.inventory.draw(self.camera)
        self.crafting_menu.draw(self.camera)

        fps = f"{self.game.clock.get_fps():.2f} fps"
        zoom = f"{self.camera.zoom:.2f} zoom"

        set_caption(f"{fps} | {zoom}")


__scene__ = Scene1
