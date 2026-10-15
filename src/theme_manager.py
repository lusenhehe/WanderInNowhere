import json
import os
import weakref
from src.Constants.config import load_config, save_config
from src.Constants.colors import get_theme_defaults
from src.paths import assets_path
from src.utils.logger import logger


class _ListenerRef:
    """弱引用包装器，用于存储回调函数。"""
    def __init__(self, callback):
        self._key = callback
        if hasattr(callback, "__self__") and getattr(callback, "__self__") is not None:
            self._ref = weakref.WeakMethod(callback)
        else:
            self._ref = weakref.ref(callback)

    def get(self):
        return self._ref()

    def matches(self, callback) -> bool:
        return self._key == callback
def _normalize_color_key(key: str) -> str:
    """
    _normalize_color_key  : 规范化颜色键名，确保其符合 COLOR_* 格式。
    :param key: 颜色键名
    :type key: str
    :return: 规范化后的颜色键名
    :rtype: str
    e.g. "backgroundColor" -> "COLOR_BACKGROUND_COLOR"
    """
    if not key:
        return key
    if key.startswith("COLOR_"):
        return key
    cleaned = []
    for ch in key:
        if ch.isalnum():
            cleaned.append(ch.upper())
        else:
            cleaned.append("_")
    normalized = "".join(cleaned)
    while "__" in normalized:
        normalized = normalized.replace("__", "_")
    return f"COLOR_{normalized.strip('_')}"
def _normalize_scope(scope: str | None) -> str | None:
    """
    _normalize_scope : 规范化主题作用域名称，去除 Qt 后缀并转换为小写。
    
    :param scope: 主题作用域名称
    :type scope: str | None
    :return: 规范化后的主题作用域名称
    :rtype: str | None


    e.g. "MainMenuQt" -> "mainmenu"
    """
    if not scope:
        return None
    s = scope.strip()
    if s.endswith("Qt"):
        s = s[:-2]
    return s.lower()
class ThemeColors:
    """主题颜色容器类，动态设置颜色属性。"""
    def __init__(self, colors_dict, *, defaults: dict):
        for key, val in defaults.items():
            setattr(self, key, colors_dict.get(key, val))
        for key, val in colors_dict.items():
            setattr(self, key, val)
class ThemeManager:
    """主题管理器单例类，负责加载和切换主题。"""
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ThemeManager, cls).__new__(cls)
            cls._instance._init_theme()
        return cls._instance
    def _load_theme_data(self, theme_name):
        """
        _load_theme_data: 加载指定主题的 JSON 数据。
        失败时回退到默认主题 "darkly"。
        :param self: 说明
        :param theme_name: 说明
        """
        try:
            theme_path = assets_path('themes', f'{theme_name}.json')
            if os.path.exists(theme_path):
                with open(theme_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning("主题加载错误 %s: %s", theme_name, e)
        if theme_name != "darkly":
             return self._load_theme_data("darkly")
        return {}

    def _split_theme_sections(self, theme_data: dict) -> tuple[dict, dict[str, dict]]:
        """
        _split_theme_sections : 将主题数据拆分为基础颜色和平面化的页面覆盖部分。
        失败时回退到默认主题 "darkly"。
        
        :param self: 说明
        :param theme_data: 主题数据
        :type theme_data: dict
        :return: 基础颜色字典和平面化的页面覆盖字典
        :rtype: tuple[dict, dict[str, dict]]
        """
        tm = theme_data.get("thememanager")
        if not isinstance(tm, dict):
            base_flat = {k: v for k, v in theme_data.items() if not isinstance(v, dict)}
            return base_flat, {}
        base_src = tm.get("base", {})
        base_flat = {}
        if isinstance(base_src, dict):
            for k, v in base_src.items():
                if isinstance(v, dict):
                    continue
                base_flat[_normalize_color_key(k)] = v
        sections: dict[str, dict] = {}
        for section_name, section_dict in tm.items():
            if section_name == "base":
                continue
            if not isinstance(section_dict, dict):
                continue
            key = _normalize_scope(section_name) or section_name
            overrides: dict[str, str] = {}
            for k, v in section_dict.items():
                if isinstance(v, dict):
                    continue
                overrides[_normalize_color_key(k)] = v
            sections[key] = overrides
        return base_flat, sections

    def _init_theme(self):
        cfg                      = load_config()
        self.current_theme_name  = cfg.get("theme", "darkly")
        theme_data               = self._load_theme_data(self.current_theme_name)
        base_flat, sections      = self._split_theme_sections(theme_data)
        self._theme_sections     = sections
        self.currentTheme        = ThemeColors(base_flat, defaults=get_theme_defaults(self.current_theme_name))
        self.FONT_FAMILY         = "微软雅黑"
        self._listeners: list[_ListenerRef] = []
    def add_change_listener(self, callback):
        """注册一个回调函数，当主题更改时调用。"""
        if callable(callback):
            for ref in list(self._listeners):
                cb = ref.get()
                if cb is None:
                    self._listeners.remove(ref)
                    continue
                if ref.matches(callback):
                    return
            self._listeners.append(_ListenerRef(callback))

    def remove_change_listener(self, callback):
        removed = False
        for ref in list(self._listeners):
            cb = ref.get()
            if cb is None:
                self._listeners.remove(ref)
                removed = True
                continue
            if ref.matches(callback):
                self._listeners.remove(ref)
                removed = True
        if not removed:
            return

    def set_font_family(self, family):
        self.FONT_FAMILY = family
    
    def set_theme(self, theme_name):
        theme_data = self._load_theme_data(theme_name)
        if theme_data:
            self.current_theme_name = theme_name
            base_flat, sections = self._split_theme_sections(theme_data)
            self._theme_sections = sections
            from src.Constants.colors import get_theme_defaults
            self.currentTheme = ThemeColors(base_flat, defaults=get_theme_defaults(self.current_theme_name))
            
            cfg = load_config()
            cfg['theme'] = theme_name
            save_config(cfg)

            for ref in list(self._listeners):
                cb = ref.get()
                if cb is None:
                    self._listeners.remove(ref)
                    continue
                try:
                    cb()
                except RuntimeError:
                    # 当Qt对象已被删除时常见
                    try:
                        self._listeners.remove(ref)
                    except ValueError as ve:
                        logger.warning(f"主题更改监听器删除失败{ve}", exc_info=True)
                        pass
                except Exception as e:
                    logger.error(f"主题更改监听器调用失败: {e}", exc_info=True)

    def get_qss_vars(self, *, scope: str | None = None) -> dict[str, str]:
        """给QSS模板用的变量。
        - scope: BaseUI子类名（如 MainMenuQt / SaveSelectQt），会映射到 section 覆盖。
        """
        theme = self.currentTheme
        vars: dict[str, str] = {}
        # 先放入所有 COLOR_* 属性
        for k, v in getattr(theme, "__dict__", {}).items():
            if isinstance(k, str) and k.startswith("COLOR_"):
                vars[k] = str(v)

        # 再叠加按页面覆盖（如果主题json里提供了 thememanager.<page>）
        key = _normalize_scope(scope)
        if key and hasattr(self, "_theme_sections"):
            overrides = getattr(self, "_theme_sections", {}).get(key, {})
            for k, v in overrides.items():
                vars[k] = str(v)

        return vars
theme_manager = ThemeManager()
