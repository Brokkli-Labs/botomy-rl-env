from dataclasses import dataclass, asdict, is_dataclass
from typing import List, Literal, TypeAlias, Union, Any, Dict
import json
from enum import Enum

# Enums and Type Aliases
class GameState(str, Enum):
    WAITING = "WAITING"
    STARTING = "STARTING"
    STARTED = "STARTED"
    ENDING = "ENDING"
    ENDED = "ENDED"
    MATCH_COMPLETED = "MATCH_COMPLETED"

ALL_ENEMIES = Literal["wolf", "ghoul", "minotaur", "tiny"]
PlayerType = Literal["player"]
ItemType = Literal["big_potion", "ring", "speed_zapper", "chest", "coin", "power_up"]
PowerUpType = Literal["freeze", "bomb", "shockwave"]
HazardType = Literal["bomb", "icicle", "lightning_storm"]
Direction = Literal["right", "left"]
HazardStatus = Literal["idle", "active", "charging"]

GameObjectType: TypeAlias = Union[PlayerType, ALL_ENEMIES, ItemType, HazardType]

@dataclass
class Position:
    x: float
    y: float
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Position':
        return cls(x=data['x'], y=data['y'])
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class GameObject:
    id: str
    position: Position
    type: GameObjectType

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GameObject':
        return cls(
            id=data.get('id', ''),  # Use get to handle missing keys
            position=Position.from_dict(data.get('position', {'x': 0, 'y': 0})),  # Default position if missing
            type=data.get('type', 'player')  # Default type if missing
        )

@dataclass
class Item(GameObject):
    value: int
    points: int

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Item':
        return cls(
            id=data['id'],
            position=Position.from_dict(data['position']),
            type=data['type'],
            value=data.get('value', 0),  # Use get to handle missing keys
            points=data.get('points', 0)  # Use get to handle missing keys
        )

@dataclass
class Character(GameObject):
    attack_damage: int
    direction: Direction
    health: int
    is_attacking: bool
    is_frozen: bool
    is_pushed: bool
    is_zapped: bool
    points: int

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Character':
        return cls(
            id=data['id'],
            position=Position.from_dict(data['position']),
            type=data['type'],
            attack_damage=data['attack_damage'],
            direction=data['direction'],
            health=data['health'],
            is_attacking=data['is_attacking'],
            is_frozen=data['is_frozen'],
            is_pushed=data['is_pushed'],
            is_zapped=data['is_zapped'],
            points=data['points']
        )

@dataclass
class Enemy(Character):
    max_health: int

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Enemy':
        return cls(
            id=data['id'],
            position=Position.from_dict(data['position']),
            type=data['type'],
            attack_damage=data['attack_damage'],
            direction=data['direction'],
            health=data['health'],
            is_attacking=data['is_attacking'],
            is_frozen=data['is_frozen'],
            is_pushed=data['is_pushed'],
            is_zapped=data['is_zapped'],
            points=data['points'],
            max_health=data.get('max_health', 0)  # Use get to handle missing keys
        )

@dataclass
class Collision:
    type: str
    relative_position: Position

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Collision':
        return cls(
            type=data['type'],
            relative_position=Position.from_dict(data['relative_position'])
        )

@dataclass
class Levelling:
    level: int
    available_skill_points: int = 0
    attack: int = 0
    speed: int = 0
    health: int = 0

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Levelling':
        return cls(
            level=data['level'],
            available_skill_points=data.get('available_skill_points', 0),
            attack=data.get('attack', 0),
            speed=data.get('speed', 0),
            health=data.get('health', 0)
        )

@dataclass
class ItemInventory:
    big_potions: List[dict]
    speed_zappers: List[dict]
    rings: List[dict]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ItemInventory':
        return cls(
            big_potions=data['big_potions'],
            speed_zappers=data['speed_zappers'],
            rings=data['rings']
        )

@dataclass
class Player(Character):
    display_name: str
    is_dashing: bool
    levelling: Levelling
    score: int
    shield_raised: bool
    special_equipped: str
    speech: str
    unleashing_shockwave: bool
    is_overclocking: bool
    has_health_regen: bool
    base_speed: float

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Player':
        return cls(
            id=data['id'],
            position=Position.from_dict(data['position']),
            type=data['type'],
            attack_damage=data['attack_damage'],
            direction=data['direction'],
            health=data['health'],
            is_attacking=data['is_attacking'],
            is_frozen=data['is_frozen'],
            is_pushed=data['is_pushed'],
            is_zapped=data['is_zapped'],
            points=data['points'],
            display_name=data['display_name'],
            is_dashing=data['is_dashing'],
            levelling=Levelling.from_dict(data['levelling']),
            score=data['score'],
            shield_raised=data['shield_raised'],
            special_equipped=data['special_equipped'],
            speech=data['speech'],
            unleashing_shockwave=data['unleashing_shockwave'],
            is_overclocking=data['is_overclocking'],
            has_health_regen=data['has_health_regen'],
            base_speed=data['base_speed']
        )

@dataclass
class OwnPlayer(Player):
    collisions: List[Collision]
    items: ItemInventory
    is_cloaked: bool
    is_colliding: bool
    is_dash_ready: bool
    is_shield_ready: bool
    is_special_ready: bool
    is_zap_ready: bool
    max_health: int
    overclock_duration: int

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'OwnPlayer':
        return cls(
            id=data['id'],
            position=Position.from_dict(data['position']),
            type=data['type'],
            attack_damage=data['attack_damage'],
            direction=data['direction'],
            health=data['health'],
            is_attacking=data['is_attacking'],
            is_frozen=data['is_frozen'],
            is_pushed=data['is_pushed'],
            is_zapped=data['is_zapped'],
            points=data['points'],
            display_name=data['display_name'],
            is_dashing=data['is_dashing'],
            levelling=Levelling.from_dict(data['levelling']),
            score=data['score'],
            shield_raised=data['shield_raised'],
            special_equipped=data['special_equipped'],
            speech=data['speech'],
            unleashing_shockwave=data['unleashing_shockwave'],
            is_overclocking=data['is_overclocking'],
            has_health_regen=data['has_health_regen'],
            base_speed=data['base_speed'],
            collisions=[Collision.from_dict(c) for c in data['collisions']],
            items=ItemInventory.from_dict(data['items']),
            is_cloaked=data['is_cloaked'],
            is_colliding=data['is_colliding'],
            is_dash_ready=data['is_dash_ready'],
            is_shield_ready=data['is_shield_ready'],
            is_special_ready=data['is_special_ready'],
            is_zap_ready=data['is_zap_ready'],
            max_health=data['max_health'],
            overclock_duration=data['overclock_duration']
        )

@dataclass
class Hazard(GameObject):
    status: HazardStatus
    attack_damage: int
    owner_id: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Hazard':
        return cls(
            id=data['id'],
            position=Position.from_dict(data['position']),
            type=data['type'],
            status=data['status'],
            attack_damage=data['attack_damage'],
            owner_id=data['owner_id']
        )

@dataclass
class GameInfo:
    friendly_fire: bool
    game_type: str
    map: str
    match_id: str
    state: GameState
    time_remaining_s: int
    latency: int

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GameInfo':
        return cls(
            friendly_fire=data['friendly_fire'],
            game_type=data['game_type'],
            map=data['map'],
            match_id=data['match_id'],
            state=GameState(data['state']),
            time_remaining_s=data['time_remaining_s'],
            latency=data['latency']
        )

@dataclass
class PlayerStat:
    id: str
    score: int
    kills: int
    deaths: int
    coins: int
    kd_ratio: float
    kill_streak: int
    overclocks: int
    xps: int
    wolf_kills: int
    ghoul_kills: int
    tiny_kills: int
    minotaur_kills: int
    player_kills: int
    self_destructs: int

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PlayerStat':
        return cls(
            id=data['id'],
            score=data['score'],
            kills=data['kills'],
            deaths=data['deaths'],
            coins=data['coins'],
            kd_ratio=data['kd_ratio'],
            kill_streak=data['kill_streak'],
            overclocks=data['overclocks'],
            xps=data['xps'],
            wolf_kills=data['wolf_kills'],
            ghoul_kills=data['ghoul_kills'],
            tiny_kills=data['tiny_kills'],
            minotaur_kills=data['minotaur_kills'],
            player_kills=data['player_kills'],
            self_destructs=data['self_destructs']
        )

@dataclass
class LevelData:
    game_info: GameInfo
    own_player: OwnPlayer
    items: List[Item]
    enemies: List[Enemy]
    players: List[Player]
    obstacles: List[Position]
    hazards: List[Hazard]
    stats: List[PlayerStat]
    
    @classmethod
    def from_json(cls, json_str: str) -> 'LevelData':
        data = json.loads(json_str)
        return cls.from_dict(data)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LevelData':
        return cls(
            game_info=GameInfo.from_dict(data['game_info']),
            own_player=OwnPlayer.from_dict(data['own_player']),
            items=[Item.from_dict(item) for item in data['items']],
            enemies=[Enemy.from_dict(enemy) for enemy in data['enemies']],
            players=[Player.from_dict(player) for player in data['players']],
            obstacles=[Position.from_dict(obstacle) for obstacle in data['obstacles']],
            hazards=[Hazard.from_dict(hazard) for hazard in data['hazards']],
            stats=[PlayerStat.from_dict(stat) for stat in data['stats']]
        )
    
    def to_dict(self) -> Dict[str, Any]:
        def convert(obj: Any) -> Any:
            if is_dataclass(obj):
                return {k: convert(v) for k, v in asdict(obj).items()}
            elif isinstance(obj, list):
                return [convert(item) for item in obj]
            elif isinstance(obj, Enum):
                return obj.value
            return obj
            
        return convert(self)

@dataclass
class DebugInfo:
    target_id: str
    message: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DebugInfo':
        return cls(
            target_id=data['target_id'],
            message=data['message']
        )

MoveType = Union[
    Literal["attack"],
    Literal["special"],
    Literal["dash"],
    Literal["shield"],
    Dict[Literal["move_to"], Position], 
    Dict[Literal["speak"], str], 
    Dict[Literal["use"], Literal["ring", "speed_zapper", "big_potion"]], 
    Dict[Literal["redeem_skill_point"], Literal["attack", "health", "speed"]], 
    Dict[Literal["debug_info"], DebugInfo]
]

@dataclass
class Move:
    move: MoveType
