import pygame
import json
import math
import random
from typing import List

from vector2 import Vector2
from player import Player
from bullet import Bullet
from asteroid import Asteroid
from sounds import SoundManager
from config_manager import ConfigManager


class Game:
    def __init__(self, config_file="config.json"):
        if not pygame.display.get_init():
            pygame.init()

        self.config_manager = ConfigManager(config_file)
        self.config = self.config_manager.config

        self.width = self.config["window"]["width"]
        self.height = self.config["window"]["height"]
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption(self.config["window"]["title"])

        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

        self.sound_manager = SoundManager()

        self.reset_game()
        self.load_scores()

    def reset_game(self):
        self.player = Player(
            self.config["player"]["x"],
            self.config["player"]["y"],
            self.config,
        )
        self.bullets: List[Bullet] = []
        self.asteroids: List[Asteroid] = []
        self.score = 0
        self.spawn_timer = 0
        self.shoot_cooldown = 0
        self.modifier_cooldowns = {
            "shield": 0,
            "speed_boost": 0,
            "slow_motion": 0,
        }

        for _ in range(3):
            self._spawn_asteroid()

    def _spawn_asteroid(self):
        angle = random.uniform(0, 360)
        distance = 150
        x = self.width / 2 + distance * math.cos(math.radians(angle))
        y = self.height / 2 + distance * math.sin(math.radians(angle))

        asteroid = Asteroid(x, y, 30, self.config)
        self.asteroids.append(asteroid)

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if self.shoot_cooldown <= 0:
                        self.bullets.append(self.player.shoot())
                        self.shoot_cooldown = 10
                        self.sound_manager.play_shoot()
                if event.key == pygame.K_1 and self.modifier_cooldowns["shield"] <= 0:
                    self.player.activate_shield()
                    self.modifier_cooldowns["shield"] = self.config["modifiers"]["shield"]["cooldown"]
                if event.key == pygame.K_2 and self.modifier_cooldowns["speed_boost"] <= 0:
                    self.player.activate_speed_boost()
                    self.modifier_cooldowns["speed_boost"] = self.config["modifiers"]["speed_boost"]["cooldown"]
                if event.key == pygame.K_3 and self.modifier_cooldowns["slow_motion"] <= 0:
                    self.player.activate_slow_motion()
                    self.modifier_cooldowns["slow_motion"] = self.config["modifiers"]["slow_motion"]["cooldown"]

        keys = pygame.key.get_pressed()
        self.player.handle_input(keys)
        return True

    def update(self):
        self.player.update(self.config, self.width, self.height)

        for bullet in self.bullets[:]:
            bullet.update(self.config, self.width, self.height, self.player.slow_motion_active)
            if not bullet.alive:
                self.bullets.remove(bullet)

        for asteroid in self.asteroids[:]:
            asteroid.update(self.config, self.width, self.height, self.player.slow_motion_active)

            if asteroid.collides_with_player(self.player):
                self.player.take_damage()
                self.asteroids.remove(asteroid)
                self.sound_manager.play_hit()
                continue

            for bullet in self.bullets[:]:
                if bullet.collides_with(asteroid):
                    self.bullets.remove(bullet)
                    if asteroid.take_damage():
                        self.asteroids.remove(asteroid)
                        self._split_asteroid(asteroid)
                        self.score += 10 * (3 - asteroid.size // 10)
                        self.sound_manager.play_explosion()
                    break

        self.shoot_cooldown -= 1
        for key in self.modifier_cooldowns:
            self.modifier_cooldowns[key] -= 1

        self.spawn_timer += 1
        if self.spawn_timer > self.config["asteroids"]["spawn_interval"]:
            if len(self.asteroids) < 5 + self.score // 100:
                self._spawn_asteroid()
            self.spawn_timer = 0

    def _split_asteroid(self, asteroid):
        if asteroid.size > 15:
            new_size = asteroid.size // 2
            for _ in range(2):
                new_ast = Asteroid(asteroid.pos.x, asteroid.pos.y, new_size, self.config)
                self.asteroids.append(new_ast)

    def draw(self):
        self.screen.fill((0, 0, 0))

        self.player.draw(self.screen)

        for bullet in self.bullets:
            bullet.draw(self.screen)

        for asteroid in self.asteroids:
            asteroid.draw(self.screen)

        score_text = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
        self.screen.blit(score_text, (10, 10))

        health_text = self.small_font.render(f"Health: {self.player.health}", True, (255, 0, 0))
        self.screen.blit(health_text, (10, 50))

        y_offset = 100
        if self.modifier_cooldowns["shield"] > 0:
            shield_text = self.small_font.render(
                f"Shield: {self.modifier_cooldowns['shield']//10}",
                True,
                (100, 100, 255),
            )
        else:
            shield_text = self.small_font.render("Shield (1) - Ready", True, (100, 255, 100))
        self.screen.blit(shield_text, (10, y_offset))

        y_offset += 30
        if self.modifier_cooldowns["speed_boost"] > 0:
            boost_text = self.small_font.render(
                f"Speed Boost: {self.modifier_cooldowns['speed_boost']//10}",
                True,
                (255, 200, 0),
            )
        else:
            boost_text = self.small_font.render("Speed Boost (2) - Ready", True, (100, 255, 100))
        self.screen.blit(boost_text, (10, y_offset))

        y_offset += 30
        if self.modifier_cooldowns["slow_motion"] > 0:
            slow_text = self.small_font.render(
                f"Slow Motion: {self.modifier_cooldowns['slow_motion']//10}",
                True,
                (100, 200, 255),
            )
        else:
            slow_text = self.small_font.render("Slow Motion (3) - Ready", True, (100, 255, 100))
        self.screen.blit(slow_text, (10, y_offset))

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            running = self.handle_input()

            if self.player.health <= 0:
                break

            self.update()
            self.draw()

            self.clock.tick(self.config["window"]["fps"])

        return self.score

    def load_scores(self):
        try:
            with open("highscores.json", "r") as f:
                self.highscores = json.load(f)
        except FileNotFoundError:
            self.highscores = []

    def save_score(self, name: str, score: int):
        self.highscores.append({"name": name, "score": score})
        self.highscores.sort(key=lambda x: x["score"], reverse=True)
        self.highscores = self.highscores[:10]

        with open("highscores.json", "w") as f:
            json.dump(self.highscores, f, indent=2)

    def show_game_over(self, score: int):
        self.sound_manager.stop_music()
        showing = True
        input_text = ""

        while showing:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        showing = False
                    elif event.key == pygame.K_RETURN:
                        if input_text.strip():
                            self.save_score(input_text.strip(), score)
                        showing = False
                    elif event.key == pygame.K_BACKSPACE:
                        input_text = input_text[:-1]
                    else:
                        if len(input_text) < 20:
                            input_text += event.unicode

            self.screen.fill((0, 0, 0))

            game_over_text = self.font.render("GAME OVER", True, (255, 0, 0))
            self.screen.blit(
                game_over_text,
                (self.width // 2 - game_over_text.get_width() // 2, 100),
            )

            score_text = self.font.render(f"Score: {score}", True, (255, 255, 255))
            self.screen.blit(
                score_text,
                (self.width // 2 - score_text.get_width() // 2, 200),
            )

            if self.highscores and score > self.highscores[0]["score"]:
                new_record = self.small_font.render("NEW RECORD!", True, (255, 215, 0))
                self.screen.blit(
                    new_record,
                    (self.width // 2 - new_record.get_width() // 2, 280),
                )

                name_label = self.small_font.render("Enter name:", True, (255, 255, 255))
                self.screen.blit(name_label, (self.width // 2 - 100, 320))

                name_text = self.small_font.render(input_text + "|", True, (0, 255, 0))
                self.screen.blit(name_text, (self.width // 2 - 50, 360))
            else:
                hint = self.small_font.render("Press ESC to continue", True, (200, 200, 200))
                self.screen.blit(
                    hint,
                    (self.width // 2 - hint.get_width() // 2, 300),
                )

            pygame.display.flip()
            self.clock.tick(60)

        return True

    def show_menu(self):
        selected = 0
        menu_items = ["Start Game", "High Scores", "Help", "Exit"]

        selecting = True
        while selecting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected = (selected - 1) % len(menu_items)
                    if event.key == pygame.K_DOWN:
                        selected = (selected + 1) % len(menu_items)
                    if event.key == pygame.K_RETURN:
                        if selected == 0:
                            return "play"
                        elif selected == 1:
                            return "scores"
                        elif selected == 2:
                            return "help"
                        elif selected == 3:
                            return "exit"

            self.screen.fill((0, 0, 0))

            title = self.font.render("ASTEROIDS", True, (0, 255, 0))
            self.screen.blit(title, (self.width // 2 - title.get_width() // 2, 50))

            for i, item in enumerate(menu_items):
                color = (255, 255, 0) if i == selected else (200, 200, 200)
                text = self.font.render(item, True, color)
                self.screen.blit(text, (self.width // 2 - text.get_width() // 2, 150 + i * 80))

            pygame.display.flip()
            self.clock.tick(60)

    def show_help(self):
        showing = True
        help_text = [
            "ASTEROIDS HELP",
            "",
            "CONTROLS:",
            "LEFT/RIGHT - Rotate ship",
            "UP - Accelerate",
            "SPACE - Shoot",
            "",
            "MODIFIERS:",
            "1 - Shield (absorbs 1 hit)",
            "2 - Speed Boost (faster movement)",
            "3 - Slow Motion (slows asteroids)",
            "",
            "GOAL:",
            "Destroy all asteroids without",
            "getting hit 3 times",
            "",
            "Press ESC to go back",
        ]

        while showing:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        showing = False

            self.screen.fill((0, 0, 0))

            y = 30
            for line in help_text:
                if line.startswith("ASTEROIDS") or line.startswith("CONTROLS") or line.startswith("MODIFIERS") or line.startswith("GOAL"):
                    text = self.font.render(line, True, (0, 255, 0))
                else:
                    text = self.small_font.render(line, True, (200, 200, 200))
                self.screen.blit(text, (50, y))
                y += 30

            pygame.display.flip()
            self.clock.tick(60)

        return True

    def show_scores(self):
        showing = True

        while showing:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        showing = False

            self.screen.fill((0, 0, 0))

            title = self.font.render("HIGH SCORES", True, (0, 255, 0))
            self.screen.blit(title, (self.width // 2 - title.get_width() // 2, 30))

            if self.highscores:
                y = 100
                for i, entry in enumerate(self.highscores[:10]):
                    text = self.small_font.render(
                        f"{i+1}. {entry['name']:<20} {entry['score']}",
                        True,
                        (200, 200, 200),
                    )
                    self.screen.blit(text, (self.width // 2 - 150, y))
                    y += 40
            else:
                text = self.small_font.render("No scores yet", True, (200, 200, 200))
                self.screen.blit(text, (self.width // 2 - text.get_width() // 2, 200))

            hint = self.small_font.render("Press ESC to go back", True, (100, 100, 100))
            self.screen.blit(hint, (self.width // 2 - hint.get_width() // 2, self.height - 50))

            pygame.display.flip()
            self.clock.tick(60)

        return True

    def main_loop(self):
        running = True
        while running:
            action = self.show_menu()

            if action == "play":
                self.reset_game()
                score = self.game_play()
                self.show_game_over(score)
            elif action == "scores":
                self.load_scores()
                self.show_scores()
            elif action == "help":
                self.show_help()
            elif action == "exit" or action is None:
                running = False

        pygame.quit()

    def game_play(self):
        self.sound_manager.play_music()
        return self.run()

    def get_score(self):
        return self.score

    def get_player(self):
        return self.player

    def get_asteroids(self):
        return self.asteroids

    def get_bullets(self):
        return self.bullets

    def get_highscores(self):
        return self.highscores


def main():
    game = Game()
    game.main_loop()
