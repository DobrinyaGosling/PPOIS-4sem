import pytest
import json
import os
from vector2 import Vector2
from player import Player
from bullet import Bullet
from asteroid import Asteroid
from config_manager import ConfigManager
import pygame


class TestIntegration:
    @pytest.fixture
    def config(self):
        return ConfigManager("config.json").config

    def test_player_bullet_creation(self, config):
        pygame.init()
        player = Player(400, 300, config)
        bullet = player.shoot()
        assert bullet is not None
        assert isinstance(bullet, Bullet)

    def test_bullet_asteroid_collision(self, config):
        pygame.init()
        bullet = Bullet(100, 100, 0, config)
        asteroid = Asteroid(100, 100, 30, config)

        assert bullet.collides_with(asteroid)

    def test_asteroid_damage_chain(self, config):
        pygame.init()
        asteroid = Asteroid(400, 300, 30, config)

        initial_health = asteroid.health
        destroyed = asteroid.take_damage()

        assert asteroid.health == initial_health - 1
        assert not destroyed

        for _ in range(asteroid.health):
            destroyed = asteroid.take_damage()

        assert destroyed
        assert not asteroid.is_alive()

    def test_player_damage_chain(self, config):
        pygame.init()
        player = Player(400, 300, config)

        initial_health = player.health

        for i in range(initial_health):
            player.take_damage()
            assert player.health == initial_health - i - 1

        assert not player.is_alive()

    def test_shield_protection(self, config):
        pygame.init()
        player = Player(400, 300, config)

        player.activate_shield()
        assert player.shield_active

        player.take_damage()
        assert not player.shield_active
        assert player.health == 3

    def test_speed_boost_duration(self, config):
        pygame.init()
        player = Player(400, 300, config)

        player.activate_speed_boost()
        boost_time = player.speed_boost_time

        for _ in range(boost_time):
            player.update(config, 800, 600)
            if player.speed_boost_active:
                assert player.speed_boost_time >= 0

        player.update(config, 800, 600)
        assert not player.speed_boost_active

    def test_slow_motion_effect(self, config):
        pygame.init()
        player = Player(400, 300, config)
        bullet = Bullet(400, 300, 0, config)
        asteroid = Asteroid(400, 300, 30, config)

        player.activate_slow_motion()
        assert player.slow_motion_active

        for _ in range(10):
            bullet.update(config, 800, 600, slow_motion=True)
            asteroid.update(config, 800, 600, slow_motion=True)

        assert bullet.is_alive()

    def test_config_consistency(self):
        config = ConfigManager("config.json").config

        window = config["window"]
        player = config["player"]
        bullet = config["bullet"]
        asteroids = config["asteroids"]
        modifiers = config["modifiers"]

        assert window["width"] > 0
        assert window["height"] > 0
        assert player["acceleration"] > 0
        assert bullet["speed"] > 0
        assert len(modifiers) >= 3

    def test_highscores_persistence(self):
        test_file = "test_scores.json"

        scores = [
            {"name": "Player1", "score": 1000},
            {"name": "Player2", "score": 500}
        ]

        with open(test_file, "w") as f:
            json.dump(scores, f)

        with open(test_file, "r") as f:
            loaded = json.load(f)

        assert len(loaded) == 2
        assert loaded[0]["score"] == 1000

        os.unlink(test_file)

    def test_vector_operations_in_game(self):
        v1 = Vector2(100, 100)
        v2 = Vector2(50, 50)

        result = v1 + v2
        assert result.x == 150
        assert result.y == 150

        scaled = v1 * 2
        assert scaled.x == 200
        assert scaled.y == 200

        distance = v1.distance_to(v2)
        assert distance > 0

    def test_asteroid_splitting(self, config):
        pygame.init()
        large_asteroid = Asteroid(400, 300, 30, config)

        assert large_asteroid._get_size_name() == "large"

        medium_asteroid = Asteroid(400, 300, 15, config)
        assert medium_asteroid._get_size_name() == "medium"

        small_asteroid = Asteroid(400, 300, 8, config)
        assert small_asteroid._get_size_name() == "small"
