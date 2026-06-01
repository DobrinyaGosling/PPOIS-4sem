import pygame
import math
import random
from vector2 import Vector2


class Asteroid:
    def __init__(self, x, y, size, config):
        self.pos = Vector2(x, y)
        self.size = size
        self.config = config
        self.angle = random.uniform(0, 360)
        self.health = self._get_health()

        size_name = self._get_size_name()
        speed_range = config["asteroids"][size_name]["speed_range"]
        speed = random.uniform(speed_range[0], speed_range[1])
        self.vel = Vector2(
            math.cos(math.radians(self.angle)) * speed,
            math.sin(math.radians(self.angle)) * speed,
        )
        self.rotation_speed = random.uniform(-3, 3)
        self.current_angle = random.uniform(0, 360)

    def _get_size_name(self):
        if self.size >= 25:
            return "large"
        elif self.size >= 12:
            return "medium"
        return "small"

    def _get_health(self):
        size_name = self._get_size_name()
        return self.config["asteroids"][size_name]["health"]

    def update(self, config, screen_width, screen_height, slow_motion=False):
        slow_factor = 1.0
        if slow_motion:
            slow_factor = config["modifiers"]["slow_motion"]["slow_factor"]

        self.pos = self.pos + (self.vel * slow_factor)
        self.current_angle += self.rotation_speed

        if self.pos.x < 0:
            self.pos.x = screen_width
        if self.pos.x > screen_width:
            self.pos.x = 0
        if self.pos.y < 0:
            self.pos.y = screen_height
        if self.pos.y > screen_height:
            self.pos.y = 0

    def draw(self, screen):
        points = self._get_points()
        pygame.draw.polygon(screen, (200, 200, 200), points, 2)

    def _get_points(self):
        points = []
        num_points = 8
        for i in range(num_points):
            angle = self.current_angle + (360 / num_points) * i
            x = self.pos.x + self.size * math.cos(math.radians(angle))
            y = self.pos.y + self.size * math.sin(math.radians(angle))
            points.append((x, y))
        return points

    def take_damage(self):
        self.health -= 1
        return self.health <= 0

    def collides_with_player(self, player):
        dist = self.pos.distance_to(player.pos)
        return dist < (self.size + 15)

    def is_alive(self):
        return self.health > 0
