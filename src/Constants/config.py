from src.paths import assets_path, save_path, saves_dir
from src.config_model import AppConfig
from src.Constants.game_constants import (
    MAX_HISTORY,
    DEFAULT_TEMPERATURE,
    DEFAULT_MAX_TOKENS,
    DEFAULT_API_URL,
    DEFAULT_API_KEY,
    DEFAULT_MODEL,
    DEFAULT_MODELS,
)
CONFIG_PATH =  save_path('config.lzn')
SAVES_DIR   =  saves_dir()
ICON_PATH   =  assets_path('Images', 'GameIcon', 'icon.ico')
DEFAULT_CONFIG = {
    "debug": False,
    "theme": "darkly",
    "api_url": DEFAULT_API_URL,
    "api_key": DEFAULT_API_KEY,
    "model": DEFAULT_MODEL,
    "temperature": DEFAULT_TEMPERATURE,
    "max_tokens": DEFAULT_MAX_TOKENS,
    "ssl_verify": False,
    "max_history": MAX_HISTORY,
    "font": "Chinese.ttf",
    "stream": True
}
_cached_config = None
def load_config(force_reload=False):
    global _cached_config
    if _cached_config is None or force_reload:
        from src.SaveLoad.ConfigLoader import load_encrypted_config
        _cached_config = load_encrypted_config(CONFIG_PATH, DEFAULT_CONFIG)
    return _cached_config.copy()

def save_config(config_dict):
    """Save configuration dict to encrypted file."""
    global _cached_config
    from src.SaveLoad.ConfigLoader import save_encrypted_config
    save_encrypted_config(CONFIG_PATH, config_dict)
    _cached_config = config_dict.copy()
def load_app_config(force_reload: bool = False) -> AppConfig:
    """Typed config wrapper (keeps unknown keys via AppConfig.extras)."""
    return AppConfig.from_dict(load_config(force_reload=force_reload))
def save_app_config(cfg: AppConfig) -> None:
    """Save typed config."""
    save_config(cfg.to_dict())
