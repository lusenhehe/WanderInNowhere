from __future__ import annotations
from typing import Any, Callable, Dict, List, Optional
from src.utils.history_optimizer import summarize_old_history, trim_history_by_tokens
from src.AI.parser import strip_state_block
def optimize_history_for_ai(history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """优化历史记录以供 AI 请求使用。
    - 从助手消息中移除 <STATE_START>...<STATE_END> 块。
    - 删除空消息。
    - 保留原始字典字段（复制消息）。
    """
    optimized: List[Dict[str, Any]] = []
    for msg in history or []:
        if not isinstance(msg, dict):
            continue

        new_msg = msg.copy()
        if new_msg.get("role") == "assistant":
            new_msg["content"] = strip_state_block(str(new_msg.get("content", "")))

        if not str(new_msg.get("content", "")).strip():
            continue

        optimized.append(new_msg)

    return optimized
def prepare_history_for_request(
    history: List[Dict[str, Any]],
    *,
    ai_client: Optional[Any] = None,
    game: Optional[Any] = None,
    on_status: Optional[Callable[[str], None]] = None,
    state_append: Optional[str] = None,
    max_history_tokens: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """为 AI 请求准备聊天历史记录。

    管道（单一真相来源）：
    1) 移除助手 <STATE_START>...<STATE_END> 块和空消息。
    2) 可选地将当前状态追加到最新的用户消息。
    3) 可选地总结旧历史记录（使用 game.summarized_line + game.summaries）。
    4) 按令牌数量修剪到安全限制。

    返回一个新列表；不改变原始历史记录。
    """

    prepared = optimize_history_for_ai(history)

    if state_append and prepared and prepared[-1].get("role") == "user":
        last = prepared[-1].copy()
        content = str(last.get("content", ""))
        if content:
            content = content.rstrip() + "\n" + str(state_append)
        else:
            content = str(state_append)
        last["content"] = content
        prepared = prepared[:-1] + [last]

    if ai_client is not None and game is not None: 
        prepared = summarize_old_history(prepared, ai_client, game=game, on_status=on_status)
    prepared = trim_history_by_tokens(prepared)
    return prepared
