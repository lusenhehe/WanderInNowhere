import os

# AI 配置
MAX_HISTORY         = 100
RECENT_HISTORY_KEEP = 100
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_TOKENS  = 4096

DEFAULT_API_URL = os.environ.get('SUANLI_API_URL', 'https://api.suanli.cn/v1/chat/completions')
DEFAULT_API_KEY = os.environ.get('SUANLI_API_KEY', '')
DEFAULT_MODEL = os.environ.get('DEFAULT_MODEL', 'glm-4.7-flash')
DEFAULT_MODELS = [
    "glm-4.7",
    "glm-4.6",
    'glm-4.5',
    'glm-4.7-flash',
]
# 游戏机制
EQUIPMENT_SLOTS = {
    "head": "头部",
    "body": "身体",
    "legs": "腿部",
    "weapon": "武器",
    "accessory": "饰品"
}
GAME_SCREEN_STATUS_ITEMS = [("race", "[种族]"),("hp", "[生命]"), ("magic", "[魔力]"), ("magic_density", "[浓度]"),("hunger", "[饥饿]"), ("action", "[状态]")]
GAME_SCREEN_ENTITY_COLUMNS = ["名字", "好感度", "身上装备", "信息"]
MAIN_LOCATIONS = ["北境", "南疆", "废都", "浮空城"]
GAME_TITLE = "Wander in Nowhere"
# 历史优化
MAX_HISTORY_TOKENS = 32000
HISTORY_MSG_THRESHOLD = 20
HISTORY_MSG_KEEP_RECENT = 10 
# 每次摘要批次大小（当未摘要消息数达到该值时，摘要最老的该批消息）
HISTORY_SUMMARY_BATCH = 10
