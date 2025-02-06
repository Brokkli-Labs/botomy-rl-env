import base64
from models import Player, OwnPlayer, Enemy, GameInfo, Collision, Hazard, Item, Position, PlayerStat

player_feature_count = 20
def serialize_player(player: Player):
    """Convert player data to a flattened NumPy array."""
    special_equipped_mapping = {
        "": 0,
        "bomb": 1,
        "shockwave": 2,
        "freeze": 3,
    }
    return [
        string_to_int(player.id),
        # player.display_name,
        # player.speech,
        player.position.x,
        player.position.y,
        player.health,
        player.base_speed,
        player.attack_damage,
        int(player.shield_raised),
        1 if player.direction == "right" else 0,  # Encode direction
        int(player.is_attacking),
        player.score,
        player.levelling.level,
        int(player.is_dashing),
        int(player.is_frozen),
        int(player.is_pushed),
        int(player.is_zapped),
        int(player.is_overclocking),
        int(player.has_health_regen),
        player.points,
        special_equipped_mapping.get(player.special_equipped, 0),
        int(player.unleashing_shockwave)
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
        collision.relative_position.x,
        collision.relative_position.y,
        type_mapping.get(collision.type,0),
    ]

max_collisions=20
own_player_feature_count = player_feature_count + 15 + max_collisions*collision_feature_count
def serialize_own_player(own_player: OwnPlayer):
    if own_player is None:
        return [0] * own_player_feature_count
    """Convert own player data to a flattened NumPy array."""
    serialized_player = serialize_player(own_player)
    serialized_collisions = []

    for i in range(max_collisions):
        if i < len(own_player.collisions): 
            collision = own_player.collisions[i]
            serialized_collisions.extend(serialize_collision(collision))
        else:  # Fill empty slots if fewer than max
            serialized_collisions.extend([0] * collision_feature_count)
    
    return serialized_player + [
        int(own_player.is_cloaked),
        int(own_player.is_colliding),
        int(own_player.is_dash_ready),
        int(own_player.is_shield_ready),
        int(own_player.is_special_ready),
        int(own_player.is_zap_ready),
        own_player.max_health,
        own_player.overclock_duration,
        len(own_player.items.big_potions),
        len(own_player.items.speed_zappers),
        len(own_player.items.rings),
        own_player.levelling.available_skill_points,
        own_player.levelling.attack,
        own_player.levelling.health,
        own_player.levelling.speed,
    ] + serialized_collisions

enemy_feature_count=11
def serialize_enemy(enemy: Enemy):
    enemy_type_mapping = {
        "wolf": 0,
        "ghoul": 1,
        "minotaur": 2,
        "tiny": 3,
    }
    """Convert enemy data to a flattened NumPy array."""
    return [
        # enemy.id,
        enemy.position.x,
        enemy.position.y,
        enemy.health,
        enemy.attack_damage,
        1 if enemy.direction == "right" else 0,  # Encode direction
        int(enemy.is_attacking),
        int(enemy.is_frozen),
        int(enemy.is_pushed),
        int(enemy.is_zapped),
        enemy.points,
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
        gameinfo.time_remaining_s,
        gameinfo.latency,
        int(gameinfo.friendly_fire),
        1 if gameinfo.game_type == "rpg" else 0
    ]

hazard_feature_count=5
def serialize_hazard(hazard: Hazard):
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
        hazard.position.x,
        hazard.position.y,
        hazard_type_mapping.get(hazard.type, -1),
        hazard.attack_damage,
        status_mapping.get(hazard.status, 0),
    ]

def string_to_int(s):
    encoded = base64.b64encode(s.encode()).hex()
    return int(encoded, 16)

item_feature_count=6
def serialize_item(item: Item):
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
        item.position.x,
        item.position.y,
        item_type_mapping.get(item.type, -1),
        item.points,
        item.value,
        power_mapping.get(item.power, -1),
    ]

obstacle_feature_count=2
def serialize_obstacle(obstacle: Position):
    return [
        obstacle.x,
        obstacle.y,
    ]

stat_feature_count=13
def serialize_player_stat(stat: PlayerStat):
    return [
        string_to_int(stat.id),
        stat.score,
        stat.kills,
        stat.deaths,
        stat.coins,
        stat.kd_ratio,
        stat.kill_streak,
        stat.overclocks,
        stat.wolf_kills,
        stat.ghoul_kills,
        stat.minotaur_kills,
        stat.tiny_kills,
        stat.player_kills,
    ]