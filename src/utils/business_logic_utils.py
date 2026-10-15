from __future__ import annotations
import re
from typing import Any, Iterable, Tuple
class BusinessLogicUtils:
    @staticmethod
    def parse_resource_string(text: Any) -> Tuple[int, int]:
        """解析资源字符串。
        支持示例：
        - "100/120" -> (100, 120)
        - "40%" -> (40, 100)
        - "10MP" / "10" -> (10, 0)
        - None/空 -> (0, 0)
        """

        if text is None:
            return (0, 0)

        s = str(text).strip()
        if not s:
            return (0, 0)

        if "/" in s:
            left, right = s.split("/", 1)
            a = BusinessLogicUtils._first_int(left)
            b = BusinessLogicUtils._first_int(right)
            return (a, b)

        if s.endswith("%"):
            a = BusinessLogicUtils._first_int(s)
            return (a, 100)

        return (BusinessLogicUtils._first_int(s), 0)

    @staticmethod
    def format_resource_string(cur: int, max_val: int) -> str:
        try:
            return f"{int(cur)}/{int(max_val)}"
        except Exception:
            return "0/0"

    @staticmethod
    def find_item_by_name(inventory: Iterable[Any], item_name: str):
        name = str(item_name or "").strip()
        if not name:
            return None

        for item in inventory or []:
            if item is None:
                continue
            if hasattr(item, "name") and str(getattr(item, "name", "")) == name:
                return item
            if isinstance(item, dict) and str(item.get("name", "")) == name:
                return item
            if isinstance(item, str) and item == name:
                return item
        return None

    @staticmethod
    def _first_int(s: str) -> int:
        m = re.search(r"-?\d+", s or "")
        if not m:
            return 0
        try:
            return int(m.group(0))
        except Exception:
            return 0
