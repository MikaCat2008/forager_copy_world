import socket, random
from typing import Optional

from network.server import BaseServer, ServerDispatcher
from network.models import (
    ChunkNetModel, 
    EntityNetModel, 
    PlayerNetModel, 
    InventoryNetModel
)
from network.methods import (
    JoinServer, 
    LoadChunk,
    MovePlayer,
    UpdateInventory,
    DamageStructure,
    DestroyStructure,
    GetPlayers
)
from network.updates import (
    PlayerJoin,
    ChunkLoad,
    EntitySpawn,
    PlayerMove,
    InventoryUpdate,
    StructureDamage,
    StructureDestroy
)

from world import WorldData, WorldGenerationManager


class Server(BaseServer):
    def player_join(self, connection: socket.socket, 
        player: PlayerNetModel
    ) -> None:
        return self(connection,
            PlayerJoin(
                player=player
            )
        )
    
    def chunk_load(self, connection: socket.socket, 
        chunk: ChunkNetModel
    ) -> None:
        return self(connection,
            ChunkLoad(
                chunk=chunk
            )
        )
    
    def entity_spawn(self, connection: socket.socket, 
        entity: EntityNetModel
    ) -> None:
        return self(connection,
            EntitySpawn(
                entity=entity
            )
        )
    
    def player_move(self, connection: socket.socket, 
        position: tuple[int, int], 
        player_id: int
    ) -> None:
        return self(connection,
            PlayerMove(
                position=position,
                player_id=player_id
            )
        )
    
    def inventory_update(self, connection: socket.socket, 
        player_id: int,
        inventory: InventoryNetModel
    ) -> None:
        return self(connection,
            InventoryUpdate(
                player_id=player_id,
                inventory=inventory
            )
        )
    
    def structure_damage(self, connection: socket.socket, 
        power: int,
        position: tuple[int, int],
        player_id: int
    ) -> None:
        return self(connection,
            StructureDamage(
                power=power,
                position=position,
                player_id=player_id
            )
        )
    
    def structure_destroy(self, connection: socket.socket, 
        position: tuple[int, int]
    ) -> None:
        return self(connection,
            StructureDestroy(
                position=position
            )
        )


server = Server()
dp = ServerDispatcher(server)


@dp.on(JoinServer)
def on_join_server(method: JoinServer) -> PlayerNetModel:
    player = PlayerNetModel(
        position=(random.randint(0, 400), random.randint(0, 400)), 
        entity_id=len(players), 
        player_id=len(players), 
        inventory=InventoryNetModel(
            data=[
                (1, 0),
                (1, 1),
                (1, 2),
                (1, 3),
                (1, 4),
                (1, 5),
                (0, None),
                (0, None),
                (0, None),
                (0, None)
            ], 
            selected_slot_id=5
        )
    )

    players.append(player)

    for connection in dp.connections:
        server.player_join(connection, player)

    return player


@dp.on(LoadChunk)
def on_load_chunk(method: LoadChunk) -> Optional[ChunkNetModel]:
    chunk = world.chunks.get(method.position)

    if chunk is None:
        return None
    
    return ChunkNetModel(
        blocks=chunk.blocks.data,
        position=method.position,
        structures=chunk.structures.data
    )


@dp.on(MovePlayer)
def on_move_player(method: MovePlayer) -> None:
    player = players[method.player_id]
    player.position = method.position

    for connection in dp.connections:
        server.player_move(connection, method.position, method.player_id)


@dp.on(UpdateInventory)
def on_update_inventory(method: UpdateInventory) -> None:
    inventory = InventoryNetModel(
        data=method.inventory_data, 
        selected_slot_id=method.selected_slot_id
    )

    players[method.player_id].inventory = inventory

    for connection in dp.connections:
        server.inventory_update(connection, method.player_id, inventory)


@dp.on(GetPlayers)
def on_get_players(method: GetPlayers) -> list[PlayerNetModel]:
    return players


world = WorldData()
players: list[PlayerNetModel] = []
generation_manager = WorldGenerationManager(world)
generation_manager.generate_chunks((20, 10))

dp.run()
