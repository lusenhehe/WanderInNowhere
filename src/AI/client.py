from zai import ZhipuAiClient
from src.Constants.config import load_config
from src.Constants.game_constants import DEFAULT_MAX_TOKENS, DEFAULT_TEMPERATURE
from src.utils.logger import logger
from src.utils.ai_output_sanitizer import ThinkBlockStripper, sanitize_ai_text
class AIClient:
    """
    AIClient : 与 ZhipuAI 交互的客户端
    负责发送聊天请求并处理响应
    """
    def __init__(self):
        self._history_cache = {}
        self.api_key    : str                = ""                   # ZhipuAI API Key
        self.model      : str                = ""                   # 使用的模型名称
        self.temperature: float              = DEFAULT_TEMPERATURE  # 生成文本的温度参数
        self.max_tokens : int                = DEFAULT_MAX_TOKENS   # 最大生成 token 数
        self.stream     : bool               = True                 # 是否启用流式输出
        self.client     : ZhipuAiClient      = None                 # ZhipuAiClient 实例
        self.stripper   : ThinkBlockStripper = ThinkBlockStripper()  # 思考块移除器
        self._refresh_from_config(load_config())

    def _refresh_from_config(self, cfg: dict) -> None:
        self.api_key     = cfg.get('api_key', '')
        self.model       = cfg.get('model', '')
        self.temperature = cfg.get('temperature', DEFAULT_TEMPERATURE)
        self.stream      = cfg.get('stream', True)
        self.max_tokens  = cfg.get('max_tokens', DEFAULT_MAX_TOKENS)
        self.client      = ZhipuAiClient(api_key=self.api_key)

    def chat(self, history, on_token=None, on_status=None, on_history_optimized=None, game=None,
             temperature=None, max_tokens=None, stream=None):
        """
        发送聊天请求
        :param history: 对话历史列表 [{"role": "user", "content": "..."}, ...]
        :param on_token: 回调函数，用于流式输出 token
        :param temperature: 覆盖默认的 temperature
        :param max_tokens: 覆盖默认的 max_tokens
        :param on_status: 状态回调函数 on_status(msg: str)
        :param on_history_optimized: 历史优化完成回调 on_history_optimized(history: list)
        :param game: GameScreen 实例，用于持久化摘要
        :return: 完整的回复内容
        """
        self._refresh_from_config(load_config())

        # 注意：
        # 历史清洗/摘要/裁剪应在上层管线完成（见 src/AI/history_pipeline.py）。
        # 这里仅负责把已准备好的 history 发给模型并返回结果。
        optimized_history = history
        if on_history_optimized:
            on_history_optimized(optimized_history)
        if on_status:
            on_status("正在生成回复...")
        messages = []
        for msg in optimized_history:
            if "role" in msg and "content" in msg:
                messages.append({"role": msg["role"],"content": msg["content"]})
        model       = self.model
        messages    = messages
        temperature = self.temperature if temperature is None else temperature
        stream      = self.stream      if stream      is None else stream
        max_tokens  = self.max_tokens  if max_tokens  is None else max_tokens
        response = self.client.chat.completions.create(
            model       = model,
            messages    = messages,
            temperature = temperature,
            stream      = stream,
            max_tokens  = max_tokens,
            thinking = False,
        )
        logger.info(f"""AI 响应: model: {model}, temp: {temperature}, max_tokens: {max_tokens},  stream: {stream}""")
        full_content = ""
        max_retries = 5
        for attempt in range(max_retries):
            print(f"Attempt {attempt + 1} to process AI response...")
            try:
                # 处理响应
                if stream:
                    # 流式响应
                    for chunk in response:
                        if hasattr(chunk, 'choices') and chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                            content = chunk.choices[0].delta.content
                            visible = self.stripper.feed(content)
                            if visible:
                                if on_token:
                                    on_token(visible)
                                full_content += visible

                    tail = self.stripper.flush()
                    if tail:
                        if on_token:
                            on_token(tail)
                        full_content += tail
                else:
                    # 非流式响应
                    if hasattr(response, 'choices') and response.choices:
                        print(f"Response choices: {response.choices}")
                        full_content = sanitize_ai_text(response.choices[0].message.content)
                        logger.info(f"Content from choices: '{full_content}'")
                    else:
                        # 如果 response 是可迭代的，尝试从中提取内容
                        for chunk in response:
                            print(f"Processing chunk: {type(chunk)}")
                            if hasattr(chunk, 'choices') and chunk.choices and hasattr(chunk.choices[0], 'message') and chunk.choices[0].message:
                                full_content += sanitize_ai_text(chunk.choices[0].message.content)
                break  # 成功则退出重试
            except Exception as e:
                logger.warning(f"获取 AI 响应失败 (尝试 {attempt + 1}/{max_retries}): {e}")
                print(f"获取 AI 响应失败 (尝试 {attempt + 1}/{max_retries}): {e}")
        full_content = sanitize_ai_text(full_content)
        return full_content

