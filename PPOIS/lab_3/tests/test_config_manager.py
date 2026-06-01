import pytest
import json
import os
import tempfile
from config_manager import ConfigManager


class TestConfigManager:
    @pytest.fixture
    def config_file(self):
        temp_config = {
            "window": {
                "width": 800,
                "height": 600,
                "fps": 60,
                "title": "Test"
            },
            "player": {
                "x": 400,
                "y": 300,
                "acceleration": 0.5
            },
            "bullet": {
                "speed": 7,
                "lifetime": 120
            },
            "asteroids": {
                "spawn_interval": 120
            },
            "modifiers": {
                "shield": {"duration": 400}
            }
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(temp_config, f)
            temp_file = f.name

        yield temp_file

        os.unlink(temp_file)

    def test_load_config(self, config_file):
        config = ConfigManager(config_file)
        assert config.config is not None

    def test_get_window_config(self, config_file):
        config = ConfigManager(config_file)
        window = config.get_window_config()
        assert window["width"] == 800
        assert window["height"] == 600

    def test_get_fps(self, config_file):
        config = ConfigManager(config_file)
        assert config.get_fps() == 60

    def test_get_window_size(self, config_file):
        config = ConfigManager(config_file)
        width, height = config.get_window_size()
        assert width == 800
        assert height == 600

    def test_get_nested_value(self, config_file):
        config = ConfigManager(config_file)
        value = config.get("window", "fps")
        assert value == 60

    def test_get_nonexistent_key(self, config_file):
        config = ConfigManager(config_file)
        value = config.get("nonexistent", "key")
        assert value is None

    def test_load_nonexistent_file(self):
        with pytest.raises(FileNotFoundError):
            ConfigManager("nonexistent_file.json")

    def test_load_invalid_json(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("invalid json {")
            temp_file = f.name

        try:
            with pytest.raises(ValueError):
                ConfigManager(temp_file)
        finally:
            os.unlink(temp_file)

    def test_get_player_config(self, config_file):
        config = ConfigManager(config_file)
        player = config.get_player_config()
        assert player["x"] == 400

    def test_get_bullet_config(self, config_file):
        config = ConfigManager(config_file)
        bullet = config.get_bullet_config()
        assert bullet["speed"] == 7

    def test_get_modifiers_config(self, config_file):
        config = ConfigManager(config_file)
        modifiers = config.get_modifiers_config()
        assert modifiers["shield"]["duration"] == 400
