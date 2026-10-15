import json
import queue
import threading
from PyQt6.QtWidgets import QMessageBox
from src.AI.history_pipeline import prepare_history_for_request
from src.utils.history_optimizer import summarize_old_history
from src.AI.parser import AICommandExecutor, STATE_START_PATTERN, strip_state_block
from src.AI.prompts import STATE_SNAPSHOT_TEMPLATE


class AiFlowHandlersMixin:
    def get_current_state_msg(self) -> str:
        inv_list = [item.name if hasattr(item, "name") else str(item) for item in self.player_data.inventory]

        equipment_display = {}
        for slot, item in self.player_data.equipment.items():
            equipment_display[slot] = item.name if item else None

        skills_list = []
        if hasattr(self.player_data, "skills") and self.player_data.skills:
            for s in self.player_data.skills:
                skills_list.append(s.to_dict() if hasattr(s, "to_dict") else s)

        return STATE_SNAPSHOT_TEMPLATE.format(
            location  =self.player_data.location,
            time      =self.world.get('time', '未知'),
            weather   =self.world.get('weather', '未知'),
            status    =json.dumps(self.player_data.status, ensure_ascii=False),
            inventory =json.dumps(inv_list, ensure_ascii=False),
            money     =self.player_data.money,
            equipment =json.dumps(equipment_display, ensure_ascii=False),
            skills=json.dumps(skills_list, ensure_ascii=False),
            quests=json.dumps(getattr(self.player_data, 'quests', []), ensure_ascii=False),
            entities=json.dumps([{"name": n.name, "attitude": n.attitude} for n in self.entities], ensure_ascii=False)
        )

    def process_queue(self):
        try:
            while True:
                msg_type, data = self.msg_queue.get_nowait()
                if msg_type == "ai_status":
                    # 避免刷屏：相同状态不重复展示
                    if getattr(self, "_last_ai_status", None) != data:
                        self._last_ai_status = data
                        if data:
                            self.append_text(f"[系统] {data}", "system")
                elif msg_type == "debug_history":
                    self.update_ui_display()
                elif msg_type == "token":
                    if self.hide_streaming:
                        continue
                    self.stream_buffer += data
                    start_match = STATE_START_PATTERN.search(self.stream_buffer)
                    if start_match:
                        valid_content = self.stream_buffer[:start_match.start()]
                        if valid_content:
                            self.append_text(valid_content, "assistant")
                        self.hide_streaming = True
                        self.stream_buffer = ""
                        continue

                    # Keep a sufficiently long tail to avoid leaking partial control tags.
                    if len(self.stream_buffer) > 128:
                        last_lt_index = self.stream_buffer.rfind("<")
                        if last_lt_index != -1 and (len(self.stream_buffer) - last_lt_index) <= 128:
                            to_print = self.stream_buffer[:last_lt_index]
                            self.stream_buffer = self.stream_buffer[last_lt_index:]
                        else:
                            to_print = self.stream_buffer[:-128]
                            self.stream_buffer = self.stream_buffer[-128:]
                        self.append_text(to_print, "assistant")
                elif msg_type == "finish":
                    if not self.hide_streaming and self.stream_buffer:
                        visible_tail = strip_state_block(self.stream_buffer)
                        if visible_tail:
                            self.append_text(visible_tail, "assistant")

                    full_response = data
                    try:
                        if self.is_first_response:
                            inv_names = [str(item) for item in self.player_data.inventory]
                            default_starter = []
                            if set(inv_names) == set(default_starter):
                                self.player_data.inventory.clear()
                            self.is_first_response = False

                        before = self._snapshot_for_updates()
                        AICommandExecutor.execute(full_response, self)
                        after = self._snapshot_for_updates()
                        self._apply_update_indicators(before, after)
                        self.update_ui_display()
                    except Exception as e:
                        # Keep UI responsive even if parsing fails
                        self.append_text(f"\n[系统] 指令执行失败: {e}", "system")

                    self.history.append(
                        {"role": "assistant", "content": full_response, "tag": "chat", "summarized": False}
                    )
                    # 异步触发摘要（避免阻塞UI）——在每条消息之后尝试压缩旧历史
                    try:
                        threading.Thread(
                            target=lambda: summarize_old_history(self.history, self.client, game=self, on_status=None),
                            daemon=True,
                        ).start()
                    except Exception:
                        pass
                    self.restore_history_display()
                    self.enable_input()

                    self.save_and_quit(quit_app=False)
                    self.is_generating = False
                    self.hide_streaming = False
                    self.stream_buffer = ""
                elif msg_type == "error":
                    QMessageBox.critical(self, "错误", f"连接中断: {data}")
                    self.is_generating = False
                    self.enable_input()
        except queue.Empty:
            pass

    def trigger_ai_response(self):
        if self.is_generating:
            return
        if not getattr(self, 'ai_client_ready', False):
            self.append_text("AI is still initializing, please wait a moment.", "system")
            return
        self.is_generating = True
        self.disable_input()

        self.hide_streaming = False
        self.stream_buffer = ""

        # Reset last assistant bubble to ensure new response creates a new bubble
        self.chat_component.last_assistant_bubble = None

        threading.Thread(target=self.run_ai_thread, daemon=True).start()
    def run_ai_thread(self):
        def on_token(token):
            self.msg_queue.put(("token", token))

        def on_status(msg):
            self.msg_queue.put(("ai_status", msg))

        def on_history_optimized(hist):
            self.msg_queue.put(("debug_history", hist))

        temp_history = prepare_history_for_request(
            self.history,
            ai_client=self.client,
            game=self,
            on_status=on_status,
            state_append=None,
        )
        on_history_optimized(temp_history)
        temp_history.append({
            "role": "user",
            "content": f"{self.get_current_state_msg()}",
        })
        full_response = self.client.chat(
            temp_history,
            on_token=on_token,
            on_status=on_status,
            game=self,
        )
        self.msg_queue.put(("finish", full_response))
    def send_player_action(self, action_text):
        if not action_text.strip():
            return
        if self.is_generating:
            return
        self.append_text(action_text, "user")
        self.history.append(
            {"role": "user", "content": action_text, "tag": "chat", "summarized": False}
        )
        self.trigger_ai_response()
