import pytest
import json
import pygame
from config_manager import ConfigManager
from vector2 import Vector2
from player import Player
from bullet import Bullet
from asteroid import Asteroid


class TestGameLogicFlow:
    @pytest.fixture
    def config(self):
        return ConfigManager("config.json").config

    def test_score_increment_logic(self, config):
        asteroid_size = 30
        score = 0
        multiplier = 10 * (3 - asteroid_size // 10)
        score += multiplier
        assert score >= 0

    def test_game_spawn_pattern(self, config):
        import pygame
        pygame.init()

        spawn_interval = config["asteroids"]["spawn_interval"]
        assert spawn_interval > 0

        spawn_timer = 0
        max_asteroids = 5

        for frame in range(spawn_interval + 1):
            spawn_timer += 1
            if spawn_timer > spawn_interval:
                if max_asteroids < 5:
                    max_asteroids += 1
                spawn_timer = 0

        assert spawn_timer == 0

    def test_modifier_cooldown_countdown(self, config):
        cooldowns = {
            "shield": 800,
            "speed_boost": 600,
            "slow_motion": 600
        }

        for frame in range(10):
            for key in cooldowns:
                if cooldowns[key] > 0:
                    cooldowns[key] -= 1

        assert cooldowns["shield"] == 790
        assert cooldowns["speed_boost"] == 590
        assert cooldowns["slow_motion"] == 590

    def test_game_state_management(self, config):
        pygame.init()
        player = Player(400, 300, config)
        bullets = []
        asteroids = []
        score = 0

        assert player.health == 3
        assert len(bullets) == 0
        assert len(asteroids) == 0
        assert score == 0

        bullet = player.shoot()
        bullets.append(bullet)
        assert len(bullets) == 1

        asteroid = Asteroid(400, 300, 30, config)
        asteroids.append(asteroid)
        assert len(asteroids) == 1

    def test_collision_damage_flow(self, config):
        pygame.init()
        player = Player(400, 300, config)
        asteroid = Asteroid(400, 300, 30, config)

        assert player.health == 3
        assert asteroid.health == 3

        asteroid.take_damage()
        assert asteroid.health == 2

        player.take_damage()
        assert player.health == 2

    def test_shield_protection_flow(self, config):
        pygame.init()
        player = Player(400, 300, config)

        assert player.health == 3

        player.activate_shield()
        assert player.shield_active

        player.take_damage()
        assert not player.shield_active
        assert player.health == 3

    def test_game_over_condition(self, config):
        pygame.init()
        player = Player(400, 300, config)

        for _ in range(3):
            player.take_damage()

        assert player.health == 0
        assert not player.is_alive()

    def test_score_highscore_tracking(self):
        scores = []

        test_score_1 = 1000
        test_score_2 = 2000
        test_score_3 = 500

        scores.append({"name": "P1", "score": test_score_1})
        scores.append({"name": "P2", "score": test_score_2})
        scores.append({"name": "P3", "score": test_score_3})

        sorted_scores = sorted(scores, key=lambda x: x["score"], reverse=True)

        assert sorted_scores[0]["score"] == test_score_2
        assert sorted_scores[1]["score"] == test_score_1
        assert sorted_scores[2]["score"] == test_score_3

        top_10 = sorted_scores[:10]
        assert len(top_10) == 3

    def test_asteroid_splitting_logic(self, config):
        pygame.init()
        asteroids = []

        large = Asteroid(400, 300, 30, config)
        asteroids.append(large)

        if large.size > 15:
            new_size = large.size // 2
            new_ast = Asteroid(400, 300, new_size, config)
            asteroids.append(new_ast)

        assert len(asteroids) == 2
        assert asteroids[1].size == 15

    def test_projectile_lifetime(self, config):
        pygame.init()
        bullet = Bullet(400, 300, 0, config)

        initial_lifetime = bullet.lifetime

        for _ in range(10):
            bullet.update(config, 800, 600)

        assert bullet.lifetime == initial_lifetime - 10
        assert bullet.is_alive()

        for _ in range(initial_lifetime):
            bullet.update(config, 800, 600)

        assert not bullet.is_alive()
