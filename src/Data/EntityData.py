
class EntityData:
    def __init__(self, name, description="暂无描述", attitude="Neutral", location="未知地点", equipment=None):
        self.name = name
        self.description = description
        self.attitude = attitude  # Enemy, Neutral, Friendly
        self.location = location
        # 兼容装备字段：dict/list/str 均可；默认 None
        self.equipment = equipment

    def to_dict(self):
        return {
            "name": self.name,
            "description": self.description,
            "attitude": self.attitude,
            "location": self.location,
            "equipment": self.equipment,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data.get("name", "未知实体"),
            description=data.get("description", "暂无描述"),
            attitude=data.get("attitude", "Neutral"),
            location=data.get("location", "未知地点"),
            equipment=data.get("equipment"),
        )
    
    def __str__(self):
        return self.name

    def __repr__(self):
        return f"EntityData(name={self.name}, attitude={self.attitude})"
