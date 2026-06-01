import json


class ConfigManager:
    def __init__(self, config_file="config.json"):
        self.config = self._load_config(config_file)

    def _load_config(self, config_file):
        try:
            with open(config_file, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Config file {config_file} not found")
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON in {config_file}")

    def get(self, *keys):
        value = self.config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return None
        return value

    def get_window_config(self):
        return self.get("window")

    def get_player_config(self):
        return self.get("player")

    def get_bullet_config(self):
        return self.get("bullet")

    def get_asteroids_config(self):
        return self.get("asteroids")

    def get_modifiers_config(self):
        return self.get("modifiers")

    def get_fps(self):
        return self.get("window", "fps")

    def get_window_size(self):
        window = self.get_window_config()
        return window["width"], window["height"]
