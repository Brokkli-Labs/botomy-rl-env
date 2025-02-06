from typing import List
from fastapi import FastAPI, Request
import asyncio
import threading

from models import LevelData, Move, GameState

app = FastAPI()

class ServerState:
    def __init__(self):
        self.should_reset = True
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
        self.data_event = threading.Event()  # Event to signal data update
        self.moves : List[Move] = []
        self.reset_options = {}
        self.reset_seed = None

server_state = ServerState()

@app.post("/")
async def play(request: Request):
    body = await request.json()
    level_data = LevelData.from_dict(body)  # Use from_dict instead of from_json
    server_state.skip_frame_count += 1
    if server_state.skip_frames > 0 and server_state.skip_frame_count >= server_state.skip_frames:
        server_state.skip_frame_count = 0
        return []
    server_state.data = level_data  # Update the data with level_data
    server_state.data_event.set()  # Signal that data has been updated
    moves = server_state.moves
    server_state.moves = []
    return moves

@app.get("/reset")
def reset():
    response = {
        "reset": server_state.should_reset,
        "seed": server_state.reset_seed,
        "options": server_state.reset_options,
        }
    server_state.should_reset = False
    return response

async def get_data():
    # Wait for the data to be updated by the play method
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, server_state.data_event.wait)
    server_state.data_event.clear()  # Reset the event for future use
    return server_state.data

def set_should_reset(value: bool, seed = None, options: dict = None):
    server_state.should_reset = value
    server_state.reset_seed = seed
    server_state.reset_options = options
    server_state.data_event.clear()

def set_moves(moves: List[Move]):
    server_state.moves = moves
    server_state.data_event.clear()

def set_skip_frames(count):
    server_state.skip_frames = count

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)
