import tiktoken
from functools import lru_cache
from typing import List, Dict, Optional, Any
from src.Constants.game_constants import (
    MAX_HISTORY_TOKENS,
    HISTORY_MSG_THRESHOLD,
    HISTORY_MSG_KEEP_RECENT,
    HISTORY_SUMMARY_BATCH,
)
from src.AI.prompts import SUMMARY_PROMPT_TEMPLATE
from src.utils.logger import logger
# 初始化tokenizer（缓存起来，避免重复创建）
@lru_cache(maxsize=1)
def get_tokenizer():
    try:
        return tiktoken.get_encoding("cl100k_base")
    except Exception as e:
        logger.error(f"失败加载tiktoken编码器: {e}")
        return None
# 计算单条消息的Token数
def count_tokens(text: str, tokenizer=None) -> int:
    if not text:
        return 0
    try:
        tokenizer = tokenizer or get_tokenizer()
        if tokenizer:
            return len(tokenizer.encode(text))
    except Exception:
        logger.exception("计算Token数失败，使用字符数代替")
    return len(text)
# 按Token数裁剪历史（基础版）
def trim_history_by_tokens(history: List[Dict[str, str]],max_tokens: int = MAX_HISTORY_TOKENS) -> List[Dict[str, str]]:
    """
    裁剪历史消息，使总Token数不超过max_tokens（保留最新消息）
    :param history: 历史消息列表，格式如[{"role": "user/assistant", "content": "xxx"}, ...]
    :param max_tokens: 最大Token数
    :return: 裁剪后的历史列表

    逻辑：
    - 总是保留第一条 System Prompt（如果有）。
    - 从后往前遍历消息，累计Token数，直到达到max_tokens为止。
    - 如果单条消息过长，截断该消息内容以适应Token限制。
    """
    tokenizer = get_tokenizer()
    total_tokens = 0

    # 总是保留第一条 System Prompt (如果有)
    system_prompt = None
    if history and history[0].get("role") == "system":
        system_prompt = history[0]
        total_tokens += count_tokens(system_prompt["content"], tokenizer)
        # 处理剩余历史
        msgs_to_process = history[1:]
    else:
        msgs_to_process = history

    # 从后往前遍历，保留最新的消息
    temp_history = []
    for msg in reversed(msgs_to_process):
        content = msg.get("content", "")
        msg_tokens = count_tokens(content, tokenizer)

        if total_tokens + msg_tokens > max_tokens:
            # 若当前消息加入后超限，且是第一条（超长单条），则截断该消息
            if not temp_history:
                # 截断消息内容（取最后max_tokens个Token对应的文本）
                # 注意：这里简单截断可能导致乱码，tiktoken decode通常能处理
                encoded = tokenizer.encode(content)
                # 留出一点空间给 system prompt
                available = max_tokens - total_tokens
                if available > 0:
                    truncated_encoded = encoded[-available:]
                    truncated_text = tokenizer.decode(truncated_encoded)
                    temp_history.insert(0, {"role": msg["role"], "content": truncated_text, "tag": msg.get("tag")})
            break
        total_tokens += msg_tokens
        temp_history.insert(0, msg)

    if system_prompt:
        return [system_prompt] + temp_history
    return temp_history

# 历史消息摘要化（高阶版）
def summarize_old_history(history: List[Dict[str, str]],ai_client: Any,game: Optional[Any] = None,on_status: Optional[Any] = None) -> List[Dict[str, str]]:
    """
    总结旧的历史消息以节省Token。
    逻辑：
    - 提取 System Prompt（如果有）。
    - 确定未总结的消息范围（基于 game.summarized_line 指针）。
    - 如果未总结的消息超过 HISTORY_MSG_THRESHOLD，则总结 (len - KEEP_RECENT) 条消息。
    - 构建返回给 AI 的 History：
         [System Prompt] + [All Summaries] + [Unsummarized History]
    :param history: 原始历史消息列表
    :param ai_client: AI 客户端实例
    :param game: GameScreen 实例
    :param on_status: 状态回调函数
    """
    # 1. 提取 System Prompt
    system_prompt = None
    if history and history[0].get("role") == "system":
        system_prompt = history[0]
    # 如果没有 game 对象，或者 history 太短，直接返回
    if not game or not hasattr(game, 'summarized_line'):
        return history
    # 2. 确定未总结的消息范围
    start_index = int(getattr(game, 'summarized_line', 0) or 0)
    if start_index < 0:
        start_index = 0
    if start_index > len(history):
        start_index = len(history)
    game.summarized_line = start_index
    # 获取未总结的消息
    unsummarized_msgs = history[start_index:]
    on_status and on_status(f"未压缩的历史消息数: {len(unsummarized_msgs)}")
    # 3. 检查是否需要总结
    # 策略：保留最近的 HISTORY_MSG_KEEP_RECENT 条消息不总结
    # 如果未总结的消息超过 HISTORY_MSG_THRESHOLD 条，则总结 (len - KEEP_RECENT) 条

    # 当未摘要消息数量达到批次阈值时，摘要最老的一批消息（可配置）
    if len(unsummarized_msgs) >= HISTORY_SUMMARY_BATCH:
        for i in range(len(unsummarized_msgs) // HISTORY_SUMMARY_BATCH):
            num_to_summarize = HISTORY_SUMMARY_BATCH
            msgs_to_summarize = unsummarized_msgs[i * HISTORY_SUMMARY_BATCH:(i + 1) * HISTORY_SUMMARY_BATCH]
            # 过滤出 chat 消息进行总结
            chat_msgs_to_summarize = [m for m in msgs_to_summarize if m.get("tag", "chat") == "chat"]

            if chat_msgs_to_summarize:
                # 生成摘要
                lines_text = ""
                for msg in chat_msgs_to_summarize:
                    role_name = "玩家" if msg['role'] == "user" else "DM"
                    content = msg['content'].replace("【摘要】", "")
                    lines_text += f"[{role_name}]: {content}\n"
                # 使用配置的模板
                summary_prompt = SUMMARY_PROMPT_TEMPLATE.format(lines_text=lines_text)
                if on_status:
                    on_status(f"正在压缩历史记录...")
                try:
                    summary_req = [{"role": "user", "content": summary_prompt}]
                    summary_res = ai_client.chat(summary_req,temperature=0.3, max_tokens=1000, stream=False)
                    summary_text = summary_res.strip()
                    # 保存到 game.summaries
                    if hasattr(game, 'summaries'):
                        game.summaries.append({"content": summary_text, "level": 1})

                    # 更新 summarized_line, 推进指针
                    game.summarized_line += num_to_summarize
                except Exception as e:
                    logger.warning("摘要生成失败: %s", e)
                    # 如果失败，不更新 summarized_line，下次重试
    else:
        on_status and on_status("历史消息量未达压缩阈值，无需压缩。")

    # 4. 构建返回给 AI 的 History
    # [System Prompt] + [All Summaries] + [Unsummarized History]
    new_history = []
    if system_prompt:
        new_history.append(system_prompt)

    # 添加所有摘要
    if hasattr(game, 'summaries'):
        for s_item in game.summaries:
            if isinstance(s_item, str):
                content = s_item
            else:
                content = s_item.get("content", "")

            new_history.append({
                "role": "system",
                "content": f"【前情提要】: {content}",
                "tag": "summary"
            })

    # 添加剩余的未总结消息
    remaining_msgs = history[game.summarized_line:]
    new_history.extend(remaining_msgs)
    return new_history
