
class ItemData:
    def __init__(self, name, description="暂无描述", item_type="item"):
        self.name = name
        self.description = description
        self.item_type = item_type

    def to_dict(self):
        return {
            "name": self.name,
            "description": self.description,
            "type": self.item_type
        }

    @classmethod
    def from_dict(cls, data):
        if isinstance(data, str):
            return cls(name=data, description="暂无描述")
        return cls(
            name=data.get("name", "未知物品"),
            description=data.get("description", "暂无描述"),
            item_type=data.get("type", "item")
        )
    
    def __str__(self):
        return self.name

    def __repr__(self):
        return f"ItemData(name={self.name}, description={self.description})"
