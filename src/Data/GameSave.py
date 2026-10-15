from dataclasses import dataclass, field
from typing import List, Dict, Any, Union
import datetime
from src.Data.PlayerData import PlayerData
from src.Data.EntityData import EntityData

@dataclass
class GameSave:
    filename: str
    world_name: str
    player_data: PlayerData
    history: List[Dict[str, Any]] = field(default_factory=list)
    world: Dict[str, Any] = field(default_factory=lambda: {"time": "第1天 08:00", "weather": "晴朗"})
    entities: List[Union[EntityData, Dict[str, Any]]] = field(default_factory=list)
    summaries: List[Dict[str, Any]] = field(default_factory=list)
    summarized_line: int = 0
    last_played: str = field(default_factory=lambda: datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def update_last_played(self):
        self.last_played = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
