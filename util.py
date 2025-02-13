import base64
from models import Player, OwnPlayer, Enemy, GameInfo, Collision, Hazard, Item, Position, PlayerStat

MAX_HEALTH=1000
MAX_SCORE=500000
MAX_SPEED=15000
MAX_DAMAGE=9001
MAX_KILLS=10000
MAX_LEVELS=30

POSITION_FACTOR=100

def serialize_position_x(position: Position, center: Position):
  return (position.x - center.x) / POSITION_FACTOR
def serialize_position_y(position: Position, center: Position):
  return (position.y - center.y) / POSITION_FACTOR

player_feature_count = 7
def serialize_player(player: Player, center_pos: Position):
    """Convert player data to a flattened NumPy array."""
    special_equipped_mapping = {
        "": 0,
        "bomb": 1,
        "shockwave": 2,
        "freeze": 3,
    }
    return [
        # string_to_int(player.id),
        # player.display_name,
        # player.speech,
        serialize_position_x(player.position, center_pos),
        serialize_position_y(player.position, center_pos),
        player.health / MAX_HEALTH,
        player.max_health / MAX_HEALTH,
        # player.base_speed / MAX_SPEED,
        # player.attack_damage / MAX_DAMAGE,
        int(player.shield_raised),
        1 if player.direction == "right" else 0,  # Encode direction
        int(player.is_attacking),
        # player.score / MAX_SCORE,
        # player.levelling.level / MAX_LEVELS,
        # int(player.is_dashing),
        # int(player.is_frozen),
        # int(player.is_pushed),
        # int(player.is_zapped),
        # int(player.is_overclocking),
        # int(player.has_health_regen),
        # player.points / MAX_SCORE,
        # special_equipped_mapping.get(player.special_equipped, 0),
        # int(player.unleashing_shockwave)
    ]

collision_feature_count=3
def serialize_collision(collision: Collision):
    type_mapping = {
        "obstacle": 0,
        "player": 1,
        "wolf": 2,
        "ghoul": 3,
        "minotaur": 4,
        "tiny": 5,
        "bomb": 6,
        "icicle": 7,
        "chest": 8,
    }
    return [
        collision.relative_position.x / POSITION_FACTOR,
        collision.relative_position.y / POSITION_FACTOR,
        type_mapping.get(collision.type,0),
    ]

max_collisions=20
own_player_feature_count = player_feature_count + 0 + max_collisions*collision_feature_count
def serialize_own_player(own_player: OwnPlayer):
    if own_player is None:
        return [0] * own_player_feature_count
    """Convert own player data to a flattened NumPy array."""
    serialized_player = serialize_player(own_player, own_player.position)
    serialized_collisions = []

    for i in range(max_collisions):
        if i < len(own_player.collisions): 
            collision = own_player.collisions[i]
            serialized_collisions.extend(serialize_collision(collision))
        else:  # Fill empty slots if fewer than max
            serialized_collisions.extend([0] * collision_feature_count)
    
    return serialized_player + [
        # int(own_player.is_cloaked),
        # int(own_player.is_colliding),
        # int(own_player.is_dash_ready),
        # int(own_player.is_shield_ready),
        # int(own_player.is_special_ready),
        # int(own_player.is_zap_ready),
        # own_player.overclock_duration,
        # len(own_player.items.big_potions),
        # len(own_player.items.speed_zappers),
        # len(own_player.items.rings),
        # own_player.levelling.available_skill_points,
        # own_player.levelling.attack,
        # own_player.levelling.health,
        # own_player.levelling.speed,
    ] + serialized_collisions

enemy_feature_count=7
def serialize_enemy(enemy: Enemy, center_pos: Position):
    enemy_type_mapping = {
        "wolf": 0,
        "ghoul": 1,
        "minotaur": 2,
        "tiny": 3,
    }
    """Convert enemy data to a flattened NumPy array."""
    return [
        # enemy.id,
        serialize_position_x(enemy.position, center_pos),
        serialize_position_y(enemy.position, center_pos),
        enemy.health / MAX_HEALTH,
        enemy.max_health / MAX_HEALTH,
        # enemy.attack_damage / MAX_DAMAGE,
        1 if enemy.direction == "right" else 0,  # Encode direction
        int(enemy.is_attacking),
        # int(enemy.is_frozen),
        # int(enemy.is_pushed),
        # int(enemy.is_zapped),
        # enemy.points / MAX_SCORE,
        enemy_type_mapping.get(enemy.type, 0)
    ]

game_info_feature_count=6
def serialize_gameinfo(gameinfo: GameInfo):
    game_state_mapping = {
        "WAITING": 0,
        "STARTING": 1,
        "STARTED": 3,
        "ENDING": 4,
        "ENDED": 5,
        "MATCH_COMPLETED": 6,
    }
    """Convert gameinfo data to a flattened NumPy array."""
    return [
        game_state_mapping.get(gameinfo.state, 0),
        string_to_int(gameinfo.map),
        gameinfo.time_remaining_s / 60,
        gameinfo.latency,
        int(gameinfo.friendly_fire),
        1 if gameinfo.game_type == "rpg" else 0
    ]

hazard_feature_count=4
def serialize_hazard(hazard: Hazard, center_pos: Position):
    """Convert hazard data to a flattened NumPy array."""
    hazard_type_mapping = {
        "bomb": 0,
        "icicle": 1,
        "speed_zapper": 2,
    }
    status_mapping = {
        "idle": 0,
        "charging": 1,
        "active": 2,
    }
    return [
        # hazard.id,
        serialize_position_x(hazard.position, center_pos),
        serialize_position_y(hazard.position, center_pos),
        hazard_type_mapping.get(hazard.type, -1),
        # hazard.attack_damage / MAX_DAMAGE,
        status_mapping.get(hazard.status, 0),
    ]

def string_to_int(s):
    encoded = base64.b64encode(s.encode()).hex()
    return int(encoded, 16)

item_feature_count=5
def serialize_item(item: Item, center_pos: Position):
    """Convert item data to a flattened NumPy array."""
    item_type_mapping = {
        "big_potion": 0,
        "speed_zapper": 1,
        "ring": 2,
        "chest": 3,
        "coin": 4,
        "power_up": 5,
    }
    power_mapping = {
        "bomb": 0,
        "shockwave": 0,
        "freeze": 0,
    }
    return [
        # item.id,
        serialize_position_x(item.position, center_pos),
        serialize_position_y(item.position, center_pos),
        item_type_mapping.get(item.type, -1),
        item.points / MAX_SCORE,
        item.value,
        # power_mapping.get(item.power, -1),
    ]

obstacle_feature_count=2
def serialize_obstacle(obstacle: Position, center_pos: Position):
    return [
        serialize_position_x(obstacle, center_pos),
        serialize_position_y(obstacle, center_pos),
    ]

stat_feature_count=10
def serialize_player_stat(stat: PlayerStat):
    return [
        # string_to_int(stat.id),
        # stat.score / MAX_SCORE,
        # stat.kills / MAX_KILLS,
        # stat.deaths / MAX_KILLS,
        # stat.xps,
        # stat.coins / MAX_KILLS,
        # stat.kd_ratio,
        # stat.kill_streak,
        # stat.overclocks,
        # stat.wolf_kills / MAX_KILLS,
        # stat.ghoul_kills / MAX_KILLS,
        # stat.minotaur_kills / MAX_KILLS,
        # stat.tiny_kills / MAX_KILLS,
        # stat.player_kills / MAX_KILLS,
    ]
