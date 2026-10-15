"""
调试相关常量
定义用于调试编辑对话框的字段配置
"""
DEBUG_FIELDS = {
    "item": [
        {"label": "物品名称", "key": "name", "default": "石头"},
        {"label": "物品描述", "key": "desc", "type": "text", "default": "[Debug]会唱歌和发光", "height": 5}
    ],
    "skill": [
        {"label": "技能名称", "key": "name", "default": ""},
        {"label": "元素类型", "key": "element", "default": "无"},
        {"label": "消耗", "key": "cost", "default": "0"},
        {"label": "浓度要求", "key": "density", "default": "0%"},
        {"label": "稀有度", "key": "rarity", "type": "combo", "values": ["普通", "稀有", "传奇", "水晶"], "default": "普通"},
        {"label": "前摇(s)", "key": "preacttime", "default": "1.0"},
        {"label": "后摇(s)", "key": "finishtime", "default": "1.0"},
        {"label": "技能描述", "key": "desc", "type": "text", "default": "暂无描述", "height": 5},
    ],
    "quest": [
        {"label": "任务ID", "key": "qid", "default": ""},
        {"label": "任务标题", "key": "title", "default": ""},
        {"label": "任务描述", "key": "desc", "type": "text", "default": "", "height": 5}
    ],
    "entity": [
        {"label": "实体名称", "key": "name", "default": "孙明昊"},
        {"label": "态度", "key": "attitude", "type": "combo", "values": ["Enemy", "Neutral", "Friendly"], "default": "Friendly"},
        {"label": "描述", "key": "desc", "type": "text", "default": "工作室宠物，kawayi", "height": 2},
        {"label": "位置", "key": "location", "default": "现实-办公室-工作区-桌子地下"},
        {"label": "装备", "key": "equipment", "type": "text", "default": "小头盔"},
    ]
}
# 调试模式相关常量
DEBUG_MODE_ENABLED = False
DEBUG_LOG_LEVEL = "DEBUG"
DEBUG_UI_UPDATE_INTERVAL = 100  # 毫秒
# 调试UI相关常量
DEBUG_PANEL_WIDTH = 300
DEBUG_PANEL_HEIGHT = 400
DEBUG_FONT_SIZE = 10