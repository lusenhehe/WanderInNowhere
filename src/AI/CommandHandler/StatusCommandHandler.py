import re
class StatusCommandHandler:
    @staticmethod
    def handle(cmd, args, game):
        if cmd == "SetHp":
            game.player_data.status["hp"] = str(args[0])
        elif cmd == "SetMagic":
            game.player_data.status["magic"] = str(args[0])
        elif cmd == "SetHunger":
            game.player_data.status["hunger"] = str(args[0])
        elif cmd == "SetInjury":
            val = str(args[0])
            if val in ["无", "None", "none", ""]:
                game.player_data.status["injury"] = "无"
            else:
                game.player_data.status["injury"] = val
        elif cmd == "RemoveInjury":
            val = str(args[0]).strip()
            current = game.player_data.status.get("injury", "无")
            if current != "无":
                # Split by comma or Chinese comma
                injuries = re.split(r'[,，]', current)
                injuries = [i.strip() for i in injuries if i.strip()]
                
                if val in injuries:
                    injuries.remove(val)
                
                if not injuries:
                    game.player_data.status["injury"] = "无"
                else:
                    game.player_data.status["injury"] = ", ".join(injuries)
        elif cmd == "SetAction":
            game.player_data.status["action"] = str(args[0])
        elif cmd == "SetMoney":
            game.player_data.money = int(args[0])
