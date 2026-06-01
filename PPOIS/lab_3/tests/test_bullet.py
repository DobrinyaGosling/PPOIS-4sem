import pytest
import pygame
from vector2 import Vector2
from bullet import Bullet
from asteroid import Asteroid
from config_manager import ConfigManager


@pytest.fixture
def config():
    return ConfigManager("config.json").config


@pytest.fixture
def bullet(config):
    pygame.init()
    return Bullet(400, 300, 0, config)


class TestBulletInit:
    def test_bullet_init(self, bullet):
        assert bullet.pos.x == 400
        assert bullet.pos.y == 300
        assert bullet.alive
        assert bullet.lifetime > 0

    def test_bullet_velocity(self, bullet, config):
        speed = config["bullet"]["speed"]
        expected_speed = speed
        assert abs(bullet.vel.length() - expected_speed) < 0.1

    def test_bullet_direction(self, config):
        bullet = Bullet(400, 300, 90, config)
        assert bullet.vel.x < 0.1
        assert bullet.vel.y > 0


class TestBulletUpdate:
    def test_bullet_movement(self, bullet, config):
        initial_x = bullet.pos.x
        bullet.update(config, 800, 600)
        assert bullet.pos.x != initial_x

    def test_bullet_out_of_bounds_left(self, bullet, config):
        bullet.pos.x = -10
        bullet.update(config, 800, 600)
        assert not bullet.alive

    def test_bullet_out_of_bounds_right(self, bullet, config):
        bullet.pos.x = 810
        bullet.update(config, 800, 600)
        assert not bullet.alive

    def test_bullet_out_of_bounds_top(self, bullet, config):
        bullet.pos.y = -10
        bullet.update(config, 800, 600)
        assert not bullet.alive

    def test_bullet_out_of_bounds_bottom(self, bullet, config):
        bullet.pos.y = 610
        bullet.update(config, 800, 600)
        assert not bullet.alive

    def test_bullet_lifetime_decrease(self, bullet, config):
        initial_lifetime = bullet.lifetime
        bullet.update(config, 800, 600)
        assert bullet.lifetime == initial_lifetime - 1

    def test_bullet_death_on_timeout(self, bullet, config):
        bullet.lifetime = 1
        bullet.update(config, 800, 600)
        assert not bullet.alive

    def test_slow_motion_effect(self, bullet, config):
        bullet1 = Bullet(400, 300, 0, config)
        bullet2 = Bullet(400, 300, 0, config)

        bullet1.update(config, 800, 600, slow_motion=False)
        bullet2.update(config, 800, 600, slow_motion=True)

        assert bullet1.pos.x > bullet2.pos.x


class TestBulletCollision:
    def test_collision_with_asteroid(self, bullet, config):
        asteroid = Asteroid(bullet.pos.x, bullet.pos.y, 30, config)
        assert bullet.collides_with(asteroid)

    def test_no_collision_far_asteroid(self, bullet, config):
        asteroid = Asteroid(bullet.pos.x + 100, bullet.pos.y + 100, 30, config)
        assert not bullet.collides_with(asteroid)

    def test_collision_multiple_asteroids(self, bullet, config):
        ast1 = Asteroid(bullet.pos.x, bullet.pos.y, 30, config)
        ast2 = Asteroid(bullet.pos.x + 200, bullet.pos.y + 200, 30, config)

        assert bullet.collides_with(ast1)
        assert not bullet.collides_with(ast2)


class TestBulletAlive:
    def test_is_alive_initial(self, bullet):
        assert bullet.is_alive()

    def test_not_alive_after_timeout(self, bullet, config):
        bullet.lifetime = 0
        bullet.update(config, 800, 600)
        assert not bullet.is_alive()

    def test_not_alive_out_of_bounds(self, bullet, config):
        bullet.pos.x = 1000
        bullet.update(config, 800, 600)
        assert not bullet.is_alive()


class TestBulletDraw:
    def test_draw(self, bullet):
        surface = pygame.Surface((800, 600))
        try:
            bullet.draw(surface)
        except Exception as e:
            pytest.fail(f"draw failed: {e}")

    def test_draw_multiple(self, config):
        pygame.init()
        surface = pygame.Surface((800, 600))
        for i in range(5):
            b = Bullet(100 + i*50, 100, i*45, config)
            try:
                b.draw(surface)
            except Exception as e:
                pytest.fail(f"draw failed: {e}")
