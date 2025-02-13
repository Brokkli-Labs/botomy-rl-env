import gymnasium as gym
from gymnasium import spaces
import numpy as np
from server import app, step, reset, get_data
from models import Position, GameState, LevelData
from util import serialize_player, serialize_own_player, serialize_enemy, serialize_item, serialize_gameinfo, serialize_hazard, serialize_obstacle, serialize_player_stat, own_player_feature_count, player_feature_count, enemy_feature_count, game_info_feature_count, hazard_feature_count, item_feature_count, obstacle_feature_count, stat_feature_count
import threading
import asyncio
from functools import partial
from enum import Enum
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

gym.envs.registration.register(
    id='CustomEnv-v0',
    entry_point='env:CustomEnv',
)

class ActionSpace(Enum):
    # Basic movements
    MOVE_RIGHT = 0
    MOVE_LEFT = 1
    MOVE_UP = 2
    MOVE_DOWN = 3
    MOVE_UP_RIGHT = 4
    MOVE_UP_LEFT = 5
    MOVE_DOWN_RIGHT = 6
    MOVE_DOWN_LEFT = 7
    
    # Dash movements
    DASH_RIGHT = 8
    DASH_LEFT = 9
    DASH_UP = 10
    DASH_DOWN = 11
    DASH_UP_RIGHT = 12
    DASH_UP_LEFT = 13
    DASH_DOWN_RIGHT = 14
    DASH_DOWN_LEFT = 15
    
    # Actions
    ATTACK = 16
    SPECIAL = 17
    SHIELD = 18
    USE_RING = 19
    USE_SPEED_ZAPPER = 20
    USE_BIG_POTION = 21
    REDEEM_SKILL_POINTS_ATTACK = 22
    REDEEM_SKILL_POINTS_HEALTH = 23
    REDEEM_SKILL_POINTS_SPEED = 24


class CustomEnv(gym.Env):
    def __init__(self, max_players=6, max_enemies=40, max_items=60, max_hazards=20, max_obstacles=1500, skip_frames=0):
        super(CustomEnv, self).__init__()
        # Start server in separate thread
        self.server_thread = threading.Thread(target=self.run_server)
        self.server_thread.daemon = True
        self.server_thread.start()
        # Create event loop in main thread
        self.loop = asyncio.get_event_loop()
        if self.loop.is_closed():
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
        
        # Initialize environment
        self.max_players = max_players
        self.max_enemies = max_enemies
        self.max_hazards = max_hazards
        self.max_items = max_items
        self.max_obstacles = max_obstacles

        self.action_space = spaces.Discrete(len(ActionSpace))  # Number of possible moves
        self.observation_space = self.get_flat_observation_space()
        
        self.state = self.initialize_game()
        self.truncated = False
        

    def initialize_game(self):
        """Initialize game state."""
        return LevelData(
            game_info={},
            own_player={},
            items=[],
            enemies=[],
            players=[],
            obstacles=[],
            hazards=[],
            stats=[]
        )

    def run_server(self):
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=3000, log_level="warning")

    def reset(self, seed=None, options=None):
        super().reset(seed=seed, options=options)

        # if self.truncated:
        #     while self.state.own_player.health <= 0:
        #         self.state = self.loop.run_until_complete(get_data(immediate=True))
        # else:
        self.state = self.loop.run_until_complete(reset(seed=seed, options=options))
        
        obs = self.get_observation()
        return obs, {}

    def get_move_coordinates(self, delta: Position):
        # Convert delta to coordinates
        if not self.state or not hasattr(self.state, 'own_player') or not self.state.own_player:
            return delta
        own_player_position = getattr(self.state.own_player, 'position', None)
        if own_player_position is None:
            return delta
        return Position(
            own_player_position.x + delta.x,
            own_player_position.y + delta.y
        )
    
    def get_game_move(self, action: ActionSpace):
        # Convert action enum to game action
        move_delta = 500
        action_map = {
            ActionSpace.MOVE_RIGHT: [{"move_to": self.get_move_coordinates(Position(move_delta, 0))}],
            ActionSpace.MOVE_LEFT: [{"move_to": self.get_move_coordinates(Position(-move_delta, 0))}],
            ActionSpace.MOVE_UP: [{"move_to": self.get_move_coordinates(Position(0, -move_delta))}],
            ActionSpace.MOVE_DOWN: [{"move_to": self.get_move_coordinates(Position(0, move_delta))}],
            ActionSpace.MOVE_UP_RIGHT: [{"move_to": self.get_move_coordinates(Position(move_delta, -move_delta))}],
            ActionSpace.MOVE_UP_LEFT: [{"move_to": self.get_move_coordinates(Position(-move_delta, -move_delta))}],
            ActionSpace.MOVE_DOWN_RIGHT: [{"move_to": self.get_move_coordinates(Position(move_delta, move_delta))}],
            ActionSpace.MOVE_DOWN_LEFT: [{"move_to": self.get_move_coordinates(Position(-move_delta, move_delta))}],
            ActionSpace.DASH_RIGHT: ["dash", {"move_to": self.get_move_coordinates(Position(move_delta, 0))}],
            ActionSpace.DASH_LEFT: ["dash", {"move_to": self.get_move_coordinates(Position(-move_delta, 0))}],
            ActionSpace.DASH_UP: ["dash", {"move_to": self.get_move_coordinates(Position(0, -move_delta))}],
            ActionSpace.DASH_DOWN: ["dash", {"move_to": self.get_move_coordinates(Position(0, move_delta))}],
            ActionSpace.DASH_UP_RIGHT: ["dash", {"move_to": self.get_move_coordinates(Position(move_delta, -move_delta))}],
            ActionSpace.DASH_UP_LEFT: ["dash", {"move_to": self.get_move_coordinates(Position(-move_delta, -move_delta))}],
            ActionSpace.DASH_DOWN_RIGHT: ["dash", {"move_to": self.get_move_coordinates(Position(move_delta, move_delta))}],
            ActionSpace.DASH_DOWN_LEFT: ["dash", {"move_to": self.get_move_coordinates(Position(-move_delta, move_delta))}],
            ActionSpace.ATTACK: ["attack"],
            ActionSpace.SPECIAL: ["special"],
            ActionSpace.SHIELD: ["shield"],
            ActionSpace.USE_RING: [{"use": "ring"}],
            ActionSpace.USE_SPEED_ZAPPER: [{"use": "speed_zapper"}],
            ActionSpace.USE_BIG_POTION: [{"use": "big_potion"}],
            ActionSpace.REDEEM_SKILL_POINTS_ATTACK: [{"redeem_skill_point": "attack"}],
            ActionSpace.REDEEM_SKILL_POINTS_HEALTH: [{"redeem_skill_point": "health"}],
            ActionSpace.REDEEM_SKILL_POINTS_SPEED: [{"redeem_skill_point": "speed"}],
        }
        move = action_map[action]
        move += [{"debug_info": {"message": str(move)}}]
        return move

    def step(self, action_idx: int):
        # convert the action index to a move
        game_action = self.get_game_move(ActionSpace(action_idx))
        # pass the action to the server and get the new state
        new_level_data = self.loop.run_until_complete(step(game_action))
        
        # calculate the reward
        reward = self.get_reward(new_level_data=new_level_data)
        if reward != 0:
            logger.debug(f"reward: {reward}, game_action: {game_action}")
        
        # check if the round is over
        terminated = new_level_data.game_info.state == GameState.ENDED or new_level_data.game_info.state == GameState.MATCH_COMPLETED or new_level_data.own_player.health <= 0
        if terminated:
            logger.debug(f"terminated: {terminated}")
        self.truncated = new_level_data.own_player.health <= 0
        
        info = {}
        
        # set the updated state
        self.state = new_level_data
        obs = self.get_observation()

        return obs, reward, terminated, self.truncated, info
    
    def get_reward(self, new_level_data: LevelData):
        reward = new_level_data.own_player.score - self.state.own_player.score

        # # moved
        # if round(self.state.own_player.position.x) != round(new_level_data.own_player.position.x) or round(self.state.own_player.position.y) != round(new_level_data.own_player.position.y):
        #     reward += 1
        
        # took damage
        if self.state.own_player.health - new_level_data.own_player.health > 0:
            reward -= self.state.own_player.health - new_level_data.own_player.health
        
        # # got zapped
        # if not self.state.own_player.is_zapped and new_level_data.own_player.is_zapped:
        #     reward -= 10
        #
        # # got frozen
        # if not self.state.own_player.is_frozen and new_level_data.own_player.is_frozen:
        #     reward -= 10
        #
        # # died
        # if self.state.own_player.health > 0 and new_level_data.own_player.health <= 0:
        #     reward -= 30

        return reward


    def get_observation(self):
        return self.get_flat_observation()
    
    
    def get_structured_observation_space(self):
        pass
    
    def get_structured_observation(self):
        return spaces.Dict(
            low=-np.inf, 
            high=np.inf, 
            shape=(
                ((self.max_players - 1) * player_feature_count) + 
                (own_player_feature_count) + 
                (self.max_enemies*enemy_feature_count) +
                game_info_feature_count+
                (self.max_hazards * hazard_feature_count) +
                (self.max_items * item_feature_count) +
                (self.max_obstacles * obstacle_feature_count)+
                (self.max_players * stat_feature_count)
                ,
                ), 
            dtype=np.float32)  # Adjust based on selected attributes

    def get_flat_observation_space(self):
        return spaces.Box(
            low=-np.inf, 
            high=np.inf, 
            shape=(
                ((self.max_players - 1) * player_feature_count) + 
                (own_player_feature_count) + 
                (self.max_enemies*enemy_feature_count) +
                game_info_feature_count+
                (self.max_hazards * hazard_feature_count) +
                (self.max_items * item_feature_count) +
                (self.max_obstacles * obstacle_feature_count)+
                (self.max_players * stat_feature_count)
                ,
                ), 
            dtype=np.float32)  # Adjust based on selected attributes
        
    def get_flat_observation(self):
        """Convert game state to a flattened NumPy array."""
        players = self.state.players
        own_player = self.state.own_player
        center_pos = own_player.position
        obs = []

        # Add own player data
        obs.extend(serialize_own_player(own_player))

        for i in range(self.max_players-1):
            if i < len(players):  # Existing player
                player = players[i]
                obs.extend(serialize_player(player, center_pos))
            else:  # Fill empty slots if fewer than max 
                obs.extend([0] * player_feature_count)
        
        for i in range(self.max_enemies):
            if i < len(self.state.enemies):  # Enemies
                enemy = self.state.enemies[i]
                obs.extend(serialize_enemy(enemy, center_pos))
            else:  # Fill empty slots if fewer than max
                obs.extend([0] * enemy_feature_count)
        
        for i in range(self.max_hazards):
            if i < len(self.state.hazards): 
                hazard = self.state.hazards[i]
                obs.extend(serialize_hazard(hazard, center_pos))
            else:  # Fill empty slots if fewer than max
                obs.extend([0] * hazard_feature_count)
        
        for i in range(self.max_items):
            if i < len(self.state.items): 
                item = self.state.items[i]
                obs.extend(serialize_item(item, center_pos))
            else:  # Fill empty slots if fewer than max
                obs.extend([0] * item_feature_count)
        
        for i in range(self.max_obstacles):
            if i < len(self.state.obstacles): 
                obstacle = self.state.obstacles[i]
                obs.extend(serialize_obstacle(obstacle, center_pos))
            else:  # Fill empty slots if fewer than max
                obs.extend([0] * obstacle_feature_count)
        
        for i in range(self.max_players):
            if i < len(self.state.stats): 
                stat = self.state.stats[i]
                obs.extend(serialize_player_stat(stat))
            else:  # Fill empty slots if fewer than max
                obs.extend([0] * stat_feature_count)
        
        obs.extend(serialize_gameinfo(self.state.game_info))
        
        return np.array(obs, dtype=np.float32)

    def render(self, mode='human'):
        # Implement rendering logic if needed
        pass

    def close(self):
        # Implement any cleanup logic if needed
        pass

if __name__ == "__main__":
    env = CustomEnv()
    state, _ = env.reset()
    action = 0  # Example action
    state, reward, terminated, truncated, info = env.step(action)
