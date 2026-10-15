import os,sys
from typing import Final
def is_frozen() -> bool:
    return bool(getattr(sys, "frozen", False))
def base_dir() -> str:
    if is_frozen():
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR: Final[str] = base_dir()
def project_path(*parts: str) -> str:
    return os.path.join(BASE_DIR, *parts)
def assets_path(*parts: str) -> str:
    return project_path("Assets", *parts)
def save_path(*parts: str) -> str:
    return project_path("Save", *parts)
def saves_dir() -> str:
    return save_path("saves")
