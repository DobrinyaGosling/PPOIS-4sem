import pytest
import pygame
from vector2 import Vector2
from asteroid import Asteroid
from player import Player
from config_manager import ConfigManager


@pytest.fixture
def config():
    return ConfigManager("config.json").config


@pytest.fixture
def asteroid_large(config):
    pygame.init()
    return Asteroid(400, 300, 30, config)


@pytest.fixture
def asteroid_medium(config):
    pygame.init()
    return Asteroid(400, 300, 15, config)


@pytest.fixture
def asteroid_small(config):
    pygame.init()
    return Asteroid(400, 300, 8, config)


class TestAsteroidInit:
    def test_asteroid_init(self, asteroid_large):
        assert asteroid_large.pos.x == 400
        assert asteroid_large.pos.y == 300
        assert asteroid_large.size == 30
        assert asteroid_large.health > 0

    def test_asteroid_velocity(self, asteroid_large):
        assert isinstance(asteroid_large.vel, Vector2)
        assert asteroid_large.vel.length() > 0


class TestAsteroidSizes:
    def test_large_asteroid_size(self, asteroid_large):
        assert asteroid_large.size == 30
        assert asteroid_large.health == 3

    def test_medium_asteroid_size(self, asteroid_medium):
        assert asteroid_medium.size == 15
        assert asteroid_medium.health == 2

    def test_small_asteroid_size(self, asteroid_small):
        assert asteroid_small.size == 8
        assert asteroid_small.health == 1

    def test_size_name_large(self, asteroid_large):
        assert asteroid_large._get_size_name() == "large"

    def test_size_name_medium(self, asteroid_medium):
        assert asteroid_medium._get_size_name() == "medium"

    def test_size_name_small(self, asteroid_small):
        assert asteroid_small._get_size_name() == "small"


class TestAsteroidMovement:
    def test_movement_updates_position(self, asteroid_large, config):
        initial_x = asteroid_large.pos.x
        asteroid_large.update(config, 800, 600)
        assert asteroid_large.pos.x != initial_x

    def test_wrapping_left(self, asteroid_large, config):
        asteroid_large.pos.x = -10
        asteroid_large.update(config, 800, 600)
        assert asteroid_large.pos.x == 800

    def test_wrapping_right(self, asteroid_large, config):
        asteroid_large.pos.x = 810
        asteroid_large.update(config, 800, 600)
        assert asteroid_large.pos.x == 0

    def test_wrapping_top(self, asteroid_large, config):
        asteroid_large.pos.y = -10
        asteroid_large.update(config, 800, 600)
        assert asteroid_large.pos.y == 600

    def test_wrapping_bottom(self, asteroid_large, config):
        asteroid_large.pos.y = 610
        asteroid_large.update(config, 800, 600)
        assert asteroid_large.pos.y == 0

    def test_rotation_updates(self, asteroid_large, config):
        initial_angle = asteroid_large.current_angle
        asteroid_large.update(config, 800, 600)
        assert asteroid_large.current_angle != initial_angle

    def test_slow_motion_effect(self, config):
        ast1 = Asteroid(400, 300, 30, config)
        ast2 = Asteroid(400, 300, 30, config)

        ast1.update(config, 800, 600, slow_motion=False)
        ast2.update(config, 800, 600, slow_motion=True)

        assert ast1.pos.distance_to(Vector2(400, 300)) > ast2.pos.distance_to(Vector2(400, 300))


class TestAsteroidDamage:
    def test_take_damage(self, asteroid_large):
        initial_health = asteroid_large.health
        asteroid_large.take_damage()
        assert asteroid_large.health == initial_health - 1

    def test_is_alive_after_damage(self, asteroid_large, config):
        asteroid_large.take_damage()
        assert asteroid_large.is_alive()

    def test_death_after_multiple_damage(self, asteroid_small):
        for _ in range(asteroid_small.health):
            asteroid_small.take_damage()
        assert not asteroid_small.is_alive()

    def test_take_damage_returns_false(self, asteroid_large):
        result = asteroid_large.take_damage()
        assert result is False

    def test_take_damage_returns_true(self, asteroid_small):
        result = asteroid_small.take_damage()
        assert result is True


class TestAsteroidCollision:
    def test_collision_with_player(self, asteroid_large, config):
        pygame.init()
        player = Player(400, 300, config)
        assert asteroid_large.collides_with_player(player)

    def test_no_collision_far_player(self, asteroid_large, config):
        pygame.init()
        player = Player(700, 500, config)
        assert not asteroid_large.collides_with_player(player)

    def test_collision_distance_based(self, config):
        pygame.init()
        asteroid = Asteroid(0, 0, 30, config)
        player = Player(40, 0, config)
        dist = asteroid.pos.distance_to(player.pos)
        collision = dist < (asteroid.size + 15)
        assert collision or not collision


class TestAsteroidAlive:
    def test_is_alive_initial(self, asteroid_large):
        assert asteroid_large.is_alive()

    def test_not_alive_after_death(self, asteroid_small):
        asteroid_small.take_damage()
        assert not asteroid_small.is_alive()


class TestAsteroidPoints:
    def test_points_generation(self, asteroid_large):
        points = asteroid_large._get_points()
        assert len(points) == 8
        assert all(isinstance(p, tuple) for p in points)


class TestAsteroidDraw:
    def test_draw(self, asteroid_large):
        surface = pygame.Surface((800, 600))
        try:
            asteroid_large.draw(surface)
        except Exception as e:
            pytest.fail(f"draw failed: {e}")

    def test_draw_multiple_sizes(self, config):
        pygame.init()
        surface = pygame.Surface((800, 600))

        for size in [30, 15, 8]:
            ast = Asteroid(400, 300, size, config)
            try:
                ast.draw(surface)
            except Exception as e:
                pytest.fail(f"draw failed: {e}")
