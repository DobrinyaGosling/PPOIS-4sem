import pytest
import pygame
from player import Player
from config_manager import ConfigManager


class TestModifiersShield:
    @pytest.fixture
    def player_with_config(self):
        pygame.init()
        config = ConfigManager("config.json").config
        return Player(400, 300, config), config

    def test_shield_activation_sets_time(self, player_with_config):
        player, config = player_with_config
        player.activate_shield()
        assert player.shield_time == config["modifiers"]["shield"]["duration"]

    def test_shield_protects_once(self, player_with_config):
        player, config = player_with_config
        player.activate_shield()
        assert player.shield_active

        player.take_damage()
        assert not player.shield_active
        assert player.health == 3

    def test_shield_no_protection_after_deactivation(self, player_with_config):
        player, config = player_with_config
        player.activate_shield()
        initial_health = player.health

        for _ in range(config["modifiers"]["shield"]["duration"] + 1):
            player.update(config, 800, 600)

        assert not player.shield_active
        player.take_damage()
        assert player.health == initial_health - 1

    def test_multiple_shield_activations(self, player_with_config):
        player, config = player_with_config
        for _ in range(3):
            player.activate_shield()
            assert player.shield_active
            player.shield_time = 0
            player.update(config, 800, 600)
            assert not player.shield_active


class TestModifiersSpeedBoost:
    @pytest.fixture
    def player_with_config(self):
        pygame.init()
        config = ConfigManager("config.json").config
        return Player(400, 300, config), config

    def test_speed_boost_activation(self, player_with_config):
        player, config = player_with_config
        player.activate_speed_boost()
        assert player.speed_boost_active
        assert player.speed_boost_time == config["modifiers"]["speed_boost"]["duration"]

    def test_speed_boost_deactivates(self, player_with_config):
        player, config = player_with_config
        player.activate_speed_boost()
        boost_duration = player.speed_boost_time

        for _ in range(boost_duration + 1):
            player.update(config, 800, 600)

        assert not player.speed_boost_active

    def test_speed_boost_multiplier(self, player_with_config):
        player, config = player_with_config
        base_acceleration = config["player"]["acceleration"]
        multiplier = config["modifiers"]["speed_boost"]["multiplier"]
        boosted_acceleration = base_acceleration * multiplier

        assert boosted_acceleration > base_acceleration
        assert boosted_acceleration == base_acceleration * 2


class TestModifiersSlowMotion:
    @pytest.fixture
    def player_with_config(self):
        pygame.init()
        config = ConfigManager("config.json").config
        return Player(400, 300, config), config

    def test_slow_motion_activation(self, player_with_config):
        player, config = player_with_config
        player.activate_slow_motion()
        assert player.slow_motion_active
        assert player.slow_motion_time == config["modifiers"]["slow_motion"]["duration"]

    def test_slow_motion_deactivates(self, player_with_config):
        player, config = player_with_config
        player.activate_slow_motion()
        slow_duration = player.slow_motion_time

        for _ in range(slow_duration + 1):
            player.update(config, 800, 600)

        assert not player.slow_motion_active

    def test_slow_motion_factor(self, player_with_config):
        player, config = player_with_config
        slow_factor = config["modifiers"]["slow_motion"]["slow_factor"]
        assert slow_factor < 1
        assert slow_factor > 0

    def test_slow_motion_effect_on_movement(self, player_with_config):
        from bullet import Bullet
        from asteroid import Asteroid

        player, config = player_with_config

        bullet1 = Bullet(400, 300, 0, config)
        bullet2 = Bullet(400, 300, 0, config)

        x1_before = bullet1.pos.x
        x2_before = bullet2.pos.x

        bullet1.update(config, 800, 600, slow_motion=False)
        bullet2.update(config, 800, 600, slow_motion=True)

        x1_after = bullet1.pos.x
        x2_after = bullet2.pos.x

        assert x1_after - x1_before > x2_after - x2_before


class TestModifierCooldowns:
    @pytest.fixture
    def player_with_config(self):
        pygame.init()
        config = ConfigManager("config.json").config
        return Player(400, 300, config), config

    def test_cooldown_values(self, player_with_config):
        player, config = player_with_config

        shield_cooldown = config["modifiers"]["shield"]["cooldown"]
        speed_cooldown = config["modifiers"]["speed_boost"]["cooldown"]
        slow_cooldown = config["modifiers"]["slow_motion"]["cooldown"]

        assert shield_cooldown > 0
        assert speed_cooldown > 0
        assert slow_cooldown > 0

    def test_multiple_activations_respects_cooldown(self, player_with_config):
        player, config = player_with_config

        player.activate_shield()
        assert player.shield_active

        initial_shield_time = player.shield_time

        for _ in range(initial_shield_time + 1):
            player.update(config, 800, 600)

        assert not player.shield_active
        assert player.health == 3
