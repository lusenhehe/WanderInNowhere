import re
from dataclasses import dataclass
from typing import Iterable, List, Optional
_START_TAGS: List[str] = ["<think>", "<analysis>", "<thinking>"]
_END_TAGS: List[str] = ["</think>", "</analysis>", "</thinking>"]
def sanitize_ai_text(text: str) -> str:
    """
    移除 AI 输出中的思考块（<think>...</think> 等）。
    返回清理后的文本。
    """
    if not text:
        return ""
    cleaned = text
    # 首先移除完整块
    for start, end in (("think", "think"), ("analysis", "analysis"), ("thinking", "thinking")):
        cleaned = re.sub(
            rf"<\s*{start}\s*>.*?<\s*/\s*{end}\s*>",
            "",
            cleaned,
            flags=re.IGNORECASE | re.DOTALL,
        )
    # 移除可能剩余的任何杂散标签
    cleaned = re.sub(r"<\s*/?\s*(think|analysis|thinking)\s*>", "", cleaned, flags=re.IGNORECASE)
    return cleaned.lstrip("\n\r ")
@dataclass
class ThinkBlockStripper:
    """流式文本处理中移除思考块的辅助类。"""
    inside: bool = False    # 是否在思考块内
    pending: str = ""       # 待处理的文本块尾部缓冲
    def _max_tag_len(self) -> int:
        """
        _max_tag_len 的 作用是计算开始标签和结束标签中最长的标签长度。
        这对于处理跨块分割的标签非常重要，因为在流式文本处理中，标签可能会被拆分到不同的块中。
        通过知道最长标签的长度，类可以在处理文本块时保留足够的尾部字符，以确保即使标签被拆分，也能正确识别它们。
        """
        return max(len(t) for t in (_START_TAGS + _END_TAGS))
    def feed(self, chunk: str) -> str:
        """处理一个新的文本块，返回可见文本。"""
        if not chunk:
            return ""
        data = self.pending + chunk
        self.pending = ""

        out_parts: List[str] = []
        max_tail = self._max_tag_len() - 1

        while data:
            lower = data.lower()

            if self.inside:
                end_pos, end_tag = _find_earliest(lower, _END_TAGS)
                if end_pos is None:
                    # 保留一个小尾巴，以防结束标签跨越块分割
                    if len(data) > max_tail:
                        self.pending = data[-max_tail:]
                    else:
                        self.pending = data
                    return ""  # 仍在内部；没有可见内容

                # 删除直到结束标签的所有内容
                data = data[end_pos + len(end_tag) :]
                self.inside = False
                continue

            start_pos, start_tag = _find_earliest(lower, _START_TAGS)
            if start_pos is None:
                if len(data) > max_tail:
                    out_parts.append(data[:-max_tail])
                    self.pending = data[-max_tail:]
                else:
                    self.pending = data
                break

            # 在标签前发出可见文本
            if start_pos > 0:
                out_parts.append(data[:start_pos])

            # 进入思考模式并跳过开始标签
            data = data[start_pos + len(start_tag) :]
            self.inside = True

        return "".join(out_parts)

    def flush(self) -> str:
        """刷新流结束后任何剩余的缓冲文本。"""
        if self.inside:
            # 如果模型从未关闭标签，则删除剩余内容
            self.pending = ""
            return ""
        tail = self.pending
        self.pending = ""
        return tail
def _find_earliest(haystack_lower: str, needles: Iterable[str]) -> tuple[Optional[int], Optional[str]]:
    """在 
    haystack_lower 中查找 needles 中的最早出现位置（不区分大小写）。
    返回 (位置, 标签)；如果未找到，则返回 (None, None)。
    e.g. _find_earliest("hello <think> world", ["<think>", "<analysis>"]) 
         -> (6, "<think>")
    """
    best_pos: Optional[int] = None
    best_tag: Optional[str] = None

    for tag in needles:
        pos = haystack_lower.find(tag)
        if pos == -1:
            continue
        if best_pos is None or pos < best_pos:
            best_pos = pos
            best_tag = tag

    return best_pos, best_tag