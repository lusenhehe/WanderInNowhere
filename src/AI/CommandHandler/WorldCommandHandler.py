class WorldCommandHandler:
    @staticmethod
    def handle(cmd, args, game):
        if cmd == "SetLocation":
            game.player_data.location = str(args[0])
            if hasattr(game, 'location_label'):
                game.location_label.configure(text=f"📍 {game.player_data.location}")
        elif cmd == "SetTime":
            game.world["time"] = str(args[0])
        elif cmd == "SetWeather":
            game.world["weather"] = str(args[0])
