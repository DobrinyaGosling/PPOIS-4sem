import pytest
import json
from config_manager import ConfigManager
from vector2 import Vector2


class TestConfigIntegrity:
    @pytest.fixture
    def config(self):
        return ConfigManager("config.json").config

    def test_all_required_sections(self, config):
        required = ["window", "player", "bullet", "asteroids", "modifiers"]
        for section in required:
            assert section in config

    def test_window_config_complete(self, config):
        window = config["window"]
        required_keys = ["width", "height", "fps", "title"]
        for key in required_keys:
            assert key in window
            assert window[key] is not None

    def test_player_config_complete(self, config):
        player = config["player"]
        required_keys = ["x", "y", "radius", "rotation_speed", "acceleration", "max_velocity", "friction"]
        for key in required_keys:
            assert key in player

    def test_bullet_config_complete(self, config):
        bullet = config["bullet"]
        required_keys = ["speed", "lifetime", "damage"]
        for key in required_keys:
            assert key in bullet

    def test_asteroid_config_complete(self, config):
        asteroids = config["asteroids"]
        required_sizes = ["large", "medium", "small"]
        for size in required_sizes:
            assert size in asteroids
            assert "size" in asteroids[size]
            assert "health" in asteroids[size]
            assert "speed_range" in asteroids[size]

    def test_modifier_shield_complete(self, config):
        shield = config["modifiers"]["shield"]
        assert "duration" in shield
        assert "cooldown" in shield
        assert shield["duration"] > 0
        assert shield["cooldown"] > shield["duration"]

    def test_modifier_speed_boost_complete(self, config):
        boost = config["modifiers"]["speed_boost"]
        assert "duration" in boost
        assert "cooldown" in boost
        assert "multiplier" in boost
        assert boost["multiplier"] > 1

    def test_modifier_slow_motion_complete(self, config):
        slow = config["modifiers"]["slow_motion"]
        assert "duration" in slow
        assert "cooldown" in slow
        assert "slow_factor" in slow
        assert 0 < slow["slow_factor"] < 1


class TestVectorMath:
    def test_vector_add_commutative(self):
        v1 = Vector2(3, 4)
        v2 = Vector2(1, 2)

        result1 = v1 + v2
        result2 = v2 + v1

        assert result1.x == result2.x
        assert result1.y == result2.y

    def test_vector_scale_consistency(self):
        v = Vector2(2, 3)
        scaled1 = v * 5
        scaled2 = 5 * v

        assert scaled1.x == scaled2.x
        assert scaled1.y == scaled2.y

    def test_distance_symmetry(self):
        v1 = Vector2(1, 2)
        v2 = Vector2(4, 6)

        dist1 = v1.distance_to(v2)
        dist2 = v2.distance_to(v1)

        assert dist1 == dist2

    def test_normalized_vector_length(self):
        v = Vector2(3, 4)
        normalized = v.normalize()

        length = normalized.length()
        assert abs(length - 1.0) < 1e-6

    def test_zero_vector_normalize(self):
        v = Vector2(0, 0)
        normalized = v.normalize()

        assert normalized.x == 0
        assert normalized.y == 0


class TestGameBalance:
    @pytest.fixture
    def config(self):
        return ConfigManager("config.json").config

    def test_bullet_faster_than_asteroid(self, config):
        bullet_speed = config["bullet"]["speed"]
        asteroid_speeds = []

        for size in ["large", "medium", "small"]:
            speed_range = config["asteroids"][size]["speed_range"]
            asteroid_speeds.append(max(speed_range))

        max_asteroid_speed = max(asteroid_speeds)
        assert bullet_speed > max_asteroid_speed

    def test_player_max_velocity_reasonable(self, config):
        max_vel = config["player"]["max_velocity"]
        bullet_speed = config["bullet"]["speed"]

        assert max_vel > 0
        assert bullet_speed > 0

    def test_modifier_duration_less_than_cooldown(self, config):
        for modifier_name in ["shield", "speed_boost", "slow_motion"]:
            modifier = config["modifiers"][modifier_name]
            assert modifier["duration"] < modifier["cooldown"]

    def test_asteroid_health_matches_size(self, config):
        asteroids = config["asteroids"]

        large_health = asteroids["large"]["health"]
        medium_health = asteroids["medium"]["health"]
        small_health = asteroids["small"]["health"]

        assert large_health > medium_health > small_health
