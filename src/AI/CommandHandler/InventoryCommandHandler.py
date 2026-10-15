from src.Data.ItemData import ItemData
class InventoryCommandHandler:
    @staticmethod
    def handle(cmd, args, game):
        if cmd == "AddItem":
            name = str(args[0]).strip()
            count = int(args[1]) if len(args) > 1 else 1
            desc = str(args[2]) if len(args) > 2 else "暂无描述"
            for _ in range(count):
                game.player_data.add_item(ItemData(name, desc))
        elif cmd == "RemoveItem":
            name = str(args[0]).strip()
            count = int(args[1]) if len(args) > 1 else 1
            removed = 0
            while removed < count:
                if game.player_data.remove_item(name):
                    removed += 1
                else:
                    break
        elif cmd == "EquipItem":
            name = str(args[0]).strip()
            slot = str(args[1]).strip()
            desc = str(args[2]) if len(args) > 2 else "暂无描述"
            if slot in game.player_data.equipment:
                # Unequip current
                prev_item = game.player_data.equipment.get(slot)
                if prev_item:
                    game.player_data.add_item(prev_item)
                
                # Equip new (remove from inventory first)
                removed_item = game.player_data.remove_item(name)
                if removed_item:
                    game.player_data.equipment[slot] = removed_item
                else:
                    # If not in inventory, just equip it (spawned)
                    game.player_data.equipment[slot] = ItemData(name, desc)
        elif cmd == "UnequipItem":
            slot = str(args[0]).strip()
            if slot in game.player_data.equipment:
                prev_item = game.player_data.equipment.get(slot)
                if prev_item:
                    game.player_data.add_item(prev_item)
                game.player_data.equipment[slot] = None
