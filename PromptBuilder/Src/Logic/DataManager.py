import json
import os

class DataManager:
    def __init__(self):
        self.current_file_path = None
        self.data = {
            "system_prompt_parts": {},
            "opening_prompt_template": "",
            "main_locations": [],
            "skills": [],
            "presets": {} # New: Store prompt snapshots
        }
        self.is_dirty = False
        self.on_dirty_change = None # Callback function(is_dirty)

    def set_dirty(self, dirty):
        if self.is_dirty != dirty:
            self.is_dirty = dirty
            if self.on_dirty_change:
                self.on_dirty_change(dirty)

    def load_file(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        self.current_file_path = file_path
        self.set_dirty(False)

    def save_file(self, file_path=None):
        path = file_path if file_path else self.current_file_path
        if not path:
            raise ValueError("No file path specified")
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)
        
        self.current_file_path = path
        self.set_dirty(False)

    def update_part(self, key, content):
        if "system_prompt_parts" not in self.data:
            self.data["system_prompt_parts"] = {}
        
        current_content = self.data["system_prompt_parts"].get(key, "")
        if current_content != content:
            self.data["system_prompt_parts"][key] = content
            self.set_dirty(True)

    def add_part(self, key):
        if "system_prompt_parts" not in self.data:
            self.data["system_prompt_parts"] = {}
        if key not in self.data["system_prompt_parts"]:
            self.data["system_prompt_parts"][key] = ""
            self.set_dirty(True)
            return True
        return False

    def delete_part(self, key):
        if "system_prompt_parts" in self.data and key in self.data["system_prompt_parts"]:
            del self.data["system_prompt_parts"][key]
            self.set_dirty(True)

    def update_opening(self, content):
        if self.data.get("opening_prompt_template") != content:
            self.data["opening_prompt_template"] = content
            self.set_dirty(True)
            
    def update_skills(self, skills_list):
        # Simple check if changed could be expensive, so we assume dirty if this method is called with valid data
        self.data["skills"] = skills_list
        self.set_dirty(True)

    # --- Preset Management ---
    def get_presets(self):
        return list(self.data.get("presets", {}).keys())

    def save_preset(self, name):
        if "presets" not in self.data:
            self.data["presets"] = {}
        
        # Deep copy current parts
        import copy
        self.data["presets"][name] = copy.deepcopy(self.data.get("system_prompt_parts", {}))
        self.set_dirty(True)

    def load_preset(self, name):
        if "presets" in self.data and name in self.data["presets"]:
            import copy
            self.data["system_prompt_parts"] = copy.deepcopy(self.data["presets"][name])
            self.set_dirty(True)
            return True
        return False

    def delete_preset(self, name):
        if "presets" in self.data and name in self.data["presets"]:
            del self.data["presets"][name]
            self.set_dirty(True)
