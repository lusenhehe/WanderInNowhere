import time

from src.Data.GameSave import GameSave
from src.saves import save_game_data


class PersistenceHandlersMixin:
    def save_and_quit(self, quit_app=True):
        # 准备保存的历史记录，移除系统提示以减小存档大小
        save_history = self.history
        save_summarized_line = self.summarized_line
        if save_history and save_history[0].get("role") == "system":
            save_history = save_history[1:]  # 移除系统提示
            save_summarized_line = max(0, self.summarized_line - 1)  # 调整summarized_line
        
        save_data = GameSave(
            filename=self.filename,
            world_name=self.world_name,
            player_data=self.player_data,
            last_played=int(time.time()),
            history=save_history,
            summaries=self.summaries,
            summarized_line=save_summarized_line,
            world=self.world,
            entities=self.entities,
        )
        save_game_data(save_data)

        if quit_app:
            self.app_window.show_main_menu()
