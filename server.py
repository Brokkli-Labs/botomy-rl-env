from typing import List
from fastapi import FastAPI, Request
import asyncio
import threading

from models import LevelData, Move, GameState

app = FastAPI()

class ServerState:
    def __init__(self):
        self.should_reset = False
        self.skip_frames = 0
        self.skip_frame_count = 0
        
        self.data: LevelData = LevelData(
            game_info={
                "friendly_fire": True,
                "game_type": "rpg",
                "map": "default",
                "match_id": "",
                "state": GameState.WAITING,
                "time_remaining_s": 0,
                "latency": 0
            },
            own_player={},
            items=[],
            enemies=[],
            players=[],
            obstacles=[],
            hazards=[],
            stats=[]
        )
        self.wait_for_data_event = threading.Event()  # Event to signal data update
        self.send_action_event = threading.Event()  # Event to signal data update
        self.moves : List[Move] = []
        self.reset_options = {}
        self.reset_seed = None

server_state = ServerState()

@app.post("/")
async def play(request: Request):
    if not (server_state.send_action_event.is_set() or server_state.wait_for_data_event.is_set()):
        return []

    server_state.skip_frame_count += 1
    if server_state.skip_frames > 0 and server_state.skip_frame_count >= server_state.skip_frames:
        server_state.skip_frame_count = 0
        return []
    
    if server_state.wait_for_data_event.is_set():
      # print("setting data")
      body = await request.json()
      level_data = LevelData.from_dict(body)  # Use from_dict instead of from_json
      server_state.data = level_data  # Update the data with level_data
      server_state.wait_for_data_event.clear()  # Signal that data has been updated
    
    moves = []
    if server_state.send_action_event.is_set():
      moves = server_state.moves
      server_state.moves = []
      server_state.send_action_event.clear()
      server_state.wait_for_data_event.set()
    
    return moves

@app.get("/reset")
def reset():
    response = {
        "reset": server_state.should_reset,
        "seed": server_state.reset_seed,
        "options": server_state.reset_options,
        }
    if server_state.should_reset:
      server_state.send_action_event.clear()
      server_state.wait_for_data_event.set()
    server_state.should_reset = False
    # print("reset")
    return response

async def wait_for_data_set():
    while server_state.wait_for_data_event.is_set():
        await asyncio.sleep(0.001)  # Use asyncio.sleep to yield control

async def get_data(immediate=False):
    if not immediate:
        # Wait for the api call
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, server_state.wait_for_data_event.wait)
    else:
        server_state.wait_for_data_event.set()

    # Wait for the next api call
    await wait_for_data_set()  # Await the coroutine properly
    server_state.wait_for_data_event.clear()  # Reset the event for future use
    return server_state.data

def set_should_reset(value: bool, seed = None, options: dict = None):
    server_state.should_reset = value
    server_state.reset_seed = seed
    server_state.reset_options = options
    server_state.data = LevelData(
            game_info={
                "friendly_fire": True,
                "game_type": "rpg",
                "map": "default",
                "match_id": "",
                "state": GameState.WAITING,
                "time_remaining_s": 0,
                "latency": 0
            },
            own_player={},
            items=[],
            enemies=[],
            players=[],
            obstacles=[],
            hazards=[],
            stats=[]
        )

def set_moves(moves: List[Move]):
    server_state.moves = moves
    server_state.wait_for_data_event.clear()
    server_state.send_action_event.set()

def set_skip_frames(count):
    server_state.skip_frames = count

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)
