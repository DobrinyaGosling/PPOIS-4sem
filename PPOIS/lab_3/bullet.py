import pygame
import math
from vector2 import Vector2


class Bullet:
    def __init__(self, x, y, angle, config):
        self.pos = Vector2(x, y)
        speed = config["bullet"]["speed"]
        self.vel = Vector2(
            math.cos(math.radians(angle)) * speed,
            math.sin(math.radians(angle)) * speed,
        )
        self.lifetime = config["bullet"]["lifetime"]
        self.config = config
        self.alive = True

    def update(self, config, screen_width, screen_height, slow_motion=False):
        slow_factor = 1.0
        if slow_motion:
            slow_factor = config["modifiers"]["slow_motion"]["slow_factor"]

        self.pos = self.pos + (self.vel * slow_factor)

        if self.pos.x < 0 or self.pos.x > screen_width or self.pos.y < 0 or self.pos.y > screen_height:
            self.alive = False

        self.lifetime -= 1
        if self.lifetime <= 0:
            self.alive = False

    def draw(self, screen):
        pygame.draw.circle(screen, (255, 255, 0), (int(self.pos.x), int(self.pos.y)), 2)

    def collides_with(self, asteroid):
        dist = self.pos.distance_to(asteroid.pos)
        return dist < asteroid.size

    def is_alive(self):
        return self.alive
