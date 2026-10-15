from enum import Enum

class Rarity(Enum):
    Common = "普通"
    Rare = "稀有"
    Legendary = "传奇"
    Crystal = "水晶"

class SkillData:
    def __init__(self, id=0, name="default_skill", type=None, rarity=Rarity.Common, concentration=10, manacost=10, description="default_skill ... \n", preacttime=1.0, finishtime=1.0):
        self.id = id
        self.name = name
        self.type = type if type is not None else ["Element", "Fire"]
        self.rarity = rarity
        self.concentration = concentration
        self.manacost = manacost
        self.description = description
        self.preacttime = preacttime
        self.finishtime = finishtime

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "rarity": self.rarity.value if isinstance(self.rarity, Rarity) else self.rarity,
            "concentration": self.concentration,
            "manacost": self.manacost,
            "description": self.description,
            "preacttime": self.preacttime,
            "finishtime": self.finishtime
        }

    @classmethod
    def from_dict(cls, data):
        rarity_str = data.get("rarity", "普通")
        try:
            rarity = Rarity(rarity_str)
        except ValueError:
            map_old = {
                "Common": Rarity.Common,
                "Uncommon": Rarity.Rare,
                "Rare": Rarity.Rare,
                "Epic": Rarity.Legendary,
                "Legendary": Rarity.Legendary
            }
            rarity = map_old.get(rarity_str, Rarity.Common)
            
        return cls(
            id=data.get("id", 0),
            name=data.get("name", "default_skill"),
            type=data.get("type", ["Element", "Fire"]),
            rarity=rarity,
            concentration=data.get("concentration", 10),
            manacost=data.get("manacost", 10),
            description=data.get("description", "default_skill ... \n"),
            preacttime=data.get("preacttime", 1.0),
            finishtime=data.get("finishtime", 1.0)
        )
