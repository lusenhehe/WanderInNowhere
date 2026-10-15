from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any, Dict
class BaseDataModel:
    """极简数据模型基类。
    该项目的多个 Data 类并不强依赖复杂 ORM 功能；这里提供最小的
    `to_dict()` / `from_dict()` 以恢复导入与运行稳定性。
    """

    def to_dict(self) -> Dict[str, Any]:
        if is_dataclass(self):
            return asdict(self)
        # 默认：按实例字段导出
        return dict(getattr(self, "__dict__", {}) or {})

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        if not isinstance(data, dict):
            raise TypeError(f"{cls.__name__}.from_dict expects dict")
        # 默认：把 dict 作为 kwargs 传给构造函数
        return cls(**data)