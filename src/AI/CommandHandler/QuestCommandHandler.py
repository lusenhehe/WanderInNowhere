class QuestCommandHandler:
    @staticmethod
    def handle(cmd, args, game):
        if cmd == "AddQuest":
            qid = str(args[0])
            title = str(args[1])
            desc = str(args[2])
            game.player_data.add_quest(qid, title, desc)
        elif cmd == "UpdateQuest":
            qid = str(args[0])
            status = str(args[1])
            game.player_data.update_quest(qid, status)
        elif cmd == "CompleteQuest":
            qid = str(args[0])
            game.player_data.update_quest(qid, "已完成")
