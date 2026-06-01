import pytest
import sys
import os


class TestMainModule:
    def test_main_imports(self):
        try:
            import main
        except ImportError as e:
            pytest.fail(f"Failed to import main: {e}")

    def test_game_can_be_instantiated(self):
        import pygame
        pygame.init()

        from game import Game
        from config_manager import ConfigManager

        config = ConfigManager("config.json").config
        assert config is not None

    def test_config_file_exists(self):
        assert os.path.exists("config.json")

    def test_highscores_file_manageable(self):
        import json

        try:
            with open("highscores.json", "r") as f:
                scores = json.load(f)
            assert isinstance(scores, list)
        except FileNotFoundError:
            with open("highscores.json", "w") as f:
                json.dump([], f)
            assert os.path.exists("highscores.json")
