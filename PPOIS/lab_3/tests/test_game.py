import pytest
import json
import os
from config_manager import ConfigManager


class TestGameScores:
    def test_load_scores_from_file(self):
        try:
            with open("highscores.json", "r") as f:
                scores = json.load(f)
            assert isinstance(scores, list)
        except FileNotFoundError:
            pytest.skip("highscores.json not found")

    def test_save_score_to_file(self):
        test_scores = [
            {"name": "TestPlayer1", "score": 1000},
            {"name": "TestPlayer2", "score": 2000}
        ]

        with open("highscores_test.json", "w") as f:
            json.dump(test_scores, f)

        with open("highscores_test.json", "r") as f:
            loaded = json.load(f)

        assert loaded[0]["score"] == 1000
        assert loaded[1]["score"] == 2000

        os.unlink("highscores_test.json")

    def test_score_sorting(self):
        scores = [
            {"name": "P3", "score": 500},
            {"name": "P2", "score": 2000},
            {"name": "P1", "score": 1000}
        ]

        sorted_scores = sorted(scores, key=lambda x: x["score"], reverse=True)

        assert sorted_scores[0]["score"] == 2000
        assert sorted_scores[1]["score"] == 1000
        assert sorted_scores[2]["score"] == 500

    def test_max_scores_limit(self):
        scores = []
        for i in range(15):
            scores.append({"name": f"P{i}", "score": 1000 - i*10})

        limited = scores[:10]
        assert len(limited) == 10


class TestGameConfig:
    def test_config_loads(self):
        config = ConfigManager("config.json").config
        assert "window" in config
        assert "player" in config
        assert "asteroids" in config
        assert "modifiers" in config

    def test_config_values(self):
        config = ConfigManager("config.json").config
        window = config["window"]
        assert window["width"] == 800
        assert window["height"] == 600
        assert window["fps"] == 60


class TestGameLogic:
    def test_asteroid_health_calculation(self):
        config = ConfigManager("config.json").config

        large_health = config["asteroids"]["large"]["health"]
        medium_health = config["asteroids"]["medium"]["health"]
        small_health = config["asteroids"]["small"]["health"]

        assert large_health == 3
        assert medium_health == 2
        assert small_health == 1

    def test_modifier_parameters(self):
        config = ConfigManager("config.json").config
        modifiers = config["modifiers"]

        assert "shield" in modifiers
        assert "speed_boost" in modifiers
        assert "slow_motion" in modifiers

        assert modifiers["shield"]["duration"] > 0
        assert modifiers["speed_boost"]["multiplier"] > 1
        assert modifiers["slow_motion"]["slow_factor"] < 1


class TestGameScore:
    def test_score_calculation(self):
        asteroid_size = 8
        score_multiplier = 10 * (3 - asteroid_size // 10)
        assert score_multiplier >= 0

    def test_score_increases_with_asteroid_destruction(self):
        score = 0

        size1 = 30
        size2 = 15
        size3 = 8

        score += 10 * (3 - size1 // 10)
        score += 10 * (3 - size2 // 10)
        score += 10 * (3 - size3 // 10)

        assert score > 0


class TestGameModifiers:
    def test_modifier_cooldowns(self):
        cooldowns = {
            "shield": 800,
            "speed_boost": 600,
            "slow_motion": 600
        }

        assert cooldowns["shield"] > cooldowns["speed_boost"]
        assert cooldowns["speed_boost"] == cooldowns["slow_motion"]

    def test_modifier_duration(self):
        config = ConfigManager("config.json").config

        shield_duration = config["modifiers"]["shield"]["duration"]
        speed_duration = config["modifiers"]["speed_boost"]["duration"]
        slow_duration = config["modifiers"]["slow_motion"]["duration"]

        assert shield_duration > 0
        assert speed_duration > 0
        assert slow_duration > 0
