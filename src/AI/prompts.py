import json
from pathlib import Path
from typing import Dict, Any
from src.paths import assets_path
from src.utils.logger import logger
PROMPTS_JSON_PATH = Path(assets_path('data', 'prompts.json'))
def load_prompts(raise_on_error: bool = False) -> Dict[str, Any]:
    try:
        if not PROMPTS_JSON_PATH.exists():
            msg = f"Prompts file not found at {PROMPTS_JSON_PATH}"
            if raise_on_error:
                raise FileNotFoundError(msg)
            logger.warning(msg)
            return {}
        with open(PROMPTS_JSON_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        msg = f"Error loading prompts.json: {e}"
        if raise_on_error:
            raise RuntimeError(msg) from e
        logger.error(msg)
        return {}
_prompts_data = load_prompts()
_parts = _prompts_data.get("system_prompt_parts", {})

SYSTEM_PROMPT: str = ""
for key in _parts:
    SYSTEM_PROMPT += f"{_parts[key]}\n"

OPENING_PROMPT_TEMPLATE       : str    = _prompts_data.get("opening_prompt_template", "")
SUMMARY_PROMPT_TEMPLATE       : str    = _prompts_data.get("summary_prompt_template", "")
STATE_SNAPSHOT_TEMPLATE       : str    = _prompts_data.get("state_snapshot_template", "")
DEFAULT_SUMMARIZE_CHUNK_SIZE  : int    = 10