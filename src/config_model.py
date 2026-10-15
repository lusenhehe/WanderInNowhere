from dataclasses import dataclass, field
from typing import Any, Dict
@dataclass
class AppConfig:
    """
    AppConfig: 应用程序配置的数据类。
    包含应用程序的各种设置，如调试模式、主题、AI API 配置等。
    还支持额外的未预定义字段，通过 extras 字典存储。

    属性:
    - debug (bool): 是否启用调试模式。
    - theme (str): 应用程序的主题名称。
    - api_url (str): AI 服务的 API URL。
    - api_key (str): AI 服务的 API Key。
    - model (str): 使用的 AI 模型名称。
    - temperature (float): 生成文本的温度参数。
    - max_tokens (int): 最大生成 token 数。
    - max_history (int): 聊天历史的最大条数。
    - font (str): 应用程序使用的字体名称。
    - ssl_verify (bool): 是否启用 SSL 证书验证。
    - extras (Dict[str, Any]): 其他未预定义的配置字段。
    """
    debug: bool = False
    theme: str = "darkly"
    api_url: str = ""
    api_key: str = ""
    model: str = ""
    temperature: float = 0.7
    max_tokens: int = 256
    max_history: int = 100
    font: str = "Chinese.ttf"
    ssl_verify: bool = False
    extras: Dict[str, Any] = field(default_factory=dict)
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AppConfig":
        known_keys = {"debug","theme","api_url","api_key","model","temperature","max_tokens","max_history","font","ssl_verify",}
        extras = {k: v for k, v in data.items() if k not in known_keys}
        return cls(debug=bool(data.get("debug", False)),theme=str(data.get("theme", "darkly") or "darkly"),api_url=str(data.get("api_url", "") or ""),api_key=str(data.get("api_key", "") or ""),model=str(data.get("model", "") or ""),temperature=float(data.get("temperature", 0.7) or 0.7),max_tokens=int(data.get("max_tokens", 256) or 256),max_history=int(data.get("max_history", 100) or 100),font=str(data.get("font", "Chinese.ttf") or "Chinese.ttf"),ssl_verify=bool(data.get("ssl_verify", False)),extras=extras,)
    def to_dict(self) -> Dict[str, Any]:
        out: Dict[str, Any] = dict(self.extras)
        out.update({"debug": bool(self.debug),"theme": str(self.theme),"api_url": str(self.api_url),"api_key": str(self.api_key),"model": str(self.model),"temperature": float(self.temperature),"max_tokens": int(self.max_tokens),"max_history": int(self.max_history),"font": str(self.font),"ssl_verify": bool(self.ssl_verify),})
        return out