import json
import os

class ConfigManager:
    def __init__(self, config_path="config.json"):
        self.config_path = config_path
        self.default_config = {
            "shortcuts": {
                "save": "<Control-s>",
                "save_as": "<Control-S>", # Shift-S usually needs explicit binding or different notation depending on OS
                "undo": "<Control-z>",
                "redo": "<Control-y>",
                "quit": "<Control-q>"
            },
            "theme": "darkly"
        }
        self.config = self.load_config()

    def load_config(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return self.default_config
        return self.default_config

    def save_config(self):
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=4)

    def get_shortcut(self, action):
        return self.config["shortcuts"].get(action, "")

    def set_shortcut(self, action, key_sequence):
        self.config["shortcuts"][action] = key_sequence
        self.save_config()
