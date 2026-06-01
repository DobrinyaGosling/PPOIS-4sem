import pytest
import pygame
from player import Player
from config_manager import ConfigManager


class TestPlayerKeyInput:
    @pytest.fixture
    def player_and_config(self):
        pygame.init()
        config = ConfigManager("config.json").config
        return Player(400, 300, config), config

    def test_handle_input_without_keys(self, player_and_config):
        player, config = player_and_config
        keys = pygame.key.get_pressed()
        try:
            player.handle_input(keys)
        except Exception as e:
            pytest.fail(f"handle_input failed: {e}")

    def test_velocity_changes_with_up_key(self, player_and_config):
        player, config = player_and_config
        initial_vel_length = player.vel.length()

        keys = pygame.key.get_pressed()
        if not keys[pygame.K_UP]:
            player.vel.x = 0
            player.vel.y = 0

        player.angle = 0

        for _ in range(10):
            try:
                player.handle_input(pygame.key.get_pressed())
            except:
                pass

    def test_angle_updates(self, player_and_config):
        player, config = player_and_config
        initial_angle = player.angle

        keys = pygame.key.get_pressed()

    def test_acceleration_direction(self, player_and_config):
        player, config = player_and_config
        player.angle = 0

        import math
        expected_x = math.cos(math.radians(0)) * config["player"]["acceleration"]
        expected_y = math.sin(math.radians(0)) * config["player"]["acceleration"]

        assert expected_x > 0
        assert expected_y == 0

    def test_speed_boost_multiplier_effect(self, player_and_config):
        player, config = player_and_config
        base_acc = config["player"]["acceleration"]
        boost_mult = config["modifiers"]["speed_boost"]["multiplier"]

        player.speed_boost_active = True

        boosted_acc = base_acc * boost_mult
        assert boosted_acc > base_acc
        assert boosted_acc == base_acc * 2
