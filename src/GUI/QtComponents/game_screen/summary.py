import threading
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtWidgets import QWidget,QVBoxLayout,QHBoxLayout,QLabel,QScrollArea,QMessageBox
from src.GUI.CustomWidgets.CardWidgets import SummaryCardQt
from src.GUI.CustomWidgets.custom_button import CustomButton
from src.theme_manager import theme_manager
from src.utils.logger import logger

class SummaryComponent(QWidget):
    compression_finished = pyqtSignal(list, dict)
    compression_failed = pyqtSignal(str)

    def __init__(self,*,ai_client=None,msg_queue=None,on_save=None,on_summaries_changed=None,parent: QWidget | None = None,):
        super().__init__(parent)
        self._ai_client = ai_client
        self._msg_queue = msg_queue
        self._on_save = on_save
        self._on_summaries_changed = on_summaries_changed

        self._summaries: list = []
        self.selected_indices: set[int] = set()

        self.compression_finished.connect(self._apply_compression_result)
        self.compression_failed.connect(self._on_compression_failed)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        toolbar = QHBoxLayout()
        self.compress_btn = CustomButton("压缩选中摘要 (0)", variant="secondary")
        self.compress_btn.setEnabled(False)
        self.compress_btn.clicked.connect(lambda: self.compress_selected_summaries(_ai_client=self._ai_client))
        toolbar.addWidget(self.compress_btn)

        hint = QLabel("提示：可压缩10个同级摘要")
        hint.setStyleSheet(f"color: {theme_manager.currentTheme.COLOR_TEXT_SECONDARY};")
        toolbar.addWidget(hint)
        toolbar.addStretch(1)
        layout.addLayout(toolbar)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        layout.addWidget(self.scroll, 1)

        self._scroll_inner = QWidget()
        self._scroll_layout = QVBoxLayout(self._scroll_inner)
        self._scroll_layout.setContentsMargins(0, 0, 0, 0)
        self._scroll_layout.setSpacing(10)
        self._scroll_layout.addStretch(1)
        self.scroll.setWidget(self._scroll_inner)
    
    def _on_compression_failed(self, err: str):
        if self._msg_queue is not None:
            self._msg_queue.put(("error", f"压缩失败: {err}"))
        self.update_compress_button_state()


    def _apply_compression_result(self, indices: list[int], new_summary: dict):
        for idx in sorted(indices, reverse=True):
            try:
                del self._summaries[idx]
            except Exception:
                pass
        insert_pos = min(indices) if indices else len(self._summaries)
        self._summaries.insert(insert_pos, new_summary)

        self.selected_indices = set()
        self.update_display(self._summaries)
        QMessageBox.information(
            self,
            "压缩完成",
            f"已成功将{len(indices)}条摘要压缩为1条Lv.{new_summary['level']}摘要。",
        )

        if callable(self._on_summaries_changed):
            self._on_summaries_changed()
        if callable(self._on_save):
            self._on_save(False)
    def update_display(self, summaries: list):
        self._summaries = summaries if summaries is not None else []

        while self._scroll_layout.count() > 1:
            item = self._scroll_layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()

        if not self._summaries:
            empty = QLabel("暂无历史摘要...")
            empty.setStyleSheet(f"color: {theme_manager.currentTheme.COLOR_TEXT_SECONDARY}; font-style: italic;")
            empty.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            self._scroll_layout.insertWidget(0, empty)
            self.selected_indices = set()
            self.update_compress_button_state()
            return

        # 分批创建 SummaryCard，避免一次性阻塞
        self._summary_iter = ((i, summary) for i, summary in enumerate(self._summaries))
        self._populate_summary_batch()

    def _populate_summary_batch(self):
        BATCH = 6
        count = 0
        while count < BATCH:
            try:
                i, summary = next(self._summary_iter)
            except StopIteration:
                if hasattr(self, '_summary_iter'):
                    del self._summary_iter
                logger.info(f"Summaries populated: {i+1 if 'i' in locals() else len(self._summaries)} items")
                self.update_compress_button_state()
                return
            if isinstance(summary, str):
                content = summary
                level = 1
            else:
                content = str(summary.get("content", "")).replace("【前情提要】:", "").replace("【前情提要】: ", "")
                level = int(summary.get("level", 1) or 1)
            cardw = SummaryCardQt(
                index=i,
                content=content,
                level=level,
                selected=(i in self.selected_indices),
                on_toggle=self._toggle_selected,
            )
            self._scroll_layout.insertWidget(self._scroll_layout.count() - 1, cardw)
            count += 1
        QTimer.singleShot(10, self._populate_summary_batch)

    def _toggle_selected(self, idx: int, checked: bool):
        if checked:
            self.selected_indices.add(idx)
        else:
            self.selected_indices.discard(idx)
        self.update_compress_button_state()

    def update_compress_button_state(self):
        selected = [i for i in sorted(self.selected_indices) if 0 <= i < len(self._summaries)]
        count = len(selected)
        if count == 0:
            self.compress_btn.setText("压缩选中摘要 (0)")
            self.compress_btn.setEnabled(False)
            return

        levels = []
        for idx in selected:
            s = self._summaries[idx]
            if isinstance(s, str):
                levels.append(1)
            else:
                levels.append(int(s.get("level", 1) or 1))

        first_level = levels[0]
        all_same_level = all(l == first_level for l in levels)
        level_ok = first_level < 3
        count_ok = count  == 10

        text = f"压缩选中摘要 ({count})"
        enabled = True
        if not all_same_level:
            text += " - 等级不一致"
            enabled = False
        elif not level_ok:
            text += " - 已达最高等级"
            enabled = False
        elif not count_ok:
            text += " - 需>10个"
            enabled = False

        self.compress_btn.setText(text)
        self.compress_btn.setEnabled(enabled)

    def compress_selected_summaries(self, _ai_client=None):
        if not self.compress_btn.isEnabled():
            return
        if self._ai_client is None:
            self._ai_client = _ai_client
        indices = sorted([i for i in self.selected_indices if 0 <= i < len(self._summaries)])
        if not indices:
            return

        contents = []
        current_level = 1
        for idx in indices:
            s = self._summaries[idx]
            if isinstance(s, str):
                contents.append(s)
                current_level = 1
            else:
                contents.append(s.get("content", ""))
                current_level = int(s.get("level", 1) or 1)

        target_words = 200 if current_level == 1 else 250
        self.compress_btn.setEnabled(False)
        self.compress_btn.setText("正在压缩...")

        threading.Thread(target=self._run_compression_thread,args=(contents, indices, current_level, target_words),daemon=True,).start()

    def _run_compression_thread(self, contents, indices, current_level, target_words):
        try:
            combined_text = "\n\n".join(contents)
            prompt = (
                f"请将以下{len(contents)}段剧情摘要合并并压缩成一段更宏观的叙述。\n"
                f"保留所有关键的主线剧情、重要转折和角色发展，去除琐碎细节。\n"
                f"目标长度：约{target_words}字。\n\n"
                f"待压缩内容：\n{combined_text}"
            )
            req = [{"role": "user", "content": prompt}]

            def on_status(msg):
                if self._msg_queue is not None:
                    self._msg_queue.put(("ai_status", msg))

            response = self._ai_client.chat(
                req,
                temperature=0.3,
                max_tokens=500,
                on_status=on_status,
            )
            new_summary = {"content": response.strip(), "level": current_level + 1}
            self.compression_finished.emit(list(indices), new_summary)
        except Exception as e:
            self.compression_failed.emit(str(e))
