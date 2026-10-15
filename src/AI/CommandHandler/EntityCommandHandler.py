from src.Data.EntityData import EntityData
import json
class EntityCommandHandler:
    @staticmethod
    def handle(cmd, args, game):
        if cmd == "UpdateEntity":
            name = str(args[0]).strip()
            attitude = str(args[1]).strip()
            desc = str(args[2]) if len(args) > 2 else ""
            location = str(args[3]).strip() if len(args) > 3 else None
            equipment = args[4] if len(args) > 4 else None

            # equipment may arrive as a JSON string
            if isinstance(equipment, str):
                equip_s = equipment.strip()
                if (equip_s.startswith("{") and equip_s.endswith("}")) or (equip_s.startswith("[") and equip_s.endswith("]")):
                    try:
                        equipment = json.loads(equip_s)
                    except Exception:
                        equipment = equip_s
            
            # Check if exists
            found = False
            for ent in game.entities:
                if ent.name == name:
                    ent.attitude = attitude
                    ent.description = desc
                    if location is not None:
                        try:
                            ent.location = location
                        except Exception:
                            pass
                    if equipment is not None:
                        try:
                            ent.equipment = equipment
                        except Exception:
                            pass
                    found = True
                    break
            if not found:
                game.entities.append(EntityData(name, desc, attitude, location or "未知地点", equipment))
