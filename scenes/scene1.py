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
from kit.input import Keyboard
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
    StructureDestroy
)

from client import Client

from resources import ResourcesManager
from net_manager import ClientNetManager

from world import Chunk, Layer, WorldController, CHUNK_SIZE, start_thread
from player import PlayerController
from crafting import CraftingMenuController
from inventory import Inventory, InventoryController


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

        @self.dispatcher.on(PlayerJoin)
        def on_player_join(update: PlayerJoin) -> None:
            player = self.net_manager.net_model_adapter.adapt_player(update.player)

            self.players.append(player)

        @self.dispatcher.on(PlayerMove)
        def on_player_move(update: PlayerMove) -> None:
            if self.player is not None and update.player_id == self.player.model.player.player_id:
                return

            player = [
                player for player in self.players if player.model.player.player_id == update.player_id
            ][0]

            player.set_position(update.position)

        @self.dispatcher.on(InventoryUpdate)
        def on_inventory_update(update: InventoryUpdate) -> None:
            if self.player is not None and update.player_id == self.player.model.player.player_id:
                return

            player = [
                player for player in self.players if player.model.player.player_id == update.player_id
            ][0]

            inventory = self.net_manager.net_model_adapter.adapt_inventory(update.inventory)

            player.set_inventory(inventory)

        start_thread(self.dispatcher.run)

        self.players = self.net_manager.get_players()
        self.player = self.net_manager.join_server()

        self.player = [
            player for player in self.players
            if player.model.player.player_id == self.player.model.player.player_id
        ][0]

        self.crafting_menu = CraftingMenuController(
            self.camera, self.player.inventory, resources_manager
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

        if self.game.ticks % 5 == 0:
            start_thread(self.player.net_move)
            
        if self.game.ticks % 20 == 0:
            start_thread(self.player.inventory.net_update, self.player.model.player.player_id)

        position = self.camera.position // self.world.view.tile_map.renderer.tile_size // CHUNK_SIZE
        position -= Vector2(3, 2)

        if position != self.world.view.position:
            self.world.view.offset(vector2tuple(position))

        self.crafting_menu.update()

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
