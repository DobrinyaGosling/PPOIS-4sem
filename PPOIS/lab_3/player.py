import pygame
import math
from vector2 import Vector2


class Player:
    def __init__(self, x, y, config):
        self.pos = Vector2(x, y)
        self.vel = Vector2(0, 0)
        self.angle = 0
        self.config = config
        self.health = 3
        self.shield_active = False
        self.shield_time = 0
        self.speed_boost_active = False
        self.speed_boost_time = 0
        self.slow_motion_active = False
        self.slow_motion_time = 0

    def handle_input(self, keys):
        if keys[pygame.K_LEFT]:
            self.angle -= self.config["player"]["rotation_speed"]
        if keys[pygame.K_RIGHT]:
            self.angle += self.config["player"]["rotation_speed"]
        if keys[pygame.K_UP]:
            acc = self.config["player"]["acceleration"]
            if self.speed_boost_active:
                acc *= self.config["modifiers"]["speed_boost"]["multiplier"]
            self.vel.x += math.cos(math.radians(self.angle)) * acc
            self.vel.y += math.sin(math.radians(self.angle)) * acc

    def update(self, config, screen_width, screen_height):
        max_vel = config["player"]["max_velocity"]
        if self.vel.length() > max_vel:
            scale = max_vel / self.vel.length()
            self.vel = self.vel * scale

        self.vel = self.vel * config["player"]["friction"]
        self.pos = self.pos + self.vel

        if self.pos.x < 0:
            self.pos.x = screen_width
        if self.pos.x > screen_width:
            self.pos.x = 0
        if self.pos.y < 0:
            self.pos.y = screen_height
        if self.pos.y > screen_height:
            self.pos.y = 0

        if self.shield_active:
            self.shield_time -= 1
            if self.shield_time <= 0:
                self.shield_active = False

        if self.speed_boost_active:
            self.speed_boost_time -= 1
            if self.speed_boost_time <= 0:
                self.speed_boost_active = False

        if self.slow_motion_active:
            self.slow_motion_time -= 1
            if self.slow_motion_time <= 0:
                self.slow_motion_active = False

    def draw(self, screen):
        points = [
            (
                self.pos.x + 12 * math.cos(math.radians(self.angle)),
                self.pos.y + 12 * math.sin(math.radians(self.angle)),
            ),
            (
                self.pos.x + 10 * math.cos(math.radians(self.angle + 120)),
                self.pos.y + 10 * math.sin(math.radians(self.angle + 120)),
            ),
            (
                self.pos.x + 10 * math.cos(math.radians(self.angle + 240)),
                self.pos.y + 10 * math.sin(math.radians(self.angle + 240)),
            ),
        ]
        pygame.draw.polygon(screen, (0, 255, 0), points, 2)

        if self.shield_active:
            radius = self.config["player"]["radius"] + 10
            pygame.draw.circle(screen, (0, 100, 255), (int(self.pos.x), int(self.pos.y)), radius, 2)

    def shoot(self):
        from bullet import Bullet
        return Bullet(self.pos.x, self.pos.y, self.angle, self.config)

    def activate_shield(self):
        self.shield_active = True
        self.shield_time = self.config["modifiers"]["shield"]["duration"]

    def activate_speed_boost(self):
        self.speed_boost_active = True
        self.speed_boost_time = self.config["modifiers"]["speed_boost"]["duration"]

    def activate_slow_motion(self):
        self.slow_motion_active = True
        self.slow_motion_time = self.config["modifiers"]["slow_motion"]["duration"]

    def take_damage(self):
        if self.shield_active:
            self.shield_active = False
        else:
            self.health -= 1

    def is_alive(self):
        return self.health > 0
