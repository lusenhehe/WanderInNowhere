
from src.Data.ItemData import ItemData
from src.Data.SkillData import SkillData, Rarity
from src.Data.EntityData import EntityData
from src.Data.base_data_model import BaseDataModel


class PlayerData(BaseDataModel):
    @classmethod
    def get_default_values(cls):
        return {
            "name": "冒险者",
            "status": {
                "race": "人类",
                "hp": "100/100",
                "magic": "100/100",
                "magic_concentration": 20,
                "mp": 40,
                "mp_max": 40,
                "magic_density": "50",
                "hunger": "100/100",
                "injury": "无",
                "action": "正常"
            },
            "inventory": [],
            "equipment": {
                "head": None,
                "body": None,
                "legs": None,
                "weapon": None,
                "accessory": None
            },
            "money": 0,
            "location": "未知地点",
            "quests": [],
            "entities": [],
            "skills": []
        }

    def __init__(self, name="冒险者", status=None, inventory=None, equipment=None,
                 money=0, location="未知地点", quests=None, skills=None, entities=None):
        # 获取默认值
        defaults = self.get_default_values()

        # 合并提供的参数和默认值
        self.name = name if name != "冒险者" or defaults["name"] == "冒险者" else defaults["name"]
        self.status = defaults["status"].copy()
        if status:
            self.status.update(status)

        self.inventory = inventory if inventory is not None else defaults["inventory"].copy()
        self.equipment = equipment if equipment is not None else defaults["equipment"].copy()
        self.money = money if money != 0 else defaults["money"]
        self.location = location if location != "未知地点" else defaults["location"]
        self.quests = quests if quests is not None else defaults["quests"].copy()
        self.entities = entities if entities is not None else defaults["entities"].copy()
        self.skills = skills if skills is not None else defaults["skills"].copy()

        # 确保MP字段的一致性
        self._ensure_mp_consistency()

        # 处理技能数据转换
        self._process_skills(skills)

    def _ensure_mp_consistency(self):
        """确保MP字段的一致性"""
        # Ensure MP fields are present and consistent with magic concentration
        conc = self.status.get("magic_concentration", 20)
        # Default mp_max scales with concentration (simple formula; can be adjusted)
        if not self.status.get("mp_max"):
            try:
                self.status["mp_max"] = int(conc * 2)
            except:
                self.status["mp_max"] = 40
        if not self.status.get("mp"):
            self.status["mp"] = int(self.status.get("mp_max", 40))

        # Keep the display 'magic' field in sync for backward compatibility
        self._sync_magic_string()

    def _sync_magic_string(self):
        """同步魔法字符串显示"""
        try:
            cur = int(self.status.get("mp", 0))
            ma = int(self.status.get("mp_max", 0))
            self.status["magic"] = f"{cur}/{ma}"
        except:
            self.status["magic"] = self.status.get("magic", "0/0")

    def _process_skills(self, skills):
        """处理技能数据转换"""
        if not skills:
            return

        for s in skills:
            if isinstance(s, dict):
                # Try to convert legacy dict or new dict to SkillData
                # Check if it has new fields
                if "manacost" in s:
                    self.skills.append(SkillData.from_dict(s))
                else:
                    # Legacy dict: {"name": "Fireball", "element": "Fire", "cost": "10MP", "density": "Low", "description": "..."}
                    # 使用业务逻辑工具来解析资源字符串
                    from src.utils.business_logic_utils import BusinessLogicUtils
                    cost_val = BusinessLogicUtils.parse_resource_string(s.get("cost", "0"))[0]

                    # Map density to concentration (arbitrary mapping for now)
                    density_map = {"Low": 10, "Medium": 50, "High": 100, "一般": 20, "无": 0}
                    conc_val = density_map.get(s.get("density"), 10)

                    self.skills.append(SkillData(
                        name=s.get("name", "Unknown"),
                        type=["Element", s.get("element", "None")],
                        manacost=cost_val,
                        concentration=conc_val,
                        description=s.get("description", "")
                    ))
            elif isinstance(s, SkillData):
                self.skills.append(s)

    def add_skill(self, name, element, cost, density, description, rarity="普通", preacttime=1.0, finishtime=1.0):
        # Check if skill already exists
        for s in self.skills:
            if s.name == name:
                return False  # Already exists

        # Parse cost using business logic utils
        from src.utils.business_logic_utils import BusinessLogicUtils
        cost_val = BusinessLogicUtils.parse_resource_string(str(cost))[0]

        density_map = {"Low": 10, "Medium": 50, "High": 100, "一般": 20, "无": 0}
        conc_val = density_map.get(density, 10)
        if isinstance(density, int):
            conc_val = density

        # Handle rarity string to Enum
        try:
            rarity_enum = Rarity(rarity)
        except ValueError:
            # Fallback mapping for English values
            map_old = {
                "Common": Rarity.Common,
                "Uncommon": Rarity.Rare,
                "Rare": Rarity.Rare,
                "Epic": Rarity.Legendary,
                "Legendary": Rarity.Legendary
            }
            rarity_enum = map_old.get(rarity, Rarity.Common)

        new_skill = SkillData(
            name=name,
            type=["Element", element],
            manacost=cost_val,
            concentration=conc_val,
            description=description,
            rarity=rarity_enum,
            preacttime=float(preacttime),
            finishtime=float(finishtime)
        )
        self.skills.append(new_skill)
        return True
    def remove_skill(self, name):
        for i, s in enumerate(self.skills):
            if s.name == name:
                del self.skills[i]
                return True
        return False
    def add_quest(self, qid, title, desc):
        for q in self.quests:
            if q["id"] == qid:
                return
        self.quests.append({"id": qid, "title": title, "description": desc, "status": "进行中"})

    def update_quest(self, qid, status):
        for q in self.quests:
            if q["id"] == qid:
                q["status"] = status
                return True
        return False

    def has_item(self, item_name):
        """检查是否拥有物品"""
        from src.utils.business_logic_utils import BusinessLogicUtils
        return BusinessLogicUtils.find_item_by_name(self.inventory, item_name) is not None

    def get_item(self, item_name):
        """获取物品"""
        from src.utils.business_logic_utils import BusinessLogicUtils
        return BusinessLogicUtils.find_item_by_name(self.inventory, item_name)

    def remove_item(self, item_name):
        """从库存中移除物品"""
        from src.utils.business_logic_utils import BusinessLogicUtils
        item = BusinessLogicUtils.find_item_by_name(self.inventory, item_name)
        if item is not None:
            self.inventory.remove(item)
            return item
        return None

    def add_item(self, item):
        """添加物品到库存"""
        self.inventory.append(item)
        return True
    def get_mp(self):
        """获取当前MP值"""
        from src.utils.business_logic_utils import BusinessLogicUtils
        return BusinessLogicUtils.parse_resource_string(self.status.get("magic", "0/0"))[0]

    def get_mp_max(self):
        """获取最大MP值"""
        from src.utils.business_logic_utils import BusinessLogicUtils
        return BusinessLogicUtils.parse_resource_string(self.status.get("magic", "0/0"))[1]

    def set_mp(self, value: int):
        """设置MP值"""
        from src.utils.business_logic_utils import BusinessLogicUtils
        max_mp = self.get_mp_max()
        current_mp = min(max(0, int(value)), max_mp)
        self.status["mp"] = current_mp
        self.status["magic"] = BusinessLogicUtils.format_resource_string(current_mp, max_mp)

    def set_mp_max(self, max_val: int, adjust_current: bool = True):
        """设置最大MP值"""
        from src.utils.business_logic_utils import BusinessLogicUtils
        max_mp = max(0, int(max_val))
        self.status["mp_max"] = max_mp

        if adjust_current:
            current_mp = self.get_mp()
            if current_mp > max_mp:
                self.set_mp(max_mp)
            else:
                # 同步magic字符串
                self.status["magic"] = BusinessLogicUtils.format_resource_string(current_mp, max_mp)

    def change_mp(self, delta: int):
        """改变MP值"""
        current_mp = self.get_mp()
        self.set_mp(current_mp + int(delta))
        """重写to_dict以正确处理装备数据"""
        # 使用基类的to_dict作为基础
        result = super().to_dict()

        # 特殊处理装备数据
        equipment_dict = {}
        for slot, item in self.equipment.items():
            if item and hasattr(item, 'to_dict'):
                equipment_dict[slot] = item.to_dict()
            else:
                equipment_dict[slot] = None
        result["equipment"] = equipment_dict

        # 确保字段名兼容
        result["player_name"] = result.pop("name", "冒险者")

        return result

    @classmethod
    def from_dict(cls, data):
        """重写from_dict以处理装备的特殊逻辑"""
        # 预处理装备数据
        equipment_data = data.get("equipment", {})
        equipment = {}

        for slot, item_data in equipment_data.items():
            if item_data is None:
                equipment[slot] = None
            elif isinstance(item_data, str):
                # 旧格式：item_data是名称
                equipment[slot] = ItemData(item_data, "暂无描述")
            elif isinstance(item_data, dict):
                # 新格式：item_data是字典
                equipment[slot] = ItemData.from_dict(item_data)
            else:
                equipment[slot] = None

        # 处理字段名兼容性
        processed_data = data.copy()
        if "player_name" in data and "name" not in data:
            processed_data["name"] = data["player_name"]

        # 处理inventory
        inventory_data = processed_data.get("inventory", [])
        if inventory_data:
            processed_data["inventory"] = [
                ItemData.from_dict(item) for item in inventory_data
                if item is not None
            ]

        # 处理skills
        skills_data = processed_data.get("skills", [])
        if skills_data:
            processed_data["skills"] = [
                SkillData.from_dict(skill) if isinstance(skill, dict) else skill
                for skill in skills_data
            ]

        # 设置装备
        processed_data["equipment"] = equipment

        # 只保留构造函数接受的参数
        allowed_keys = {"name", "status", "inventory", "equipment", "money", "location", "quests", "skills", "entities"}
        filtered_data = {k: v for k, v in processed_data.items() if k in allowed_keys}

        # 使用基类的from_dict
        return super().from_dict(filtered_data)

    def to_dict(self):
        """重写to_dict以确保嵌套对象也被序列化"""
        data = super().to_dict()

        # 转换inventory中的ItemData对象
        if "inventory" in data and data["inventory"]:
            data["inventory"] = [
                item.to_dict() if hasattr(item, 'to_dict') else item
                for item in data["inventory"]
            ]

        # 转换equipment中的ItemData对象
        if "equipment" in data and data["equipment"]:
            equipment_dict = {}
            for slot, item in data["equipment"].items():
                if item is None:
                    equipment_dict[slot] = None
                elif hasattr(item, 'to_dict'):
                    equipment_dict[slot] = item.to_dict()
                else:
                    equipment_dict[slot] = item
            data["equipment"] = equipment_dict

        # 转换skills中的SkillData对象
        if "skills" in data and data["skills"]:
            data["skills"] = [
                skill.to_dict() if hasattr(skill, 'to_dict') else skill
                for skill in data["skills"]
            ]

        # 转换entities中的EntityData对象
        if "entities" in data and data["entities"]:
            data["entities"] = [
                entity.to_dict() if hasattr(entity, 'to_dict') else entity
                for entity in data["entities"]
            ]

        return data