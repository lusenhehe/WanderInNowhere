class SkillCommandHandler:
    @staticmethod
    def handle(cmd, args, game):
        if cmd == "AddSkill":
            name = str(args[0])
            element = str(args[1]) if len(args) > 1 else "无"
            cost = str(args[2]) if len(args) > 2 else "0"
            density = str(args[3]) if len(args) > 3 else "无"
            rarity = str(args[4]) if len(args) > 4 else "普通"
            
            def parse_time(val):
                try:
                    return float(str(val).lower().replace('s', ''))
                except ValueError:
                    return 1.0

            preacttime = parse_time(args[5]) if len(args) > 5 else 1.0
            finishtime = parse_time(args[6]) if len(args) > 6 else 1.0
            
            description = str(args[7]) if len(args) > 7 else "暂无描述"
            """
            AddSkill(\"火苗术\",\"火\",5,10,\"普通\",1.0,0.5,\"在指尖凝聚一簇小火苗,可点燃易燃物\")
            """
            game.player_data.add_skill(name, element, cost, density, description, rarity, preacttime, finishtime)
        elif cmd == "RemoveSkill":
            name = str(args[0])
            game.player_data.remove_skill(name)
