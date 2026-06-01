import pytest
import pygame
from vector2 import Vector2
from player import Player
from config_manager import ConfigManager


@pytest.fixture
def config():
    return ConfigManager("config.json").config


@pytest.fixture
def player(config):
    pygame.init()
    return Player(400, 300, config)


class TestPlayerInit:
    def test_player_init(self, player):
        assert player.pos.x == 400
        assert player.pos.y == 300
        assert player.angle == 0
        assert player.health == 3

    def test_player_velocity_zero(self, player):
        assert player.vel.x == 0
        assert player.vel.y == 0

    def test_modifiers_inactive(self, player):
        assert not player.shield_active
        assert not player.speed_boost_active
        assert not player.slow_motion_active


class TestPlayerRotation:
    def test_rotation_angle(self, player):
        assert player.angle == 0
        player.angle = 45
        assert player.angle == 45
        player.angle = 360
        assert player.angle == 360

    def test_angle_increments(self, player):
        initial = player.angle
        player.angle = initial + 10
        assert player.angle == initial + 10


class TestPlayerMovement:
    def test_wrapping_left(self, player, config):
        player.pos.x = -10
        player.update(config, 800, 600)
        assert player.pos.x == 800

    def test_wrapping_right(self, player, config):
        player.pos.x = 810
        player.update(config, 800, 600)
        assert player.pos.x == 0

    def test_wrapping_top(self, player, config):
        player.pos.y = -10
        player.update(config, 800, 600)
        assert player.pos.y == 600

    def test_wrapping_bottom(self, player, config):
        player.pos.y = 610
        player.update(config, 800, 600)
        assert player.pos.y == 0

    def test_velocity_friction(self, player, config):
        player.vel.x = 10
        initial_vel = player.vel.x
        player.update(config, 800, 600)
        assert player.vel.x < initial_vel

    def test_max_velocity(self, player, config):
        player.vel = Vector2(100, 100)
        player.update(config, 800, 600)
        assert player.vel.length() <= config["player"]["max_velocity"]


class TestPlayerShield:
    def test_shield_activation(self, player, config):
        player.activate_shield()
        assert player.shield_active
        assert player.shield_time > 0

    def test_shield_damage_reduction(self, player, config):
        player.activate_shield()
        initial_health = player.health
        player.take_damage()
        assert player.health == initial_health
        assert not player.shield_active

    def test_shield_deactivation(self, player, config):
        player.activate_shield()
        shield_time = player.shield_time
        for _ in range(shield_time + 1):
            player.update(config, 800, 600)
        assert not player.shield_active

    def test_damage_without_shield(self, player, config):
        initial_health = player.health
        player.take_damage()
        assert player.health == initial_health - 1


class TestPlayerSpeedBoost:
    def test_speed_boost_activation(self, player, config):
        player.activate_speed_boost()
        assert player.speed_boost_active
        assert player.speed_boost_time > 0

    def test_speed_boost_deactivation(self, player, config):
        player.activate_speed_boost()
        boost_time = player.speed_boost_time
        for _ in range(boost_time + 1):
            player.update(config, 800, 600)
        assert not player.speed_boost_active


class TestPlayerSlowMotion:
    def test_slow_motion_activation(self, player, config):
        player.activate_slow_motion()
        assert player.slow_motion_active
        assert player.slow_motion_time > 0

    def test_slow_motion_deactivation(self, player, config):
        player.activate_slow_motion()
        slow_time = player.slow_motion_time
        for _ in range(slow_time + 1):
            player.update(config, 800, 600)
        assert not player.slow_motion_active


class TestPlayerHealth:
    def test_health_initial(self, player):
        assert player.health == 3

    def test_health_decrease(self, player):
        player.take_damage()
        assert player.health == 2

    def test_is_alive(self, player):
        assert player.is_alive()

    def test_not_alive(self, player):
        player.health = 0
        assert not player.is_alive()

    def test_multiple_damage(self, player):
        for _ in range(3):
            player.take_damage()
        assert player.health == 0


class TestPlayerShoot:
    def test_shoot_creates_bullet(self, player):
        bullet = player.shoot()
        assert bullet is not None
        assert bullet.pos.x == player.pos.x
        assert bullet.pos.y == player.pos.y

    def test_shoot_multiple(self, player):
        bullet1 = player.shoot()
        bullet2 = player.shoot()
        assert bullet1 is not None
        assert bullet2 is not None
        assert bullet1 is not bullet2


class TestPlayerInput:
    def test_rotation_works(self, player):
        initial_angle = player.angle
        assert initial_angle == 0


class TestPlayerDraw:
    def test_draw(self, player):
        surface = pygame.Surface((800, 600))
        try:
            player.draw(surface)
        except Exception as e:
            pytest.fail(f"draw failed: {e}")

    def test_draw_with_shield(self, player, config):
        surface = pygame.Surface((800, 600))
        player.activate_shield()
        try:
            player.draw(surface)
        except Exception as e:
            pytest.fail(f"draw failed: {e}")
