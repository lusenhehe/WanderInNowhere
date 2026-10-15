SPLASHED_TEXTS = [
    "你知道吗，创作者已经和朋友沉迷于游戏无法自拔了！",
    "欢迎来到乌有乡，一个充满未知与冒险的世界！",
    "你知道吗，双手剑需要中距离挥砍？",
]

CREDITS_DATA = [
    ("备注", "排名分先后(仅限第一排)"),
    ("工作室宠物", "孙明昊, 毛一鸣"),
    ("总策划", "ZCJ"),
    ("首位速通玩家" , "⭐⭐zhtttykq⭐⭐"),
    ("世界观", "ZCJ, STY, SMH"),
    ("核心程序", "LZN"),
    ("主要测试人员", "zhtttykq[首通], 伊之憨包"),
    ("美术资源", "xxx"),
    ("特别鸣谢", "xxx"),
    ("测试团队", "xxxx"),
    ("灵感来源", "xxx"),
    ("致谢", "所有支持我们的玩家"),
]

UI_TEXTS = {
    "game_screen": {
        "tab_adventure": "⚔冒险",
        "tab_entities": "👥 实体",
        "tab_summary": "📝 摘要",
        "tab_status": "⚡状态",
        "tab_inventory": "🎒物品",
        "tab_skills": "✨技能",
        "tab_quests": "📜任务",
    },
    "main_menu": {
        "btn_start_journey": "开始旅程",
        "btn_settings": "系统设置",
        "btn_credits": "制作人员",
        "btn_exit": "退出游戏",
    },
    "settings": {
        "title": "设置",
        "sidebar_appearance": "外观",
        "sidebar_ai": "AI 设置",
        "sidebar_debug": "调试",
        "theme_card_title": "主题设置",
        "theme_label": "主题:",
        "font_card_title": "字体设置",
        "font_label": "字体:",
        "api_card_title": "API 配置",
        "api_url_label": "API URL:",
        "api_key_label": "API Key:",
        "model_card_title": "模型配置",
        "model_label": "模型:",
        "params_card_title": "生成参数",
        "temperature_label": "Temperature:",
        "max_tokens_label": "Max Tokens:",
        "max_history_label": "Max History:",
        "debug_card_title": "调试选项",
        "debug_checkbox": "启用 Debug 模式",
        "debug_info": "启用调试模式将解锁AI设置，并启用详细日志记录。\n需要密码验证。",
        "btn_apply": "应用",
        "btn_save_back": "保存并返回",
        "btn_cancel": "取消",
        "debug_verification": "Debug 验证",
        "enter_debug_password": "请输入 Debug 密码:",
        "password_incorrect": "密码错误",
        "error": "错误",
    },
    "credits": {
        "credits_title": "制作人员名单",
        "subtitle": "感谢所有为这个世界添砖加瓦的人",
        "development_team": "开发团队",
        "btn_back_to_menu": "返回主菜单",
    },
    "save_select": {
        "title": "选择存档",
        "subtitle": "挑选你的世界，继续旅程。",
        "save_list_title": "存档",
        "empty_hint": "暂无存档\n创建一个新世界，开始故事。",
        "btn_enter_world": "进入世界",
        "btn_create_world": "创建新世界",
        "btn_delete_save": "删除存档",
        "btn_back": "返回",
        "confirm_delete": "确认",
        "delete_save_prompt": "确定要删除存档 '{world_name}' 吗？此操作不可恢复。",
        "warning": "提示",
        "select_save_first": "请先选择一个存档",
    },
    "create_world": {
        "title": "创建新世界",
        "subtitle": "打造你的独特世界：名称、种族与出身将形成开场故事",
        "form_title": "设定",
        "world_name_label": "世界名称:",
        "player_name_label": "角色名称:",
        "race_label": "种族:",
        "magic_label": "魔力浓度:",
        "birthplace_label": "出生地区:",
        "actions_title": "操作",
        "btn_create": "创建世界",
        "btn_cancel": "取消",
        "error": "错误",
        "fill_required_fields": "请填写必填字段（世界名称 & 角色名称）",
    },
}

UI_ICONS = {
    # Main Menu Icons
    "icon_play": "play",
    "icon_settings": "settings",
    "icon_summary": "summary",
    "icon_status": "status",
}

class UIConstants:
    SAVE_CARD_PADX = 4
    SAVE_CARD_PADY = 6
    SAVE_CARD_INNER_PADX = 8
    SAVE_CARD_INNER_PADY = 8
    SAVE_CARD_ACCENT_WIDTH = 6
    SAVE_HEADER_PADY = (20, 10)
    SAVE_HEADER_PADX = 30
    SAVE_LIST_PADX = 60
    SAVE_LIST_PADY = 10
